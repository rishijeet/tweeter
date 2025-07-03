import tweepy
import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from parser import InshortsParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Log to console
    ]
)
logger = logging.getLogger(__name__)

class SummaryTweeter:
    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
            consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        self.parser = InshortsParser(max_news=20)

    def tweet_summaries(self):
        """Tweet summaries with delays and proper logging"""
        try:
            summaries = self.parser.fetch_summaries()
            total = len(summaries)
            logger.info(f"Starting tweet sequence for {total} summaries")
            
            for idx, summary in enumerate(summaries, 1):
                tweet_text = summary[:277] + "..." if len(summary) > 280 else summary
                
                try:
                    # Send tweet
                    result = self.client.create_tweet(text=tweet_text)
                    tweet_id = result.data['id']
                    
                    logger.info(
                        f"Tweet {idx}/{total} SUCCESS | "
                        f"ID: {tweet_id} | "
                        f"Content: {tweet_text[:50]}..."
                    )
                    
                    # 10-second delay unless last tweet
                    if idx < total:
                        time.sleep(10)
                        
                except tweepy.errors.Forbidden as e:
                    logger.warning(f"Tweet {idx}/{total} BLOCKED - {str(e)}")
                except tweepy.errors.TooManyRequests:
                    logger.warning("Rate limit hit - waiting 15 minutes")
                    time.sleep(15 * 60)
                except Exception as e:
                    logger.error(f"Tweet {idx}/{total} FAILED - {str(e)}")
                    
        except Exception as e:
            logger.critical(f"Fatal error in tweet sequence: {str(e)}")
            raise

if __name__ == "__main__":
    logger.info("Starting Twitter bot with 10-second delays")
    bot = SummaryTweeter()
    bot.tweet_summaries()
    logger.info("Tweet sequence completed successfully")
