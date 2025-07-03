import requests
from bs4 import BeautifulSoup
import re

class InshortsParser:
    def __init__(self, max_news=20):
        self.base_url = "https://www.inshorts.com/en/read/technology"
        self.max_news = max_news
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.inshorts.com/en/read/technology'
        }

    def fetch_headlines(self):
        """Fetch headlines with proper load more simulation"""
        headlines = []
        news_offset = None
        attempt = 0
        
        while len(headlines) < self.max_news and attempt < 3:
            try:
                # First page or subsequent AJAX calls
                if not news_offset:
                    response = self.session.get(self.base_url)
                else:
                    response = self.session.post(
                        "https://www.inshorts.com/en/ajax/more_news",
                        data={"category": "technology", "news_offset": news_offset}
                    )
                
                response.raise_for_status()
                data = response.json() if news_offset else {'html': response.text}
                
                # Parse headlines
                soup = BeautifulSoup(data['html'], 'html.parser')
                new_headlines = [
                    h.text.strip() 
                    for h in soup.find_all('span', itemprop='headline')
                    if h and h.text.strip()
                ]
                headlines.extend(new_headlines)
                
                print(f"Batch {attempt + 1}: Added {len(new_headlines)} headlines (Total: {len(headlines)})")
                
                # Update offset for next request
                script = soup.find('script', string=re.compile('min_news_id'))
                if script:
                    match = re.search(r'min_news_id\s*=\s*"(.*?)"', script.string)
                    news_offset = match.group(1) if match else None
                
                attempt += 1
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                break
                
        return headlines[:self.max_news]

if __name__ == "__main__":
    print("Fetching latest technology headlines...")
    parser = InshortsParser(max_news=20)
    headlines = parser.fetch_headlines()
    
    print(f"\nFinal Results ({len(headlines)} headlines):")
    for idx, headline in enumerate(headlines, 1):
        print(f"{idx}. {headline}")
    
    if len(headlines) < 20:
        print(f"\nNote: Only {len(headlines)} headlines were available")
