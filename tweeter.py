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

def format_for_tweet(post):
    tweet = f"{post['headline']}\n\n{post['summary']}"
    return tweet[:277] + "..." if len(tweet) > 280 else tweet

def main():
    posts = fetch_inshorts_tech_posts()
    print(f"Number of posts fetched: {len(posts)}")
    for i, post in enumerate(posts, 1):
        print(f"Tweet {i}:\n{format_for_tweet(post)}\n{'-'*50}\n")

if __name__ == "__main__":
    main()
