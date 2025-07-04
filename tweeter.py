"""
Inshorts Headline Tweeter - Tweets fetched headlines from Inshorts.
Author: Rishijeet Mishra
"""

import tweepy
import os
import time
import logging
from dotenv import load_dotenv
from parser import InshortsParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class HeadlineTweeter:
    def __init__(self):
        load_dotenv()  # Load environment variables
        self._validate_credentials()
        self.client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
            consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        self.parser = InshortsParser(max_news=20)

    def _validate_credentials(self):
        """Ensure all required Twitter API credentials are set."""
        required_keys = [
            "TWITTER_CONSUMER_KEY",
            "TWITTER_CONSUMER_SECRET",
            "TWITTER_ACCESS_TOKEN",
            "TWITTER_ACCESS_TOKEN_SECRET"
        ]
        missing = [key for key in required_keys if not os.getenv(key)]
        if missing:
            raise ValueError(f"Missing Twitter API credentials: {', '.join(missing)}")

    def tweet_headlines(self):
        """Fetch headlines and tweet them one by one with a 2-second delay."""
        headlines = self.parser.fetch_content(content_type='headline')
        if not headlines:
            logger.error("No headlines fetched. Exiting.")
            return

        logger.info(f"Fetched {len(headlines)} headlines. Starting to tweet...")
        for idx, headline in enumerate(headlines, 1):
            try:
                response = self.client.create_tweet(text=headline)
                logger.info(f"Tweeted headline {idx}/{len(headlines)}: {headline[:50]}...")
                time.sleep(2)  # 2-second delay between tweets
            except tweepy.errors.Forbidden as e:
                logger.error(f"Skipping tweet (blocked by Twitter): {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Failed to tweet: {str(e)}")
                break

if __name__ == "__main__":
    try:
        tweeter = HeadlineTweeter()
        tweeter.tweet_headlines()
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
