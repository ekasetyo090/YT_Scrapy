# YTScrapy
YT_Scrapy is a Python script that empowers users to perform data mining on YouTube using the "Try Feature" of the YouTube Data API v3. This script eliminates the need for an API key, making it a valuable tool for researchers, developers, and anyone interested in extracting insights from YouTube.

At its core, YT_Scrapy provides a class and its associated methods that leverage the "Try Feature" to retrieve data from YouTube. This feature enables users to bypass the traditional API key requirement, allowing for unrestricted data retrieval. As a result, YT_Scrapy offers several advantages over traditional data mining methods:

1. No API Key Required: Eliminate the need for an API key, making it accessible to a broader audience.
2. Unrestricted Data Retrieval: Conduct data mining without limitations imposed by API quotas.
3. Accurate Data Collection: Utilize the official YouTube Data API to ensure data accuracy and reliability.

* [Basic Channel Data](#basic-channel-data)
* [Playlist Item](#playlist-item)
* [Video Data](#video-data)
* [Video Search](#video-search)
* [Channel Search](#channel-search)


## How to use:
### Importing Script:
```python
from YT_Scrapy import YtScraper

scraper_obj = YTScraper()
```
### The class offers methods for:
#### Basic Channel Data:
Retrieves basic information about a YouTube channel, including channel ID, title, description, and subscriber count.\
Takes a string containing a YouTube channel ID as input and returns a dictionary. Raises an error if the channel ID is invalid.\
Accepts YouTube channel IDs in two formats:

1. @channel_id (usually found in the address bar of a browser)
2. usc49qumsn14md (usually found in the HTML block)

**[sample data](https://github.com/ekasetyo090/YT_Scrapy/blob/ece98b673238e2c26e4df0a812f3dcfe49700509/sample%20data/channel_basic_data.json)**

```python
from YT_Scrapy import YtScraper

scraper_obj = YTScraper()
data = scraper_obj.scrape_channel_basic_data(
channel_id # string of youtube channel
)
```
#### Playlist Item:
Retrieves list of video ID that contained in playlist ID.
Takes a string of playlist ID as input and returns a list contain video ID.

```python
from YT_Scrapy import YtScraper

scraper_obj = YTScraper()
data = scraper_obj.scrape_playlist_item(
playlist_id # string of playlist ID
) # return list contain video ID
```
#### Video Data:
Retrieves detailed information about a YouTube video, including view count, comment count, likes, dislikes, and publishing date.
Takes a string or list containing a YouTube video ID as input and returns a pandas dataframe.

**[sample data](https://github.com/ekasetyo090/YT_Scrapy/blob/ece98b673238e2c26e4df0a812f3dcfe49700509/sample%20data/channel%20all%20upload%20video%20data.csv)**

```python
from YT_Scrapy import YtScraper

scraper_obj = YTScraper()
data = scraper_obj.scrape_video_data(
video_id # a string or list containing a YouTube video ID
)
```
#### Video Search:
Searches for YouTube videos based on a user-defined query and retrieves basic information about the top results base on relevancy.

**[sample data](https://github.com/ekasetyo090/YT_Scrapy/blob/ece98b673238e2c26e4df0a812f3dcfe49700509/sample%20data/search%20video%20data.csv)**

```python
from YT_Scrapy import YtScraper

scraper_obj = YTScraper()
data = scraper_obj.scrape_search_video(
q, # string of user define query related to video
regionCode, # string of iso 2 alpha region code
publishedAfter, # string of date time yyyy-mm-dd
publishedBefore,# string of date time yyyy-mm-dd
max_data, #int of max data retrive default: 100, maximum:10,000
event_type # string of event type ['completed','live','upcoming']
) # return pandas dataframe:
```
#### Channel Search:
Searches for YouTube channels based on a user-defined query and retrieves basic information about the top results.

**[sample data](https://github.com/ekasetyo090/YT_Scrapy/blob/ece98b673238e2c26e4df0a812f3dcfe49700509/sample%20data/search%20channel%20data.csv)**

```python
from YT_Scrapy import YtScraper

scraper_obj = YTScraper()
data = scraper_obj.scrape_search_channel(
q, # string of user define query related to video
regionCode, # string of iso 2 alpha region code
publishedAfter,# string of date time yyyy-mm-dd
publishedBefore,# string of date time yyyy-mm-dd
max_data #int of max data retrive default: 100, maximum:10,000
) # return pandas dataframe:
```