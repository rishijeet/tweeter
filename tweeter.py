import tweepy
import os
import time
from dotenv import load_dotenv
from parser import fetch_inshorts_tech_headlines  # Import the new function

load_dotenv()

def tweet_headlines(client, headlines):
    """Tweet each headline as a standalone post."""
    for i, headline in enumerate(headlines, 1):
        try:
            client.create_tweet(text=headline)
            print(f"Tweeted {i}: {headline}")
            time.sleep(2.5)  # Avoid rate limits
        except tweepy.errors.Forbidden as e:
            print(f"Skipped (Twitter blocked): {headline}\nError: {e}")
            continue

def main():
    # Initialize Twitter Client
    client = tweepy.Client(
        consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
        consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    )
    
    # Fetch and tweet headlines
    headlines = fetch_inshorts_tech_headlines()
    print(f"Fetched {len(headlines)} headlines. Starting to tweet...")
    tweet_headlines(client, headlines)

if __name__ == "__main__":
    main()
