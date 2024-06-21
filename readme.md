# YTScrapy
This script provides a class and its associated methods for performing 
data mining on YouTube using the "Try Feature" of the YouTube Data API v3.\
The script does not require an API key to make data retrieval requests.\

## How to use:\
### Importing Script:\
'''python
from YT_Scrapy import YtScraper

scraper_obj = YTScraper()
'''
### The class offers methods for:
#### Basic Channel Data:\
Retrieves basic information about a YouTube channel, including channel ID, title, description, and subscriber count.\
Takes a string containing a YouTube channel ID as input and returns a dictionary. Raises an error if the channel ID is invalid.\
Accepts YouTube channel IDs in two formats:\
1. @channel_id (usually found in the address bar of a browser)
2. usc49qumsn14md (usually found in the HTML block)
**[sample data](https://github.com/ekasetyo090/YT_Scrapy/blob/ece98b673238e2c26e4df0a812f3dcfe49700509/sample%20data/channel_basic_data.json)**

'''python
from YT_Scrapy import YtScraper

scraper_obj = YTScraper()
data = scraper_obj.scrape_channel_basic_data(
channel_id # string of youtube channel
)
'''
#### Video Data:\ 
Retrieves detailed information about a YouTube video, including view count, comment count, likes, dislikes, and publishing date.
#### Video Search:\
Searches for YouTube videos based on a user-defined query and retrieves basic information about the top results.
#### Channel Search:\
Searches for YouTube channels based on a user-defined query and retrieves basic information about the top results.