# Inshorts Headline Tweeter

A Python script to fetch headlines from Inshorts' startup section and tweet them with relevant hashtags.

## Features
- Fetches headlines from Inshorts using their AJAX API.
- Formats headlines to fit Twitter's character limit (270 chars + hashtags).
- Tweets headlines one by one with a 2-second delay to avoid rate limits.
- Supports dual-mode parsing (headlines or summaries) via `parser.py`.


## Files
- `parser.py`: Fetches and formats headlines/summaries from Inshorts.
- `tweeter.py`: Tweets the fetched headlines.

## Author
**Rishijeet Mishra** 