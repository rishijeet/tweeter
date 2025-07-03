import tweepy
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from parser import InshortsParser  # Make sure parser.py is in same directory

load_dotenv()

class SummaryTweeter:
    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
            consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        self.parser = InshortsParser(max_news=20)
        self.log_file = "tweet_log.txt"

    def _log_tweet(self, status, summary, tweet_num, total):
        """Log each tweet attempt with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (
            f"[{timestamp}] Tweet {tweet_num}/{total} - {status}\n"
            f"Content: {summary[:100]}...\n"
            f"{'-'*50}\n"
        )
        with open(self.log_file, "a") as f:
            f.write(log_entry)
        print(log_entry)

    def tweet_summaries(self):
        """Tweet summaries with delays and logging"""
        try:
            summaries = self.parser.fetch_summaries()
            total = len(summaries)
            print(f"Starting tweet sequence for {total} summaries")
            
            for idx, summary in enumerate(summaries, 1):
                tweet_text = summary[:277] + "..." if len(summary) > 280 else summary
                
                try:
                    # Tweet and log success
                    self.client.create_tweet(text=tweet_text)
                    self._log_tweet("SUCCESS", tweet_text, idx, total)
                    
                    # Wait 10 seconds unless it's the last tweet
                    if idx < total:
                        time.sleep(10)
                        
                except tweepy.errors.Forbidden as e:
                    self._log_tweet(f"BLOCKED - {str(e)}", tweet_text, idx, total)
                except tweepy.errors.TooManyRequests:
                    self._log_tweet("RATE LIMITED - Waiting 15 minutes", tweet_text, idx, total)
                    time.sleep(5)
                except Exception as e:
                    self._log_tweet(f"ERROR - {str(e)}", tweet_text, idx, total)
                    
        except Exception as e:
            error_msg = f"Critical failure: {str(e)}"
            print(error_msg)
            with open(self.log_file, "a") as f:
                f.write(error_msg)

if __name__ == "__main__":
    print("Starting Twitter bot with 10-second delays")
    bot = SummaryTweeter()
    bot.tweet_summaries()
    print("Tweet sequence completed. Check tweet_log.txt for details")
