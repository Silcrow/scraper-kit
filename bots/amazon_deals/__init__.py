import requests
from bs4 import BeautifulSoup
import json
import random
from datetime import datetime
from fake_useragent import UserAgent

class Bot:
    """
    A bot that scrapes deals from Amazon
    """
    name = "amazon_deals"
    description = "Fetches deals from Amazon's Today's Deals page"
    author = "Scraping Station"
    version = "1.0.0"

    def __init__(self):
        self.base_url = "https://www.amazon.com/gp/goldbox"
        self.output_dir = "data/amazon_deals"
        self.headers = {
            'User-Agent': UserAgent().random,
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'keep-alive',
        }
        
    def get_proxy(self):
        """Get a random proxy (you should implement your own proxy rotation)"""
        # This is a placeholder - in production, use a proxy service
        return None
    
    def run(self, category=None, limit=10):
        """
        Fetch deals from Amazon's Today's Deals page
        :param category: Optional category filter
        :param limit: Maximum number of deals to fetch
        """
        try:
            # Create output directory
            import os
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Prepare the URL
            url = self.base_url
            params = {}
            if category:
                params['category'] = category
                
            # Make the request
            proxies = self.get_proxy()
            response = requests.get(
                url, 
                headers=self.headers, 
                params=params,
                proxies=proxies,
                timeout=30
            )
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find deal containers (this selector might need adjustment)
            deal_containers = soup.select('div.dealTile')
            deals = []
            
            for container in deal_containers[:limit]:
                try:
                    title_elem = container.select_one('div.dealTitle')
                    if not title_elem:
                        continue
                        
                    title = title_elem.text.strip()
                    url = title_elem.get('href', '')
                    if url and not url.startswith('http'):
                        url = f"https://www.amazon.com{url}"
                    
                    # Get price information
                    price_elem = container.select_one('span.priceBlockDealPriceString')
                    price = price_elem.text.strip() if price_elem else "Price not available"
                    
                    # Get discount
                    discount_elem = container.select_one('div.itemPriceDrop')
                    discount = discount_elem.text.strip() if discount_elem else "Discount not specified"
                    
                    # Get rating
                    rating_elem = container.select_one('i.a-icon-star')
                    rating = rating_elem.text.strip() if rating_elem else "Rating not available"
                    
                    deals.append({
                        'title': title,
                        'url': url,
                        'price': price,
                        'discount': discount,
                        'rating': rating,
                        'scraped_at': datetime.utcnow().isoformat()
                    })
                    
                except Exception as e:
                    print(f"Error parsing deal: {e}")
                    continue
            
            # Save results
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_file = f"{self.output_dir}/deals_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump({
                    'source': 'Amazon Deals',
                    'scraped_at': datetime.utcnow().isoformat(),
                    'category': category or 'All',
                    'deals': deals
                }, f, indent=2)
            
            print(f"Successfully scraped {len(deals)} deals. Saved to {output_file}")
            return {"status": "success", "deals_found": len(deals), "output_file": output_file}
            
        except Exception as e:
            print(f"Error scraping Amazon deals: {e}")
            return {"status": "error", "error": str(e)}
            
    def analyze(self, data):
        """Analyze the scraped deals data"""
        if not data or 'deals' not in data:
            return "No data to analyze"
            
        deals = data['deals']
        if not deals:
            return "No deals found in the data"
            
        # Basic analysis
        total_deals = len(deals)
        
        # Extract prices (this is simplified, you'd need to parse the price strings)
        prices = []
        for deal in deals:
            try:
                # This is a very basic price extraction - you'd need to improve this
                price_str = ''.join(c for c in deal.get('price', '') if c.isdigit() or c == '.')
                if price_str:
                    prices.append(float(price_str))
            except:
                continue
        
        avg_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        
        return {
            "total_deals": total_deals,
            "average_price": round(avg_price, 2),
            "min_price": min_price,
            "max_price": max_price,
            "sample_deal": deals[0] if deals else None
        }
