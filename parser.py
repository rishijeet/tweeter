import requests
from bs4 import BeautifulSoup

def fetch_inshorts_tech_posts():
    url = "https://inshorts.com/en/read/technology"
    
    # Fetch the page content
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch page: HTTP {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    news_cards = soup.find_all('div', class_='PmX01nT74iM8UNAIENsC')
    
    posts = []
    for item in news_cards[:20]:  # Limit to 20 posts
        headline = item.find('span', class_='ddVzQcwl2yPlFt4fteIE') or item.find('h2')
        summary = item.find('div', class_='KkupEonoVHxNv4A_D7UG') or item.find('div', itemprop='articleBody')
        
        posts.append({
            "headline": headline.text.strip() if headline else "No headline found",
            "summary": summary.text.strip() if summary else "No summary found"
        })
    
    return posts

def split_text(text, max_length=280):
    """Split text into chunks of max_length characters."""
    chunks = []
    while text:
        chunk = text[:max_length]
        chunks.append(chunk)
        text = text[max_length:]
    return chunks

def format_for_tweet_thread(post):
    """Format a post into a thread of tweets."""
    thread = []
    thread.append(post['headline'])  # First tweet: headline
    thread.extend(split_text(post['summary']))  # Split summary into chunks
    return thread

def main():
    """Test the parser functions independently."""
    print("Testing parser.py...\n")
    
    # Test fetching posts
    posts = fetch_inshorts_tech_posts()
    print(f"Fetched {len(posts)} posts.")
    
    if not posts:
        print("No posts fetched. Check the HTML structure or network.")
        return
    
    # Display the first 3 posts as an example
    for i, post in enumerate(posts[:3], 1):
        print(f"\nPost {i}:")
        print(f"Headline: {post['headline']}")
        print(f"Summary: {post['summary']}")
        
        # Test thread formatting
        thread = format_for_tweet_thread(post)
        print(f"\nFormatted Thread (Length: {len(thread)} tweets):")
        for j, tweet in enumerate(thread, 1):
            print(f"  Tweet {j}: {tweet[:50]}...")  # Preview first 50 chars

if __name__ == "__main__":
    main()
