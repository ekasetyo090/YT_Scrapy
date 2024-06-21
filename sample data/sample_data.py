# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 08:45:12 2024

@author: snsv
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scraper')))

import json

from YT_Scrapy import YtScraper

scraper = YtScraper()
df_channel = scraper.scrape_channel_basic_data('@cecilialieberia')
df_channel['date_created(UTC)'] = df_channel['date_created(UTC)'].isoformat()
json_data = json.dumps(df_channel)
print(df_channel)
# Save the JSON data to a file
with open('channel_basic_data.json', 'w') as outfile:
    outfile.write(json_data)
    
list_video_id = scraper.scrape_playlist_item(df_channel['all_video_upload_playlist_id'])
df_video = scraper.scrape_video_data(list_video_id)
df_video_search = scraper.scrape_search_video(q='vtuber',regionCode='ID',max_data=50)
df_channel_search = scraper.scrape_search_channel(q='vtuber',regionCode='ID',max_data=50)

#----to csv----


df_video.to_csv('channel all upload video data.csv',index=False)
df_video_search.to_csv('search video data.csv',index=False)
df_channel_search.to_csv('search channel data.csv',index=False)

