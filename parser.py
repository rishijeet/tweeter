"""
Inshorts Parser - Fetches and formats headlines/summaries from Inshorts.
Author: Rishijeet Mishra
"""

import requests
from bs4 import BeautifulSoup
import re
import argparse

class InshortsParser:
    def __init__(self, max_news=20):
        self.base_url = "https://www.inshorts.com/en/read/startup"
        self.max_news = max_news
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.inshorts.com/en/read/startup'
        }

    def _generate_hashtags(self, text):
        """Generate relevant hashtags based on content"""
        hashtags = []
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['ai', 'artificial intelligence']):
            hashtags.extend(['#AI', '#ArtificialIntelligence'])
        if 'startup' in text_lower:
            hashtags.append('#Startup')
        if any(word in text_lower for word in ['funding', 'invest', 'venture']):
            hashtags.extend(['#Funding', '#VentureCapital'])
        if any(word in text_lower for word in ['tech', 'technology']):
            hashtags.append('#Tech')
            
        hashtags.extend(['#Business', '#News'])
        return ' '.join(sorted(set(hashtags), key=lambda x: len(x)))

    def _format_content(self, text, is_headline=False):
        """Format content to 270 chars + hashtags"""
        max_len = 270 - 30 if is_headline else 270  # Headlines get extra space
        truncated = (text[:max_len-3] + '...') if len(text) > max_len else text
        hashtags = self._generate_hashtags(text)
        return f"{truncated}\n\n{hashtags}"

    def fetch_content(self, content_type='summary'):
        """Fetch either headlines or summaries based on content_type"""
        raw_content = []
        news_offset = None
        attempt = 0
        
        while len(raw_content) < self.max_news and attempt < 3:
            try:
                # Fetch page
                if not news_offset:
                    response = self.session.get(self.base_url)
                else:
                    response = self.session.post(
                        "https://www.inshorts.com/en/ajax/more_news",
                        data={"category": "startup", "news_offset": news_offset}
                    )
                
                response.raise_for_status()
                data = response.json() if news_offset else {'html': response.text}
                
                # Parse content
                soup = BeautifulSoup(data['html'], 'html.parser')
                if content_type == 'headline':
                    new_content = [
                        h.text.strip() 
                        for h in soup.find_all('span', itemprop='headline')
                        if h and h.text.strip()
                    ]
                else:  # summary
                    new_content = [
                        s.text.strip() 
                        for s in soup.find_all('div', itemprop='articleBody')
                        if s and s.text.strip()
                    ]
                
                raw_content.extend(new_content)
                
                # Update offset
                script = soup.find('script', string=re.compile('min_news_id'))
                if script:
                    match = re.search(r'min_news_id\s*=\s*"(.*?)"', script.string)
                    news_offset = match.group(1) if match else None
                
                attempt += 1
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                break
                
        return [self._format_content(c, is_headline=(content_type=='headline')) 
               for c in raw_content[:self.max_news]]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--only-head', action='store_true', 
                       help='Fetch headlines instead of summaries')
    args = parser.parse_args()

    content_type = 'headline' if args.only_head else 'summary'
    content_label = "headlines" if args.only_head else "summaries"
    
    print(f"Fetching latest startup {content_label}...")
    inshorts = InshortsParser(max_news=20)
    results = inshorts.fetch_content(content_type)
    
    print(f"\nFinal Results ({len(results)} {content_label}):")
    for idx, item in enumerate(results, 1):
        print(f"\n{content_label[:-1].title()} {idx}:")
        print(item)
        print(f"Length: {len(item)} chars")
        print("-"*50)
    
    if len(results) < 20:
        print(f"\nNote: Only {len(results)} {content_label} were available")
