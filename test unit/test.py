# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 00:01:18 2024

@author: eka setyo agung mahanani
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scraper')))

import unittest
import pandas as pd
import time
from datetime import datetime,timezone
from requests.exceptions import HTTPError
from YT_Scrapy import YtScraper

class YtScraperIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.instance = YtScraper()

    def test_channel_basic_data(self):   
        channel_id = '@cecilialieberia'
        channel_data = self.instance.scrape_channel_basic_data(channel_id)
        self.assertIsNotNone(channel_data)
        self.assertIn('title', channel_data)
        self.assertIn('description', channel_data)
        self.assertIn('custom_id', channel_data)
        self.assertIn('date_created(UTC)', channel_data)
        self.assertIn('thumbnails_default', channel_data)
        self.assertIn('country', channel_data)
        self.assertIn('all_video_upload_playlist_id', channel_data)
        self.assertIn('views_count', channel_data)
        self.assertIn('video_count', channel_data)
        self.assertIn('subs_count', channel_data)
        self.assertIn('hidden_sub', channel_data)
        self.assertIn('topic', channel_data)
        expected_item = {
            'title': 'Cecilia Lieberia Ch.『 Re:Memories 』', 
            'owner_urls': 'http://www.youtube.com/@CeciliaLieberia', 
            'custom_id': '@cecilialieberia',
            'country':'ID',
            'channel_name':'Cecilia Lieberia Ch.『 Re:Memories 』',
            'channel_url': 'https://www.youtube.com/channel/UC4pEixMozb6UnOtwg5Uew-Q',
            }

        for key, value in expected_item.items():
            self.assertEqual(channel_data[key], value)
        channel_id = 'UC4pEixMozb6UnOtwg5Uew-Q'
        channel_data = self.instance.scrape_channel_basic_data(channel_id)

        # Assert basic data is retrieved (modify as needed)
        self.assertIsNotNone(channel_data)
        self.assertIn('title', channel_data)
        self.assertIn('description', channel_data)
        self.assertIn('custom_id', channel_data)
        self.assertIn('date_created(UTC)', channel_data)
        self.assertIn('thumbnails_default', channel_data)
        self.assertIn('country', channel_data)
        self.assertIn('all_video_upload_playlist_id', channel_data)
        self.assertIn('views_count', channel_data)
        self.assertIn('video_count', channel_data)
        self.assertIn('subs_count', channel_data)
        self.assertIn('hidden_sub', channel_data)
        self.assertIn('topic', channel_data)
        for key, value in expected_item.items():
            self.assertEqual(channel_data[key], value)
        
    def test_basic_data_invalid(self):
        channel_id = '@cecilialieberia_inveliss3t1sg35u'
        with self.assertRaises(HTTPError):
            self.instance.scrape_channel_basic_data(channel_id)
    def test_valid_duration_with_hours_minutes_seconds(self):
        duration_str = "PT1H2M3S"
        expected_duration = 3723
        parsed_duration = self.instance.parse_duration(duration_str)
        self.assertEqual(parsed_duration, expected_duration)
    
    def test_valid_duration_with_minutes_seconds(self):
        duration_str = "PT5M10S"
        expected_duration = 310
        parsed_duration = self.instance.parse_duration(duration_str)
        self.assertEqual(parsed_duration, expected_duration)
      
    def test_valid_duration_with_seconds(self):
        duration_str = "PT15S"
        expected_duration = 15
        parsed_duration = self.instance.parse_duration(duration_str)
        self.assertEqual(parsed_duration, expected_duration)
      
    def test_invalid_duration_format(self):
        duration_str = "invalid_format"
        expected_duration = 0
        parsed_duration = self.instance.parse_duration(duration_str)
        self.assertEqual(parsed_duration, expected_duration)
        
    def test_valid_iso_string_with_utc(self):
        iso_string = "2024-06-20T14:30:00Z"
        expected_datetime = datetime(year=2024, month=6, day=20, hour=14, minute=30, second=0, tzinfo=timezone.utc)
        converted_datetime = self.instance.convert_to_datetime(iso_string)
        self.assertEqual(converted_datetime, expected_datetime)

    def test_empty_string(self):
        iso_string = None
        expected_datetime = None
        converted_datetime = self.instance.convert_to_datetime(iso_string)
        self.assertEqual(converted_datetime, expected_datetime)

    def test_scrape_search_video_column_names_and_data_types(self):
        for i in ['completed','live','upcoming']:
            data = self.instance.scrape_search_video(q="vtuber", regionCode="ID",max_data=50,event_type=i)
            expected_column_names = [
                'keyword', 'ranking', 'video_id', 'date_video_published(UTC)',
                'video_title', 'video_description', 'video_thumbnail',
                'video_default_audio_language', 'video_status', 'video_duration(s)',
                'video_licenced_content', 'video_tag', 'video_view_count',
                'video_like_count', 'video_favorite_count', 'video_comment_count',
                'is_video_for_kids', 'video_topic_id', 'video_topic',
                'video_start_time(UTC)', 'video_end_time(UTC)', 'video_scheduled_time(UTC)',
                'channel_id', 'channel_title', 'date_channel_create(UTC)',
                'channel_country', 'channel_all_video_upload_playlist_id',
                'channel_url', 'channel_owner_url', 'channel_description',
                'channel_custom_id', 'channel_tag', 'is_channel_Family_safe',
                'is_channel_hiden_sub', 'channel_topic', 'channel_view_count',
                'channel_video_count', 'channel_subs_count'
            ]
            self.assertListEqual(list(data.columns), expected_column_names)
            expected_numeric_cols = [
                'ranking', 'video_duration(s)', 'video_view_count', 'video_like_count',
                'video_favorite_count', 'video_comment_count', 'channel_view_count',
                'channel_video_count', 'channel_subs_count'
            ]
            
            
            expected_datetime_cols = [
                'date_video_published(UTC)', 'video_start_time(UTC)',
                'video_end_time(UTC)', 'video_scheduled_time(UTC)','date_channel_create(UTC)'
            ]
            for col in expected_numeric_cols:
                self.assertTrue(pd.api.types.is_numeric_dtype(data[col]))
            for cols in expected_datetime_cols:    
                self.assertTrue(isinstance(data[cols].dtype, pd.DatetimeTZDtype))
            time.sleep(6)
        with self.assertRaises(ValueError):
            self.instance.scrape_search_video(q="vtuber", regionCode="ID",max_data=50,event_type='invalid_input')
        
            
    def test_scrape_search_video_invalid_max_data(self):
        with self.assertRaises(ValueError):
            self.instance.scrape_search_video(q="vtuber", regionCode="ID",max_data=9904550)
        
        
    def test_scrape_search_video_invalid_max_data_str(self):
        with self.assertRaises(TypeError):
            self.instance.scrape_search_video(q="vtuber", regionCode="ID",max_data='INVALID_INPUT')
    
    def test_scrape_search_video_invalid_publishedAfter(self):
        with self.assertRaises(ValueError):
            self.instance.scrape_search_video(q="vtuber", regionCode="ID",max_data=50,publishedAfter='sssdvsfwas')
        with self.assertRaises(ValueError):
            self.instance.scrape_search_video(q="vtuber", regionCode="ID",max_data=50,publishedAfter='2024-31-01')
        with self.assertRaises(ValueError):
            self.instance.scrape_search_video(q="vtuber", regionCode="ID",max_data=50,publishedAfter="2024-06-20T00:00:00Z")
        with self.assertRaises(ValueError):
            self.instance.scrape_search_video(q="vtuber", regionCode="ID",max_data=50,publishedBefore='sssdvsfwas')
        with self.assertRaises(ValueError):
            self.instance.scrape_search_video(q="vtuber", regionCode="ID",max_data=50,publishedBefore='2024-31-01')
        with self.assertRaises(ValueError):
            self.instance.scrape_search_video(q="vtuber", regionCode="ID",max_data=50,publishedBefore="2024-06-20T00:00:00Z")
       
    
    
    def test_valid_date(self):
        self.assertEqual(self.instance.validate_date("2024-06-20"), "2024-06-20T00:00:00Z")

    def test_invalid_date_format(self):
        with self.assertRaises(ValueError) as context:
            self.instance.validate_date("20-06-2024")
        self.assertEqual(str(context.exception), "Format date invalid. use format yyyy-mm-dd.")
    
    def test_invalid_date_format1(self):
        with self.assertRaises(ValueError) as context:
            self.instance.validate_date("2024/06/24")
        self.assertEqual(str(context.exception), "Format date invalid. use format yyyy-mm-dd.")

    def test_empty_date_string(self):
        with self.assertRaises(ValueError) as context:
            self.instance.validate_date("")
        self.assertEqual(str(context.exception), "Format date invalid. use format yyyy-mm-dd.")

    def test_invalid_date_value(self):
        with self.assertRaises(ValueError) as context:
            self.instance.validate_date("2024-02-30")
        self.assertEqual(str(context.exception), "Format date invalid. use format yyyy-mm-dd.")

    def test_non_string_input(self):
        with self.assertRaises(TypeError) as context:
            self.instance.validate_date(20240620)
        self.assertEqual(str(context.exception), "Format date invalid. use format yyyy-mm-dd in string not integer.")

    def test_scrape_video_data(self):
       valid_video_id = 'mIP5nRNCI6c'
       valid_video_id_list = ['mIP5nRNCI6c','T2tN4EJgXYE']
       expected_columns = [
           'published_date','channel_id','channel_title','video_title',
           'description','thumbnail_url','video_tag','categoryId',
           'defaultAudioLanguage','duration(s)','licensed_content','status',
           'for_kids','view_count','like_count','favorite_count',
           'comment_count','topic_category','start_time(UTC)','end_time(UTC)',
           'scheduled_time(UTC)']
       expected_num_columns = [
           'duration(s)','view_count','like_count','favorite_count',
           'comment_count'
           ]
       expected_date_columns = [
           'published_date','start_time(UTC)','end_time(UTC)',
           'scheduled_time(UTC)'
           ]
       data = self.instance.scrape_video_data(valid_video_id)
       self.assertEqual(data.shape[0], 1)
       self.assertListEqual(list(data.columns), expected_columns)
       for col in expected_num_columns:
           self.assertTrue(pd.api.types.is_numeric_dtype(data[col]))
       for cols in expected_date_columns:    
           self.assertTrue(isinstance(data[cols].dtype, pd.DatetimeTZDtype))
       #---------------------
       data = self.instance.scrape_video_data(valid_video_id_list)
       self.assertEqual(data.shape[0], 2)
       self.assertListEqual(list(data.columns), expected_columns)
       for col in expected_num_columns:
           self.assertTrue(pd.api.types.is_numeric_dtype(data[col]))
       for cols in expected_date_columns:    
           self.assertTrue(isinstance(data[cols].dtype, pd.DatetimeTZDtype))


    def test_valid_playlist_item(self): 
        playlist_id = "UUXyGmdCo1owxgyQsAHT4iPA" 
        video_list = self.instance.scrape_playlist_item(playlist_id) 
        self.assertIsInstance(video_list, list)
       
    def test_invalid_id_playlist_item(self): 
        playlist_id = "INVALID_ID"  
        with self.assertRaises(HTTPError): 
            self.instance.scrape_playlist_item(playlist_id)
    
    def test_int_invalid_id_playlist_item(self): 
        playlist_id = 123  # Invalid playlist ID (should be string) 
        with self.assertRaises(TypeError): 
            self.instance.scrape_playlist_item(playlist_id)
    
    def test_int_invalid_list_id_playlist_item(self): 
        playlist_id = [123,'dg',12]  # Invalid playlist ID (should be string) 
        with self.assertRaises(TypeError): 
            self.instance.scrape_playlist_item(playlist_id)
            
    def test_int_playlist_item_invalid_list(self): 
        playlist_id = ['123','lop',9,62]  # Invalid playlist ID (should be string) 
        with self.assertRaises(TypeError): 
            self.instance.scrape_video_data(playlist_id)
            
    def test_int_playlist_item_invalid_list_1(self): 
        playlist_id = ['123','lop','9','62']  # Invalid playlist ID (should be string) 
        with self.assertRaises(ValueError): 
            self.instance.scrape_video_data(playlist_id)
    
    def test_int_playlist_item_invalid_id(self): 
        playlist_id = 12  # Invalid playlist ID (should be string) 
        with self.assertRaises(TypeError): 
            self.instance.scrape_video_data(playlist_id)
            
    def test_scrape_search_channel_invalid_max_data(self):
        with self.assertRaises(ValueError):
            self.instance.scrape_search_channel(q="vtuber", regionCode="ID",max_data=9904550)
        expected_columns = [
            'keyword', 'ranking', 'date_channel_create(UTC)', 'channel_country',
            'channel_all_video_upload_playlist_id', 'channel_url',
            'channel_owner_url', 'channel_description', 'channel_custom_id',
            'channel_tag', 'is_channel_Family_safe', 'is_channel_hiden_sub',
            'channel_topic', 'channel_view_count', 'channel_video_count',
            'channel_subs_count']
        expected_num_col = ['ranking','channel_view_count','channel_video_count','channel_subs_count']
        expected_date_col = ['date_channel_create(UTC)']
        data = self.instance.scrape_search_channel(q="vtuber", regionCode="ID",max_data=50)
        self.assertListEqual(list(data.columns), expected_columns)
        for col in expected_num_col:
            self.assertTrue(pd.api.types.is_numeric_dtype(data[col]))
        for cols in expected_date_col:    
            self.assertTrue(isinstance(data[cols].dtype, pd.DatetimeTZDtype))
        



if __name__ == '__main__':
    unittest.main()