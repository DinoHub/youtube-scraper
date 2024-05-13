# YouTube Scraper

This repository contains the scripts to scrape YouTube videos. As there are possibly many different use cases for scraping, please use the respective branches for different use cases.

1. Machine Translation Branch (mt-subtitles)
To scrape paired subtitles of English - X (where X is another language)
```sh
git checkout mt-subtitles
```

2. Installing Requirements
```sh
pip install -r requirements.txt
```

3. Installing External Libraries (ffmpeg)
Ubuntu
```sh
sudo apt-get install ffmpeg
```
macOS
```sh
brew install ffmpeg
```

## MT Subtitles
This Branch is the MT Subtitle Branch. Follow the steps below to scrape subtitles!

1. Add youtube URLs to `to_scrape_ids.txt`.
2. Run `get_id.py` to obtain the IDs of the youtube URLs in `to_scrape_ids.txt`.
```
python3 get_id.py
```
3. Check if subtitles exist.
```
python3 retrieve_subtitle_exists.py en to_scrape_ids.txt

# viet
python3 retrieve_subtitle_exists.py vi to_scrape_ids.txt
```
4. Download subtitles and audio files.
```
python3 download_video.py en sub/en/to_scrape_ids.csv

# viet
python3 download_video.py vi sub/vi/to_scrape_ids.csv
```
5. Remove subfolders that are empty and subfolders where the text files of the same name have mismatched number of rows from all folders. Move filtered subfolders to a separate directory.
```
python3 filter_and_move_files.py
```
