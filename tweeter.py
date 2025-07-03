import tweepy
import os
import time
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from parser import InshortsParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class SummaryTweeter:
    def __init__(self):
        load_dotenv()  # Load env first
        self._validate_credentials()
        self.client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
            consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        self.parser = InshortsParser(max_news=20)
        self.rate_limit_reset = None

    def _validate_credentials(self):
        """Validate all required credentials exist"""
        required = [
            "TWITTER_CONSUMER_KEY",
            "TWITTER_CONSUMER_SECRET",
            "TWITTER_ACCESS_TOKEN", 
            "TWITTER_ACCESS_TOKEN_SECRET"
        ]
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing credentials: {', '.join(missing)}")

    def tweet_summaries(self):
        """Main tweeting method with rate limit handling"""
        try:
            summaries = self.parser.fetch_summaries()
            logger.info(f"Starting tweet sequence for {len(summaries)} summaries")
            
            for idx, summary in enumerate(summaries, 1):
                while True:  # Retry loop
                    try:
                        self._tweet_single(summary, idx, len(summaries))
                        time.sleep(15)  # 15-second buffer between tweets
                        break
                        
                    except tweepy.errors.TooManyRequests as e:
                        self._handle_rate_limit(e)
                    except Exception as e:
                        logger.error(f"Tweet {idx} failed: {str(e)}")
                        break
                        
        except Exception as e:
            logger.critical(f"Tweet sequence aborted: {str(e)}")
        finally:
            logger.info("Tweet sequence completed")

    def _tweet_single(self, summary, idx, total):
        """Handle single tweet attempt"""
        tweet_text = summary[:277] + "..." if len(summary) > 280 else summary
        response = self.client.create_tweet(text=tweet_text)
        logger.info(
            f"Tweet {idx}/{total} posted | "
            f"ID: {response.data['id']} | "
            f"Content: {tweet_text[:50]}..."
        )

    def _handle_rate_limit(self, error):
        """Calculate and wait for rate limit reset"""
        reset_time = datetime.fromtimestamp(int(error.response.headers.get('x-rate-limit-reset', 0)))
        wait_seconds = max(0, (reset_time - datetime.now()).total_seconds() + 10)  # 10-second buffer
        
        logger.warning(
            f"Rate limit exceeded. Waiting {wait_seconds//60} minutes "
            f"(until {reset_time.strftime('%H:%M:%S')})"
        )
        
        time.sleep(wait_seconds)
        logger.info("Resuming tweet sequence")

if __name__ == "__main__":
    try:
        logger.info("Starting Twitter bot with rate limit protection")
        bot = SummaryTweeter()
        bot.tweet_summaries()
    except Exception as e:
        logger.critical(f"Application failed to start: {str(e)}")
