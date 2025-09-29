import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class Bot:
    """
    A bot that scrapes the top stories from Hacker News
    """
    name = "hackernews_top"
    description = "Fetches the top stories from Hacker News"
    author = "Scraping Station"
    version = "1.0.0"

    def __init__(self):
        self.base_url = "https://news.ycombinator.com"
        self.output_dir = "data/hackernews"
        
    def run(self, limit: int = 10):
        """
        Fetch top stories from Hacker News
        :param limit: Number of stories to fetch (default: 10)
        """
        try:
            # Create output directory if it doesn't exist
            import os
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Fetch the homepage
            response = requests.get(self.base_url)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all story rows
            stories = []
            rows = soup.select('tr.athing')
            
            for row in rows[:limit]:
                title_elem = row.select_one('span.titleline > a')
                if not title_elem:
                    continue
                    
                title = title_elem.text
                url = title_elem['href']
                
                # Get score and comments
                next_row = row.find_next_sibling('tr')
                score_elem = next_row.select_one('span.score')
                score = int(score_elem.text.split()[0]) if score_elem else 0
                
                # Get number of comments
                links = next_row.find_all('a')
                comments_link = next((a for a in links if 'comment' in a.text.lower()), None)
                num_comments = 0
                if comments_link and comments_link.text.strip():
                    num_comments = int(comments_link.text.split()[0])
                
                stories.append({
                    'title': title,
                    'url': url,
                    'score': score,
                    'comments': num_comments,
                    'scraped_at': datetime.utcnow().isoformat()
                })
            
            # Save results
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_file = f"{self.output_dir}/top_stories_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump({
                    'source': 'Hacker News',
                    'scraped_at': datetime.utcnow().isoformat(),
                    'stories': stories
                }, f, indent=2)
            
            print(f"Successfully scraped {len(stories)} stories. Saved to {output_file}")
            return {"status": "success", "stories_found": len(stories), "output_file": output_file}
            
        except Exception as e:
            print(f"Error scraping Hacker News: {e}")
            return {"status": "error", "error": str(e)}
            
    def analyze(self, data):
        """Analyze the scraped data"""
        if not data or 'stories' not in data:
            return "No data to analyze"
            
        stories = data['stories']
        if not stories:
            return "No stories found in the data"
            
        # Basic analysis
        total_score = sum(story.get('score', 0) for story in stories)
        avg_score = total_score / len(stories) if stories else 0
        
        return {
            "total_stories": len(stories),
            "total_score": total_score,
            "average_score": round(avg_score, 2),
            "top_story": max(stories, key=lambda x: x.get('score', 0)) if stories else None
        }
