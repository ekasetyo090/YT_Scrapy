# -*- coding: utf-8 -*-
"""
Created on March 19 18:32:42 2024

@author: eka setyo agung Mahanani
"""

import pandas as pd
import requests as req
import json
import time
import urllib.parse
import re


from datetime import datetime
from typing import Union
from requests.exceptions import ConnectionError, HTTPError
from bs4 import BeautifulSoup

class YtScraper:
    """A class for scraping YouTube channel data (assuming non-commercial use).

    DISCLAIMER: YouTube's Terms of Service (TOS) may restrict scraping.
                 Use this code responsibly and ethically. Consider the YouTube Data API
                 for more reliable and authorized data access.

    Attributes:
        channel_id (str): The ID of the YouTube channel to scrape.
        channel_url (str): The constructed URL for the YouTube channel.
        session (requests.Session): A session object to manage cookies and headers.
    """

    def __init__(self):
        self.BASE_URL = 'https://www.youtube.com/'
        self.session = req.Session()
        self.session_api = req.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-us,en;q=0.5",
            "Sec-Fetch-Mode": "navigate"
        }
        self.session.get('https://www.google.com/')
        self.api_key, self.reff = self.get_api_reff()
        self.session_api.headers = {
            'Accept-Encoding':'gzip, deflate, br, zstd',
            'Accept-Language':'en-US,en;q=0.9',
            'Cache-Control':'no-cache',
            'Dnt':'1',
            'Pragma':'no-cache',
            'Priority':'u=1, i',
            'Referer':f'https://content-youtube.googleapis.com/static/proxy.html?usegapi=1&jsh={self.reff}',
            'Sec-Ch-Ua':'"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'Sec-Ch-Ua-Mobile':'?0',
            'Sec-Ch-Ua-Platform':"Windows",
            'Sec-Fetch-Dest':'empty',
            'Sec-Fetch-Mode':'cors',
            'Sec-Fetch-Site':'same-origin',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'X-Clientdetails':'appVersion=5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F125.0.0.0%20Safari%2F537.36&platform=Win32&userAgent=Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F125.0.0.0%20Safari%2F537.36',
            'X-Goog-Encode-Response-If-Executable':'base64',
            'X-Javascript-User-Agent':'apix/3.0.0 google-api-javascript-client/1.1.0',
            'X-Origin':'https://explorer.apis.google.com',
            'X-Referer':'https://explorer.apis.google.com',
            'X-Requested-With':'XMLHttpRequest'
        }
        
    def get_api_reff(self):
        """Get api key and reff url to make request.

        Raises:
            ConnectionError: If a connection error occurs.
            requests.exceptions.RequestException: If a request fails due to other reasons.

        Returns:
            2 variable string (api_key) and (reff url).
        """
        
        self.session_api.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-us,en;q=0.5",
            "Sec-Fetch-Mode": "navigate"
        }
        self.session_api.get('https://developers.google.com/youtube/v3/docs')
        response = self.session_api.get('https://explorer.apis.google.com/embedded.js')
        api_pattern = re.compile(r'var JF=function\(a\){this.security={.*?};\s*this\.g=a;.*?this\.j=\{[\s\S]*?\}\};')
        match = api_pattern.search(response.text)
        api_pattern = re.compile(r'api_key:\s*\{Jc:\s*"(.*?)"\}')
        match = api_pattern.search(match.group())
        api_key = match.group(1)
        #------------
        self.session_api.headers["Referer"] = 'https://developers.google.com/'
        response = self.session_api.get('https://apis.google.com/js/api.js')
        reff_pattern = re.compile(r'window\.gapi\.load\("",\s*\{([\s\S]*?)\}\);')
        match = reff_pattern.search(response.text)
        reff_pattern = re.compile(r'h:\s*"(m;/_/scs/abc-static/_/js/k=gapi\.lb\.en\.[^"]*)"')
        reff = urllib.parse.quote(reff_pattern.search(match.group(1)).group(1), safe='')
        
        return api_key, reff
        

    def scrape_channel_basic_data(self,channel_id: str):
        """Scrapes data from the YouTube channel using the constructed URL and session with headers.

        Raises:
            ConnectionError: If a connection error occurs.
            requests.exceptions.RequestException: If a request fails due to other reasons.

        Returns:
            dict: A dictionary containing scraped data channel.
        """
        
        self.channel_url = f"{self.BASE_URL}{channel_id}" if channel_id.startswith('@') else f"{self.BASE_URL}channel/{channel_id}"
        
        response = self.make_request(url=self.channel_url,api=False)
        html = response.text #-> save a text response from prev request
        soup = BeautifulSoup(html, 'html.parser')
        
        script_tag = soup.find('script', string=lambda text: text and 'ytInitialData' in text)
        script_text = script_tag.text.strip()
        data_part = script_text.split('ytInitialData = ')[1]
        data_part = json.loads(data_part.strip(';'))
        self.channel_data = {}
        self.channel_data['channel_name'] = data_part.get('microformat', {}).get('microformatDataRenderer', {}).get('title')
        channel_tag = data_part.get('microformat',{}).get('microformatDataRenderer',{}).get('tags',[])
        if channel_tag:
            self.channel_data['channel_tag'] = data_part.get('microformat',{}).get('microformatDataRenderer',{}).get('tags',[])
        else:
            self.channel_data['channel_tag'] = None
        self.channel_data['channel_id'] = data_part.get('metadata', {}).get('channelMetadataRenderer', {}).get('externalId')
        owner_url = data_part.get('metadata',{}).get('channelMetadataRenderer',{}).get('ownerUrls')
        if owner_url:
            self.channel_data['owner_urls'] = owner_url[0]
        else:
            self.channel_data['owner_urls'] = None
        self.channel_data['channel_url'] = data_part.get('metadata',{}).get('channelMetadataRenderer',{}).get('channelUrl',{})
        self.channel_data['isFamilySafe'] = data_part.get('metadata',{}).get('channelMetadataRenderer',{}).get('isFamilySafe',{})
        
        if self.channel_data['channel_tag']:
            self.channel_data['channel_tag'] = ",".join(data_part.get('microformat',{}).get('microformatDataRenderer',{}).get('tags',[]))
        
        url_channel_api = "https://content-youtube.googleapis.com/youtube/v3/channels"

        param = {
            'id': self.channel_data['channel_id'],
            'part': "brandingSettings,contentDetails,contentOwnerDetails,id,localizations,snippet,statistics,status,topicDetails",
            'key': self.api_key
        }
        response = self.make_request(url=url_channel_api, params=param)
        self.channel_data['title'] = response.get('items',[])[0].get('snippet',{}).get('title')
        self.channel_data['description'] = response.get('items',[])[0].get('snippet',{}).get('description')
        self.channel_data['custom_id'] = response.get('items',[])[0].get('snippet',{}).get('customUrl')
        self.channel_data['date_created(UTC)'] = self.convert_to_datetime(response.get('items',[])[0].get('snippet',{}).get('publishedAt'))
        self.channel_data['thumbnails_default'] = response.get('items',[])[0].get('snippet',{}).get('thumbnails',{}).get('default',{}).get('url')
        self.channel_data['country'] = response.get('items',[])[0].get('snippet',{}).get('country')
        self.channel_data['all_video_upload_playlist_id'] = response.get('items',[])[0].get('contentDetails',{}).get('relatedPlaylists',{}).get('uploads')
        view_count = response.get('items',[])[0].get('statistics',{}).get('viewCount')
        video_count = response.get('items',[])[0].get('statistics',{}).get('videoCount')
        subs_count = response.get('items',[])[0].get('statistics',{}).get('subscriberCount')
        if view_count:
            self.channel_data['views_count'] = int(view_count)
        else:
            self.channel_data['views_count'] = None
        if video_count:
            self.channel_data['video_count'] = int(video_count)
        else:
            self.channel_data['video_count'] = None
        if subs_count:
            self.channel_data['subs_count'] = int(subs_count)
        else:
            self.channel_data['subs_count'] = None
        self.channel_data['hidden_sub'] = response.get('items',[])[0].get('statistics',{}).get('hiddenSubscriberCount')
        topic = response.get('items',[])[0].get('topicDetails',{}).get('topicCategories',[])
        
        if topic:
            self.channel_data['topic'] = ','.join([cat.split('/')[-1] for cat in topic])
        else:
            self.channel_data['topic'] = None
       
        return self.channel_data
        
    
    def scrape_playlist_item(self, playlist_id:str):
        """Scrapes data from the YouTube channel using the constructed URL and session with headers.

        Raises:
            ConnectionError: If a connection error occurs.
            requests.exceptions.RequestException: If a request fails due to other reasons.

        Returns:
            dict: A dictionary containing scraped data channel video.
        """
        if not isinstance(playlist_id, (str)):
            raise TypeError("playlist_id must be a string or a list")
        url_channel_api = 'https://content-youtube.googleapis.com/youtube/v3/playlistItems'
        param = {
            'part': 'contentDetails,id,snippet,status',
            'maxResults': '50',
            'playlistId': playlist_id,
            'key': self.api_key
        }

        response = self.make_request(url=url_channel_api, params=param)
        video_list = []
        for i in range(len(response.get('items',[]))):
            video_list.append(response.get('items',[])[i].get('snippet',{}).get('resourceId',{}).get('videoId'))
        page_token = response.get('nextPageToken')
        while page_token != None:
            url_channel_api = 'https://content-youtube.googleapis.com/youtube/v3/playlistItems'
            param = {
                'maxResults': '50',
                'pageToken': page_token,
                'playlistId': playlist_id,
                'part': 'contentDetails,id,snippet,status',
                'key': self.api_key
            }
            response = self.make_request(url=url_channel_api, params=param)
            for i in range(len(response.get('items',[]))):
                video_list.append(response.get('items',[])[i].get('snippet',{}).get('resourceId',{}).get('videoId'))
            page_token = response.get('nextPageToken')
        return video_list   
    
    def scrape_video_data(self, video_id: Union[list, str])->pd.DataFrame:
        """
        Scrapes video data from YouTube using the YouTube Data API v3.

        Args:
            video_id (Union[list, str]): A list of video IDs or a single video ID.

        Returns:
            pd.DataFrame: A DataFrame containing the scraped video data.

        Raises:
            ValueError: If the provided video ID is not a string or a list of strings.
        """
        if not isinstance(video_id, (str, list)):
            raise TypeError("playlist_id must be a string or a list")
        temp_list = []
        if isinstance(video_id, (list)):
            batches = []
            for i in range(0, len(video_id), 50):
                batches.append(','.join(video_id[i:i + 50]))
            for batch in range(0,len(batches),1):   
                url_channel_api = 'https://content-youtube.googleapis.com/youtube/v3/videos'
                param = {
                    'id': batches[batch],
                    'part': 'contentDetails,id,liveStreamingDetails,localizations,snippet,statistics,status,topicDetails,player',
                    'maxResults': '50',
                    'key': self.api_key}
                response = self.make_request(url=url_channel_api, params=param)
                if len(response.get('items',[]))<1:
                    raise ValueError("invalid playlist id")
                for i in range(len(response.get('items',[]))):
                    temp_dict = {}
                    temp_dict['published_date'] = self.convert_to_datetime(response.get('items',[])[i].get('snippet',{}).get('publishedAt'))
                    temp_dict['channel_id'] = response.get('items',[])[i].get('snippet',{}).get('channelId')
                    temp_dict['channel_title'] = response.get('items',[])[i].get('snippet',{}).get('channelTitle')
                    temp_dict['video_title'] = response.get('items',[])[i].get('snippet',{}).get('title')
                    temp_dict['description'] = response.get('items',[])[i].get('snippet',{}).get('description')
                    temp_dict['thumbnail_url'] = response.get('items',[])[i].get('snippet',{}).get('thumbnails',{}).get('default',{}).get('url')
                    tag_string = response.get('items',[])[i].get('snippet',{}).get('tags')
                    if tag_string:
                        temp_dict['video_tag'] = ','.join(tag_string)
                    else:
                        temp_dict['video_tag'] = None
                    temp_dict['categoryId'] = response.get('items',[])[i].get('snippet',{}).get('categoryId')
                    temp_dict['defaultAudioLanguage'] = response.get('items',[])[i].get('snippet',{}).get('defaultAudioLanguage')
                    temp_dict['duration(s)'] = self.parse_duration(response.get('items',[])[i].get('contentDetails',{}).get('duration'))
                    temp_dict['licensed_content'] = response.get('items',[])[i].get('contentDetails',{}).get('licensedContent')
                    temp_dict['status'] = response.get('items',[])[i].get('status',{}).get('privacyStatus')
                    temp_dict['for_kids'] = response.get('items',[])[i].get('status',{}).get('madeForKids')
                    temp_dict['view_count'] = response.get('items',[])[i].get('statistics',{}).get('viewCount')
                    temp_dict['like_count'] = response.get('items',[])[i].get('statistics',{}).get('likeCount')
                    temp_dict['favorite_count'] = response.get('items',[])[i].get('statistics',{}).get('favoriteCount')
                    temp_dict['comment_count'] = response.get('items',[])[i].get('statistics',{}).get('commentCount')
                    topic = response.get('items',[])[i].get('topicDetails',{}).get('topicCategories',[])
                    if topic:
                        temp_dict['topic_category'] = ','.join([cat.split('/')[-1] for cat in topic])
                    else:
                        temp_dict['topic_category'] = None
                    temp_dict['start_time(UTC)'] = self.convert_to_datetime(response.get('items',[])[i].get('liveStreamingDetails',{}).get('actualStartTime'))
                    temp_dict['end_time(UTC)'] = self.convert_to_datetime(response.get('items',[])[i].get('actualEndTime',{}).get('actualStartTime'))
                    temp_dict['scheduled_time(UTC)'] = self.convert_to_datetime(response.get('items',[])[i].get('liveStreamingDetails',{}).get('scheduledStartTime'))
                    temp_list.append(temp_dict)
                    
                    
        elif isinstance(video_id, (str)):
            url_channel_api = 'https://content-youtube.googleapis.com/youtube/v3/videos'
            param = {
                'id': video_id,
                'part': 'contentDetails,id,liveStreamingDetails,localizations,snippet,statistics,status,topicDetails,player',
                'maxResults': '50',
                'key': self.api_key}
            response = self.make_request(url=url_channel_api, params=param)
            if len(response.get('items',[]))<1:
                raise ValueError("invalid playlist id")
            for i in range(len(response.get('items',[]))):
                temp_dict = {}
                temp_dict['published_date'] = self.convert_to_datetime(response.get('items',[])[i].get('snippet',{}).get('publishedAt'))
                temp_dict['channel_id'] = response.get('items',[])[i].get('snippet',{}).get('channelId')
                temp_dict['channel_title'] = response.get('items',[])[i].get('snippet',{}).get('channelTitle')
                temp_dict['video_title'] = response.get('items',[])[i].get('snippet',{}).get('title')
                temp_dict['description'] = response.get('items',[])[i].get('snippet',{}).get('description')
                temp_dict['thumbnail_url'] = response.get('items',[])[i].get('snippet',{}).get('thumbnails',{}).get('default',{}).get('url')
                tag_string = response.get('items',[])[i].get('snippet',{}).get('tags')
                if tag_string:
                    temp_dict['video_tag'] = ','.join(tag_string)
                else:
                    temp_dict['video_tag'] = None
                temp_dict['categoryId'] = response.get('items',[])[i].get('snippet',{}).get('categoryId')
                temp_dict['defaultAudioLanguage'] = response.get('items',[])[i].get('snippet',{}).get('defaultAudioLanguage')
                temp_dict['duration(s)'] = self.parse_duration(response.get('items',[])[i].get('contentDetails',{}).get('duration'))
                temp_dict['licensed_content'] = response.get('items',[])[i].get('contentDetails',{}).get('licensedContent')
                temp_dict['status'] = response.get('items',[])[i].get('status',{}).get('privacyStatus')
                temp_dict['for_kids'] = response.get('items',[])[i].get('status',{}).get('madeForKids')
                temp_dict['view_count'] = response.get('items',[])[i].get('statistics',{}).get('viewCount')
                temp_dict['like_count'] = response.get('items',[])[i].get('statistics',{}).get('likeCount')
                temp_dict['favorite_count'] = response.get('items',[])[i].get('statistics',{}).get('favoriteCount')
                temp_dict['comment_count'] = response.get('items',[])[i].get('statistics',{}).get('commentCount')
                topic = response.get('items',[])[i].get('topicDetails',{}).get('topicCategories',[])
                if topic:
                    temp_dict['topic_category'] = ','.join([cat.split('/')[-1] for cat in topic])
                else:
                    temp_dict['topic_category'] = None     
                temp_dict['start_time(UTC)'] = self.convert_to_datetime(response.get('items',[])[i].get('liveStreamingDetails',{}).get('actualStartTime'))
                temp_dict['end_time(UTC)'] = self.convert_to_datetime(response.get('items',[])[i].get('actualEndTime',{}).get('actualStartTime'))
                temp_dict['scheduled_time(UTC)'] = self.convert_to_datetime(response.get('items',[])[i].get('liveStreamingDetails',{}).get('scheduledStartTime'))
                temp_list.append(temp_dict)  
        temp_list = pd.DataFrame.from_records(temp_list)
        numeric_col = ['duration(s)','view_count','like_count','favorite_count','comment_count']
        date_col = ['published_date','start_time(UTC)','end_time(UTC)','scheduled_time(UTC)']
        temp_list[numeric_col] = temp_list[numeric_col].apply(pd.to_numeric, errors='coerce', axis=1,downcast='integer') 
        temp_list[date_col] = temp_list[date_col].apply(pd.to_datetime, errors='coerce', axis=1) 
        return temp_list
    
    def parse_duration(self,duration):
        """
          Parses an ISO 8601 duration string and converts it to the total number of seconds.
        
          Args:
              duration: The ISO 8601 duration string to be parsed. 
                  Examples: "PT1H2M3S", "PT20M", "P1D" (day not supported)
        
          Returns:
              The total number of seconds represented by the duration string. 
              Returns 0 if the string is not a valid ISO 8601 duration format.
          """
        
        # Regex to extract hours, minutes, and seconds from the ISO 8601 duration
        pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        match = pattern.match(duration)

        if not match:
            return 0

        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        seconds = int(match.group(3)) if match.group(3) else 0

        # Convert the duration to seconds
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds
    
    def convert_to_datetime(self,iso_string):
        """
        Converts an ISO 8601 formatted date-time string to a Python datetime object.

        This method handles ISO 8601 strings with or without a trailing 'Z' indicating UTC time.
        If the provided string is empty or cannot be parsed as a datetime, it returns None.

        Args:
            iso_string (str): The ISO 8601 formatted date-time string to convert.

        Returns:
            datetime: The converted datetime object, or None if the conversion fails.
        """
        if iso_string:
            return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        else:
            return None
    
    def validate_date(self,date_str: str) -> str:
        """
        Validates the given date string to ensure it is in the correct format.

        Args:
            date_str (str): The date string to be validated.

        Returns:
            bool: True if the date is valid, False otherwise.

        Raises:
            ValueError: If the date format is invalid.
        """
        try:
            date_object = datetime.strptime(date_str, "%Y-%m-%d")
            return date_object.isoformat(timespec="seconds") + "Z"
        except ValueError:
            raise ValueError("Format date invalid. use format yyyy-mm-dd.")
        except TypeError:
            raise TypeError("Format date invalid. use format yyyy-mm-dd in string not integer.")
    
    def scrape_search_video(self,q:str,regionCode:str,publishedAfter:str=None,publishedBefore:str=None,max_data:int=100,event_type:str='completed')->pd.DataFrame:
        """
        Scrapes search results for videos on YouTube using the YouTube Data API v3.

        This method searches for videos based on a query string (`q`), region code (`regionCode`),
        event type (`event_type`), and optional filters for published date (`publishedAfter`, `publishedBefore`).
        It retrieves video details and basic channel information for a maximum of `max_data` results 
        (or all results if `all_data` is True).

        Args:
            q (str): The search query string.
            regionCode (str): The YouTube region code (e.g., US, GB).
            publishedAfter (str, optional): The ISO 8601 formatted date after which to search (inclusive).
            publishedBefore (str, optional): The ISO 8601 formatted date before which to search (exclusive).
            max_data (int, optional): The maximum number of video results to scrape (default: 100, maximum: 10,000).
            event_type (str, optional): The event type to search for ("completed", "live", or "upcoming"). Defaults to "completed".
            all_data (bool, optional): If True, retrieves all search results (up to 500). Defaults to False.

        Returns:
            pd.DataFrame: A DataFrame containing the scraped video data and basic channel information.

        Raises:
            ValueError: If the event_type is not one of "completed", "live", or "upcoming".
        """
        if event_type not in ['completed','live','upcoming']:
            raise ValueError('event type must one of these ["completed","live","upcoming"]')
        if publishedAfter is not None:
            publishedAfter = self.validate_date(publishedAfter)
        if publishedBefore is not None:
            publishedBefore = self.validate_date(publishedBefore)
        if max_data > 10000:
            raise ValueError("Maximum allowed value for max_data is 5000.")
        url_channel_api = 'https://content-youtube.googleapis.com/youtube/v3/search'
        
        rank = 1
        data_count = 0
        param = {
            'q': q,
            'publishedAfter': publishedAfter,
            'maxResults': '50',
            'regionCode': regionCode,
            'order': 'relevance',
            'type': 'video',
            'part': 'snippet',
            'publishedBefore': publishedBefore,
            'eventType': event_type,
            'key': self.api_key
        }
        response = self.make_request(url=url_channel_api, params=param)
        next_page = response.get('nextPageToken')
        list_data = []
        
        for i in range(len(response.get('items',[]))):
            if data_count < max_data:
                temp_dict = {}
                temp_dict['keyword'] = q
                temp_dict['ranking'] = rank
                temp_dict['video_id'] = response.get('items',[])[i].get('id',{}).get('videoId')
                temp_dict['date_video_published(UTC)'] = self.convert_to_datetime(response.get('items',[])[i].get('snippet',{}).get('publishedAt'))
                temp_dict['video_title'] = response.get('items',[])[i].get('snippet',{}).get('title')
                temp_dict['video_description'] = response.get('items',[])[i].get('snippet',{}).get('description')
                temp_dict['video_thumbnail'] = response.get('items',[])[i].get('snippet',{}).get('thumbnails',{}).get('default',{}).get('url')
                #----------------------------------------
                temp_video_data = self.scrape_video_data(temp_dict['video_id'])
                temp_dict['video_default_audio_language'] = temp_video_data['defaultAudioLanguage'].iat[0]
                temp_dict['video_status'] = temp_video_data['status'].iat[0]
                temp_dict['video_duration(s)'] = temp_video_data['duration(s)'].iat[0]
                temp_dict['video_licenced_content'] = temp_video_data['licensed_content'].iat[0]
                temp_dict['video_tag'] =  temp_video_data['video_tag'].iat[0]
                temp_dict['video_view_count'] = temp_video_data['view_count'].iat[0]
                temp_dict['video_like_count'] = temp_video_data['like_count'].iat[0]
                temp_dict['video_favorite_count'] = temp_video_data['favorite_count'].iat[0]
                temp_dict['video_comment_count'] = temp_video_data['comment_count'].iat[0]
                temp_dict['is_video_for_kids'] = temp_video_data['for_kids'].iat[0]
                temp_dict['video_topic_id'] = temp_video_data['categoryId'].iat[0]
                temp_dict['video_topic'] = temp_video_data['topic_category'].iat[0]
                temp_dict['video_start_time(UTC)'] = temp_video_data['start_time(UTC)'].iat[0]
                temp_dict['video_end_time(UTC)'] = temp_video_data['end_time(UTC)'].iat[0]
                temp_dict['video_scheduled_time(UTC)'] = temp_video_data['scheduled_time(UTC)'].iat[0]
                #--------------------------------------------
                temp_dict['channel_id'] = response.get('items',[])[i].get('snippet',{}).get('channelId')
                temp_dict['channel_title'] = response.get('items',[])[i].get('snippet',{}).get('channelTitle')
                temp_channel_data = self.scrape_channel_basic_data(temp_dict['channel_id'])
                temp_dict['date_channel_create(UTC)'] = temp_channel_data['date_created(UTC)']
                temp_dict['channel_country'] = temp_channel_data['country']
                temp_dict['channel_all_video_upload_playlist_id'] = temp_channel_data['all_video_upload_playlist_id']
                temp_dict['channel_url'] = temp_channel_data['channel_url']
                temp_dict['channel_owner_url'] = temp_channel_data['owner_urls']
                temp_dict['channel_description'] = temp_channel_data['description']
                temp_dict['channel_custom_id'] = temp_channel_data['custom_id']
                temp_dict['channel_tag'] = temp_channel_data['channel_tag']
                temp_dict['is_channel_Family_safe'] = temp_channel_data['isFamilySafe']
                temp_dict['is_channel_hiden_sub'] = temp_channel_data['hidden_sub']
                temp_dict['channel_topic'] = temp_channel_data['topic']
                temp_dict['channel_view_count'] = temp_channel_data['views_count']
                temp_dict['channel_video_count'] = temp_channel_data['video_count']
                temp_dict['channel_subs_count'] = temp_channel_data['subs_count']
                list_data.append(temp_dict)
                rank +=1
                data_count += 1
        while data_count < max_data or next_page is not None:
            param = {
                'q': q,
                'publishedAfter': publishedAfter,
                'maxResults': '50',
                'regionCode': regionCode,
                'pageToken' : next_page,
                'order': 'relevance',
                'type': 'video',
                'part': 'snippet',
                'publishedBefore': publishedBefore,
                'eventType': event_type,
                'key': self.api_key
            }
            response = self.make_request(url=url_channel_api, params=param)
            next_page = response.get('nextPageToken')
            for i in range(len(response.get('items',[]))):
                if data_count < max_data:
                    temp_dict = {}
                    temp_dict['keyword'] = q
                    temp_dict['ranking'] = rank
                    temp_dict['video_id'] = response.get('items',[])[i].get('id',{}).get('videoId')
                    temp_dict['date_video_published(UTC)'] = self.convert_to_datetime(response.get('items',[])[i].get('snippet',{}).get('publishedAt'))
                    temp_dict['video_title'] = response.get('items',[])[i].get('snippet',{}).get('title')
                    temp_dict['video_description'] = response.get('items',[])[i].get('snippet',{}).get('description')
                    temp_dict['video_thumbnail'] = response.get('items',[])[i].get('snippet',{}).get('thumbnails',{}).get('default',{}).get('url')
                    #----------------------------------------
                    temp_video_data = self.scrape_video_data(temp_dict['video_id'])
                    temp_dict['video_default_audio_language'] = temp_video_data['defaultAudioLanguage'].iat[0]
                    temp_dict['video_status'] = temp_video_data['status'].iat[0]
                    temp_dict['video_duration(s)'] = temp_video_data['duration(s)'].iat[0]
                    temp_dict['video_licenced_content'] = temp_video_data['licensed_content'].iat[0]
                    temp_dict['video_tag'] =  temp_video_data['video_tag'].iat[0]
                    temp_dict['video_view_count'] = temp_video_data['view_count'].iat[0]
                    temp_dict['video_like_count'] = temp_video_data['like_count'].iat[0]
                    temp_dict['video_favorite_count'] = temp_video_data['favorite_count'].iat[0]
                    temp_dict['video_comment_count'] = temp_video_data['comment_count'].iat[0]
                    temp_dict['is_video_for_kids'] = temp_video_data['for_kids'].iat[0]
                    temp_dict['video_topic_id'] = temp_video_data['categoryId'].iat[0]
                    temp_dict['video_topic'] = temp_video_data['topic_category'].iat[0]
                    temp_dict['video_start_time(UTC)'] = temp_video_data['start_time(UTC)'].iat[0]
                    temp_dict['video_end_time(UTC)'] = temp_video_data['end_time(UTC)'].iat[0]
                    temp_dict['video_scheduled_time(UTC)'] = temp_video_data['scheduled_time(UTC)'].iat[0]
                    #--------------------------------------------
                    temp_dict['channel_id'] = response.get('items',[])[i].get('snippet',{}).get('channelId')
                    temp_dict['channel_title'] = response.get('items',[])[i].get('snippet',{}).get('channelTitle')
                    temp_channel_data = self.scrape_channel_basic_data(temp_dict['channel_id'])
                    temp_dict['date_channel_create(UTC)'] = temp_channel_data['date_created(UTC)']
                    temp_dict['channel_country'] = temp_channel_data['country']
                    temp_dict['channel_all_video_upload_playlist_id'] = temp_channel_data['all_video_upload_playlist_id']
                    temp_dict['channel_url'] = temp_channel_data['channel_url']
                    temp_dict['channel_owner_url'] = temp_channel_data['owner_urls']
                    temp_dict['channel_description'] = temp_channel_data['description']
                    temp_dict['channel_custom_id'] = temp_channel_data['custom_id']
                    temp_dict['channel_tag'] = temp_channel_data['channel_tag']
                    temp_dict['is_channel_Family_safe'] = temp_channel_data['isFamilySafe']
                    temp_dict['is_channel_hiden_sub'] = temp_channel_data['hidden_sub']
                    temp_dict['channel_topic'] = temp_channel_data['topic']
                    temp_dict['channel_view_count'] = temp_channel_data['views_count']
                    temp_dict['channel_video_count'] = temp_channel_data['video_count']
                    temp_dict['channel_subs_count'] = temp_channel_data['subs_count']
                    list_data.append(temp_dict)
                    data_count += 1
                    rank +=1
        
        list_data = pd.DataFrame.from_records(list_data)
        numeric_cols = [
            'ranking', 'video_duration(s)', 'video_view_count', 'video_like_count',
            'video_favorite_count', 'video_comment_count', 'channel_view_count',
            'channel_video_count', 'channel_subs_count'
        ]
        datetime_cols = [
            'date_video_published(UTC)', 'video_start_time(UTC)',
            'video_end_time(UTC)', 'video_scheduled_time(UTC)','date_channel_create(UTC)'
        ]
        
        list_data[numeric_cols] = list_data[numeric_cols].apply(pd.to_numeric, errors='coerce', axis=1, downcast='integer') 
        list_data[datetime_cols] = list_data[datetime_cols].apply(pd.to_datetime, errors='coerce', axis=1) 
        
        return list_data
    
    def make_request(self,url:str, params=None, max_retries=10, backoff_factor=10,api:bool=True):
        """
        Makes a GET request to a URL with optional parameters and retries on errors.

        This method handles both API requests (using a separate session with potential authentication)
        and regular requests. It implements a retry mechanism with exponential backoff for a 
        specified number of attempts (`max_retries`) in case of connection errors or HTTP errors.

        Args:
            url (str): The URL to make the request to.
            params (dict, optional): A dictionary of query parameters to include in the request.
            max_retries (int, optional): The maximum number of retries in case of errors (default: 10).
            backoff_factor (int, optional): The base factor for the exponential backoff between retries (default: 10).
            api (bool, optional): Indicates if the request is for an API endpoint (default: True).

        Returns:
            dict or requests.Response: The JSON response for API requests or the raw response object for non-API requests.

        Raises:
            Exception: If the request fails after all retries.
        """
        retries = 1
        while True:
            try:
                if api:
                    response = self.session_api.get(url, params=params)
                    response.raise_for_status()
                    return response.json()
                else:
                    response = self.session.get(url)
                    response.raise_for_status()
                    return response
            except HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")
                raise
            except (ConnectionError, req.exceptions.RequestException) as e:
                print(e)
                if api:
                    print('try again')
                    time.sleep(backoff_factor * (2 ** retries))
                    return self.session_api.get(url, params=params).json()
                else:
                    print('try again')
                    time.sleep(backoff_factor * (2 ** retries))
                    return self.session.get(url)
    def scrape_search_channel(self,q:str,regionCode:str,publishedAfter:str=None,publishedBefore:str=None,max_data:int=100)->pd.DataFrame:
        if publishedAfter is not None:
            publishedAfter = self.validate_date(publishedAfter)
        if publishedBefore is not None:
            publishedBefore = self.validate_date(publishedBefore)
        if max_data >= 10000:
            raise ValueError("Maximum allowed value for max_data is 10000.")
        url_channel_api = 'https://content-youtube.googleapis.com/youtube/v3/search'
        rank = 1
        data_count = 0
        param = {
            'q': q,
            'publishedAfter': publishedAfter,
            'maxResults': '50',
            'regionCode': regionCode,
            'order': 'relevance',
            'type': 'channel',
            'part': 'snippet',
            'publishedBefore': publishedBefore,
            'key': self.api_key
        }
        response = self.make_request(url=url_channel_api, params=param)
        next_page = response.get('nextPageToken')
        list_data = []
        for data in range(len(response.get('items',[]))):
            if data_count < max_data:
                temp_dict = {}
                temp_dict['keyword'] = q
                temp_dict['ranking'] = rank
                temp_channel_data = self.scrape_channel_basic_data(response.get('items',[])[data].get('snippet',{}).get('channelId'))
                temp_dict['date_channel_create(UTC)'] = temp_channel_data['date_created(UTC)']
                temp_dict['channel_country'] = temp_channel_data['country']
                temp_dict['channel_all_video_upload_playlist_id'] = temp_channel_data['all_video_upload_playlist_id']
                temp_dict['channel_url'] = temp_channel_data['channel_url']
                temp_dict['channel_owner_url'] = temp_channel_data['owner_urls']
                temp_dict['channel_description'] = temp_channel_data['description']
                temp_dict['channel_custom_id'] = temp_channel_data['custom_id']
                temp_dict['channel_tag'] = temp_channel_data['channel_tag']
                temp_dict['is_channel_Family_safe'] = temp_channel_data['isFamilySafe']
                temp_dict['is_channel_hiden_sub'] = temp_channel_data['hidden_sub']
                temp_dict['channel_topic'] = temp_channel_data['topic']
                temp_dict['channel_view_count'] = temp_channel_data['views_count']
                temp_dict['channel_video_count'] = temp_channel_data['video_count']
                temp_dict['channel_subs_count'] = temp_channel_data['subs_count']
                list_data.append(temp_dict)
                data_count += 1
                rank += 1
        while data_count < max_data or next_page is not None:
            param = {
                'pageToken' : next_page,
                'q': q,
                'publishedAfter': publishedAfter,
                'maxResults': '50',
                'regionCode': regionCode,
                'order': 'relevance',
                'type': 'channel',
                'part': 'snippet',
                'publishedBefore': publishedBefore,
                'key': self.api_key
            }
            response = self.make_request(url=url_channel_api, params=param)
            next_page = response.get('nextPageToken')
            for i in range(len(response.get('items',[]))):
                if data_count < max_data:
                    temp_dict = {}
                    temp_dict['keyword'] = q
                    temp_dict['ranking'] = rank
                    temp_channel_data = self.scrape_channel_basic_data(response.get('items',[])[data].get('snippet',{}).get('channelId'))
                    temp_dict['date_channel_create(UTC)'] = temp_channel_data['date_created(UTC)']
                    temp_dict['channel_country'] = temp_channel_data['country']
                    temp_dict['channel_all_video_upload_playlist_id'] = temp_channel_data['all_video_upload_playlist_id']
                    temp_dict['channel_url'] = temp_channel_data['channel_url']
                    temp_dict['channel_owner_url'] = temp_channel_data['owner_urls']
                    temp_dict['channel_description'] = temp_channel_data['description']
                    temp_dict['channel_custom_id'] = temp_channel_data['custom_id']
                    temp_dict['channel_tag'] = temp_channel_data['channel_tag']
                    temp_dict['is_channel_Family_safe'] = temp_channel_data['isFamilySafe']
                    temp_dict['is_channel_hiden_sub'] = temp_channel_data['hidden_sub']
                    temp_dict['channel_topic'] = temp_channel_data['topic']
                    temp_dict['channel_view_count'] = temp_channel_data['views_count']
                    temp_dict['channel_video_count'] = temp_channel_data['video_count']
                    temp_dict['channel_subs_count'] = temp_channel_data['subs_count']
                    list_data.append(temp_dict)
                    data_count += 1
                    rank += 1
        list_data = pd.DataFrame.from_records(list_data)
        numeric_cols = [
            'ranking', 'channel_view_count',
            'channel_video_count', 'channel_subs_count'
        ]
        datetime_cols = [
            'date_channel_create(UTC)'
        ]
        
        list_data[numeric_cols] = list_data[numeric_cols].apply(pd.to_numeric, errors='coerce', axis=1, downcast='integer') 
        list_data[datetime_cols] = list_data[datetime_cols].apply(pd.to_datetime, errors='coerce', axis=1)
        return list_data
    
                        