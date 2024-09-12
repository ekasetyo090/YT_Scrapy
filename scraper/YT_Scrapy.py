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

import pytz
from datetime import datetime
import dateutil.parser
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
        
        self.TOPIC_ID = {
            "music (parent topic)": "/m/04rlf",
            "christian spiritual music": "/m/02mscn",
            "classical music": "/m/0ggq0m",
            "country": "/m/01lyv",
            "electronic music": "/m/02lkt",
            "hip hop music": "/m/0glt670",
            "indie music": "/m/05rwpb",
            "jazz music": "/m/03_d0",
            "asian music": "/m/028sqc",
            "latin american music": "/m/0g293",
            "pop music": "/m/064t9",
            "reggae music": "/m/06cqb",
            "rhythm and blues music": "/m/06j6l",
            "rock music": "/m/06by7",
            "soul music": "/m/0gywn",
            "games (parent topic)": "/m/0bzvm2",
            "action games": "/m/025zzc",
            "action-adventure games": "/m/02ntfj",
            "casual games": "/m/0b1vjn",
            "music video games": "/m/02hygl",
            "puzzle video games": "/m/04q1x3q",
            "racing video games": "/m/01sjng",
            "role-playing video games": "/m/0403l3g",
            "simulation video games": "/m/021bp2",
            "sports games": "/m/022dc6",
            "strategy video games": "/m/03hf_rm",
            "sports (parent topic)": "/m/06ntj",
            "american football": "/m/0jm_",
            "baseball": "/m/018jz",
            "basketball": "/m/018w8",
            "boxing": "/m/01cgz",
            "cricket": "/m/09xp_",
            "football (soccer)": "/m/02vx4",
            "golf": "/m/037hz",
            "ice hockey": "/m/03tmr",
            "mixed martial arts": "/m/01h7lh",
            "motorsport": "/m/0410tth",
            "tennis": "/m/07bs0",
            "volleyball": "/m/07_53",
            "entertainment (parent topic)": "/m/02jjt",
            "comedy": "/m/09kqc",
            "film": "/m/02vxn",
            "performing arts": "/m/05qjc",
            "professional wrestling": "/m/066wd",
            "tv shows": "/m/0f2f9",
            "lifestyle (parent topic)": "/m/019_rr",
            "fashion": "/m/032tl",
            "fitness": "/m/027x7n",
            "food": "/m/02wbm",
            "hobbies": "/m/03glg",
            "pets": "/m/068hy",
            "physical attraction [beauty]": "/m/041xxh",
            "technology": "/m/07c1v",
            "travel": "/m/07bxq",
            "vehicles": "/m/07yv9",
            "society (parent topic)": "/m/098wr",
            "business": "/m/09s1f",
            "health": "/m/0kt51",
            "military": "/m/01h6rj",
            "politics": "/m/05qt0",
            "religion": "/m/06bvp",
            "knowledge": "/m/01k8wb"
        }
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
    def validate_topic(self,topic_id:Union[list, str]):
        if topic_id is not None:
            if isinstance(topic_id, list):            
                if not all(item in topic_id for item in list(self.TOPIC_ID.values())):
                    raise ValueError("invalid topic id, check topic id with self.TOPIC_ID")
                return ','.join(topic_id)
            
            elif isinstance(topic_id, str):
                if topic_id not in list(self.TOPIC_ID.values()):
                    raise ValueError("invalid topic id, check topic id with self.TOPIC_ID")
                return topic_id
            else:
                raise TypeError("topic id only takes str or list")
        else:
            return None
    
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
        pattern = r'this\.Ic\s*=\s*"([\w\-\_\n]*)"'
        match = re.search(pattern, response.text)
        api_key = match.group(1)
        #------------
        self.session_api.headers["Referer"] = 'https://developers.google.com/'
        response = self.session_api.get('https://apis.google.com/js/api.js')
        pattern = r'h:"(m;/_/scs/abc-static/_/js/k=gapi\.lb\.en\.[^"]*)"'
        match = re.search(pattern, response.text)
        reff = urllib.parse.quote(match.group(1), safe='')
        
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
        self.channel_data['thumbnails_default'] = response.get('items',[])[0].get('snippet',{}).get('thumbnails',{}).get('high',{}).get('url')
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
            self.channel_data['topic'] = ((','.join([cat.split('/')[-1] for cat in topic])).replace('_',' ')).replace('-', ' ')
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
                    temp_dict['video_id'] = response.get('items',[])[i].get('id',{})
                    temp_dict['description'] = response.get('items',[])[i].get('snippet',{}).get('description')
                    temp_dict['thumbnail_url'] = response.get('items',[])[i].get('snippet',{}).get('thumbnails',{}).get('standard',{}).get('url')
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
                        temp_dict['topic_category'] = ((','.join([cat.split('/')[-1] for cat in topic])).replace('_',' ')).replace('-',' ')
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
                temp_dict['video_id'] = response.get('items',[])[i].get('id',{})
                temp_dict['description'] = response.get('items',[])[i].get('snippet',{}).get('description')
                temp_dict['thumbnail_url'] = response.get('items',[])[i].get('snippet',{}).get('thumbnails',{}).get('standard',{}).get('url')
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
                    temp_dict['topic_category'] = ((','.join([cat.split('/')[-1] for cat in topic])).replace('_',' ')).replace('-', ' ')
                else:
                    temp_dict['topic_category'] = None     
                temp_dict['start_time(UTC)'] = self.convert_to_datetime(response.get('items',[])[i].get('liveStreamingDetails',{}).get('actualStartTime'))
                temp_dict['end_time(UTC)'] = self.convert_to_datetime(response.get('items',[])[i].get('actualEndTime',{}).get('actualStartTime'))
                temp_dict['scheduled_time(UTC)'] = self.convert_to_datetime(response.get('items',[])[i].get('liveStreamingDetails',{}).get('scheduledStartTime'))
                temp_list.append(temp_dict)  
        temp_list = pd.DataFrame.from_records(temp_list)
        numeric_col = ['duration(s)','view_count','like_count','favorite_count','comment_count']
        date_col = ['published_date','start_time(UTC)','end_time(UTC)','scheduled_time(UTC)']
        for i in numeric_col:
            temp_list[i] = pd.to_numeric(temp_list[i], errors='coerce', downcast='integer')
        for i in date_col:
            temp_list[i] = pd.to_datetime(temp_list[i], errors='coerce')
        
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
        if not duration:
            return 0
        # Regex to extract hours, minutes, and seconds from the ISO 8601 duration
        pattern = re.compile(
            r'P'  # starts with 'P'
            r'(?:(?P<years>\d+)Y)?'  # years
            r'(?:(?P<months>\d+)M)?'  # months
            r'(?:(?P<weeks>\d+)W)?'  # weeks
            r'(?:(?P<days>\d+)D)?'  # days
            r'(?:T'  # time part starts with 'T'
            r'(?:(?P<hours>\d+)H)?'  # hours
            r'(?:(?P<minutes>\d+)M)?'  # minutes
            r'(?:(?P<seconds>\d+)S)?'  # seconds
            r')?'  # end of the time part
        )
    
        # Match the pattern with the input duration string
        match = pattern.match(duration)
        if not match:
            return 0
    
        # Extract the matched groups as integers (default to 0 if not present)
        duration = match.groupdict()
        years = int(duration['years']) if duration['years'] else 0
        months = int(duration['months']) if duration['months'] else 0
        weeks = int(duration['weeks']) if duration['weeks'] else 0
        days = int(duration['days']) if duration['days'] else 0
        hours = int(duration['hours']) if duration['hours'] else 0
        minutes = int(duration['minutes']) if duration['minutes'] else 0
        seconds = int(duration['seconds']) if duration['seconds'] else 0
    
        # Convert everything to seconds
        total_seconds = (
            years * 365 * 24 * 60 * 60 +
            months * 30 * 24 * 60 * 60 +
            weeks * 7 * 24 * 60 * 60 +
            days * 24 * 60 * 60 +
            hours * 60 * 60 +
            minutes * 60 +
            seconds
        )
    
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
        Validates the given date string and converts it to ISO format.
    
        Args:
            date_str (str): The date string to be validated.
    
        Returns:
            str: The date in ISO format (yyyy-mm-ddTHH:MM:SSZ).
    
        Raises:
            ValueError: If the date format is invalid.
        """
    
        try:
            # Attempt to parse the date string using strptime for yyyy-mm-dd format
            date_object = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            try:
                # Attempt to parse the date string using dateutil.parser for more complex formats
                date_object = dateutil.parser.parse(date_str)
            except ValueError:
                raise ValueError("Invalid date format. Use yyyy-mm-dd or ISO 8601 format.")
        date_object = date_object.replace(tzinfo=pytz.utc)
        return date_object.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    def scrape_search_video(self,
                            q:str=None,
                            regionCode:str=None,
                            publishedAfter:str=None,
                            publishedBefore:str=None,
                            duration:str='videoDurationUnspecified',
                            max_data:int=100,
                            event_type:str='completed',
                            topic_id: Union[list, str]=None,
                            all_data:bool=False)->pd.DataFrame:
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
            topic_id (Union[list, str]): A list of topic IDs or a single topic ID.

        Returns:
            pd.DataFrame: A DataFrame containing the scraped video data and basic channel information.

        Raises:
            ValueError: If the event_type is not one of "completed", "live", or "upcoming".
        """
        raise_mesage = """
        q (str): The search query string.
        regionCode (str): The YouTube region code (e.g., US, GB).
        publishedAfter (str, optional): The ISO 8601 formatted date after which to search (inclusive).
        publishedBefore (str, optional): The ISO 8601 formatted date before which to search (exclusive).
        duration (str,optional) : 'any','short','medium','long', and 'videoDurationUnspecified' 
        max_data (int, optional): The maximum number of video results to scrape (default: 100, maximum: 10,000).
        event_type (str, optional): The event type to search for ("completed", "live", or "upcoming"). Defaults to "completed".
        all_data (bool, optional): If True, retrieves all search results (up to 500). Defaults to False.
        topic_id (Union[list, str]): A list of topic IDs or a single topic ID.
        """
        if duration not in ['videoDurationUnspecified','any','short','medium','long']:
            raise ValueError('invalid duration argumen')
        if not topic_id and not q and not regionCode and not publishedAfter and not publishedBefore:
            raise ValueError(f'invalid args, all args (q,topic_id,regionCode,publishedAfter,publishedBefore) is empty. at least 1 arg is not empty : {raise_mesage}')
        topic_id = self.validate_topic(topic_id)
        if event_type not in ['completed','live','upcoming']:
            raise ValueError('event type must one of these ["completed","live","upcoming"]')
        if publishedAfter is not None:
            publishedAfter = self.validate_date(publishedAfter)
        if publishedBefore is not None:
            publishedBefore = self.validate_date(publishedBefore)
        
        url_channel_api = 'https://content-youtube.googleapis.com/youtube/v3/search'
        
        rank = 1
        data_count = 0
        param = {
            'q': q,
            'publishedAfter': publishedAfter,
            'maxResults': '50',
            'regionCode': regionCode,
            'videoDuration': duration,
            'order': 'relevance',
            'type': 'video',
            'part': 'snippet',
            'publishedBefore': publishedBefore,
            'eventType': event_type,
            'key': self.api_key,
            'topicId':topic_id
        }
        response = self.make_request(url=url_channel_api, params=param)
        next_page = response.get('nextPageToken')
        list_data = []
        
        for i in range(len(response.get('items',[]))):
            if all_data == False:
                if data_count == max_data:
                    break
            
            temp_dict = {}
            temp_dict['keyword'] = q
            temp_dict['ranking'] = rank
            temp_dict['video_id'] = response.get('items',[])[i].get('id',{}).get('videoId')
            temp_dict['date_video_published(UTC)'] = self.convert_to_datetime(response.get('items',[])[i].get('snippet',{}).get('publishedAt'))
            temp_dict['video_title'] = response.get('items',[])[i].get('snippet',{}).get('title')
            temp_dict['video_description'] = response.get('items',[])[i].get('snippet',{}).get('description')
            
            #----------------------------------------
            temp_video_data = self.scrape_video_data(temp_dict['video_id'])
            temp_dict['video_thumbnail'] = temp_video_data['thumbnail_url']
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
        while next_page is not None:
            if all_data == False:
                if data_count == max_data:
                    break
            param = {
                'q': q,
                'publishedAfter': publishedAfter,
                'maxResults': '50',
                'regionCode': regionCode,
                'pageToken' : next_page,
                'videoDuration': duration,
                'order': 'relevance',
                'type': 'video',
                'part': 'snippet',
                'publishedBefore': publishedBefore,
                'eventType': event_type,
                'key': self.api_key,
                'topicId':topic_id
            }
            response = self.make_request(url=url_channel_api, params=param)
            next_page = response.get('nextPageToken')
            for i in range(len(response.get('items',[]))):
                if all_data == False:
                    if data_count == max_data:
                        break
                
                temp_dict = {}
                temp_dict['keyword'] = q
                temp_dict['ranking'] = rank
                temp_dict['video_id'] = response.get('items',[])[i].get('id',{}).get('videoId')
                temp_dict['date_video_published(UTC)'] = self.convert_to_datetime(response.get('items',[])[i].get('snippet',{}).get('publishedAt'))
                temp_dict['video_title'] = response.get('items',[])[i].get('snippet',{}).get('title')
                temp_dict['video_description'] = response.get('items',[])[i].get('snippet',{}).get('description')
                
                #----------------------------------------
                temp_video_data = self.scrape_video_data(temp_dict['video_id'])
                temp_dict['video_thumbnail'] = temp_video_data['thumbnail_url']
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
        for i in numeric_cols:
            list_data[i] = pd.to_numeric(list_data[i], errors='coerce',downcast='integer') 
        for i in datetime_cols:
            list_data[i] = pd.to_datetime(list_data[i], errors='coerce') 
        
        return list_data
    
    def make_request(self,url:str, params=None, api:bool=True):
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
        try:
            if api:
                response = self.session_api.get(url, params=params)
                response.raise_for_status()
                return response.json()
            else:
                response = self.session.get(url)
                response.raise_for_status()
                return response
        except HTTPError:
            if response.status_code == 403:
                time.sleep(20)
                return self.make_request(url=url, params=params,api=api)
            else:
                raise  # Re-raise error jika bukan 403

        except (ConnectionError, req.exceptions.RequestException):
            time.sleep(20)
            return self.make_request(url=url, params=params,api=api)
        
                
    def scrape_search_channel(self,q:str=None,
                              regionCode:str=None,
                              publishedAfter:str=None,
                              publishedBefore:str=None,
                              max_data:int=100,
                              topic_id: Union[list, str]=None,
                              all_data:bool=False)->pd.DataFrame:
        raise_mesage = """
        q (str): The search query string.
        regionCode (str): The YouTube region code (e.g., US, GB).
        publishedAfter (str, optional): The ISO 8601 formatted date after which to search (inclusive).
        publishedBefore (str, optional): The ISO 8601 formatted date before which to search (exclusive).
        max_data (int, optional): The maximum number of video results to scrape (default: 100, maximum: 10,000).
        all_data (bool, optional): If True, retrieves all search results (up to 500). Defaults to False.
        topic_id (Union[list, str]): A list of topic IDs or a single topic ID.
        """
        if not topic_id and not q and not regionCode and not publishedAfter and not publishedBefore:
            raise ValueError(f'invalid args, all args is empty. at least 1 arg is not empty : {raise_mesage}')
        topic_id = self.validate_topic(topic_id)
        
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
            'key': self.api_key,
            'topicId':topic_id
        }
        response = self.make_request(url=url_channel_api, params=param)
        next_page = response.get('nextPageToken')
        list_data = []
        for data in range(len(response.get('items',[]))):
            if all_data == False:
                if data_count == max_data:
                    break
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
        while next_page is not None:
            if all_data == False:
                if data_count == max_data:
                    break
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
                'key': self.api_key,
                'topicId':topic_id
            }
            response = self.make_request(url=url_channel_api, params=param)
            next_page = response.get('nextPageToken')
            for i in range(len(response.get('items',[]))):
                if all_data == False:
                    if data_count == max_data:
                        break
                temp_dict = {}
                temp_dict['keyword'] = q
                temp_dict['ranking'] = rank
                temp_channel_data = self.scrape_channel_basic_data(response.get('items',[])[i].get('snippet',{}).get('channelId'))
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

        
        for i in numeric_cols:
            list_data[i] = pd.to_numeric(list_data[i], errors='coerce', downcast='integer')
       
        list_data['date_channel_create(UTC)'] = pd.to_datetime(list_data['date_channel_create(UTC)'], errors='coerce')
        return list_data
    
                        