# Bright Data Python Examples

## Installation Requirements

```bash
# For Playwright
pip install playwright
playwright install chromium

# For Pyppeteer (alternative)
pip install pyppeteer

# For Selenium (alternative)
pip install selenium
```

## Environment Setup

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Your Bright Data credentials
BRIGHT_DATA_AUTH = "brd-customer-hl_ccf234f3-zone-terms_and_conditions:r5tk64g5ywyt"
BRIGHT_DATA_ENDPOINT = f"wss://{BRIGHT_DATA_AUTH}@brd.superproxy.io:9222"
```

## Complete Playwright Example

```python
from playwright.async_api import async_playwright
import asyncio
import json
from datetime import datetime

class BrightDataScraper:
    def __init__(self, auth_string):
        self.auth = auth_string
        self.endpoint = f"wss://{auth_string}@brd.superproxy.io:9222"
    
    async def scrape_page(self, url, wait_for_selector=None):
        """
        Scrape a single page using Bright Data Browser API
        
        Args:
            url: Target URL to scrape
            wait_for_selector: Optional CSS selector to wait for
            
        Returns:
            dict: Contains page content, title, and metadata
        """
        async with async_playwright() as playwright:
            try:
                # Connect to Bright Data browser
                browser = await playwright.chromium.connect_over_cdp(self.endpoint)
                page = await browser.new_page()
                
                # Block unnecessary resources to save bandwidth
                await page.route("**/*.{png,jpg,jpeg,gif,svg,css,font,woff,woff2}", 
                                lambda route: route.abort())
                
                # Navigate to page with extended timeout
                response = await page.goto(url, 
                                         wait_until="domcontentloaded",
                                         timeout=120000)
                
                # Wait for specific content if needed
                if wait_for_selector:
                    await page.wait_for_selector(wait_for_selector, timeout=30000)
                
                # Extract page data
                title = await page.title()
                content = await page.content()
                
                # Get page metadata
                metadata = {
                    "url": url,
                    "title": title,
                    "status": response.status if response else None,
                    "scraped_at": datetime.now().isoformat(),
                    "content_length": len(content)
                }
                
                await browser.close()
                
                return {
                    "success": True,
                    "content": content,
                    "metadata": metadata
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "url": url
                }

# Usage example
async def main():
    scraper = BrightDataScraper(BRIGHT_DATA_AUTH)
    
    # Example: Scrape terms and conditions
    result = await scraper.scrape_page(
        "https://www.tiktok.com/legal/terms-of-service",
        wait_for_selector="body"
    )
    
    if result["success"]:
        print(f"Successfully scraped {result['metadata']['content_length']} characters")
        print(f"Page title: {result['metadata']['title']}")
    else:
        print(f"Scraping failed: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Example: Terms & Conditions Scraper

```python
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

class TermsAndConditionsScraper:
    def __init__(self, auth_string):
        self.scraper = BrightDataScraper(auth_string)
    
    async def find_terms_links(self, domain_url: str) -> List[str]:
        """
        Find terms and conditions links on a website
        
        Args:
            domain_url: Main website URL to search
            
        Returns:
            List of potential terms and conditions URLs
        """
        result = await self.scraper.scrape_page(domain_url)
        
        if not result["success"]:
            return []
        
        # Look for terms-related links
        terms_patterns = [
            r'href="([^"]*(?:terms|conditions|legal|privacy|policy)[^"]*)"',
            r'href="([^"]*(?:tos|eula|agreement)[^"]*)"'
        ]
        
        found_links = []
        content = result["content"]
        
        for pattern in terms_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Convert relative URLs to absolute
                full_url = urljoin(domain_url, match)
                if full_url not in found_links:
                    found_links.append(full_url)
        
        return found_links
    
    async def scrape_terms_content(self, terms_url: str) -> Dict:
        """
        Scrape the actual terms and conditions content
        
        Args:
            terms_url: URL of the terms and conditions page
            
        Returns:
            Dictionary with extracted terms content
        """
        result = await self.scraper.scrape_page(terms_url)
        
        if not result["success"]:
            return result
        
        # Extract text content (remove HTML tags)
        content = result["content"]
        
        # Simple text extraction (could be enhanced with BeautifulSoup)
        import re
        text_content = re.sub(r'<[^>]+>', '', content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        return {
            "success": True,
            "url": terms_url,
            "title": result["metadata"]["title"],
            "raw_html": content,
            "text_content": text_content,
            "content_length": len(text_content),
            "scraped_at": result["metadata"]["scraped_at"]
        }

# Usage example
async def scrape_app_terms():
    scraper = TermsAndConditionsScraper(BRIGHT_DATA_AUTH)
    
    # Example: TikTok terms
    terms_url = "https://www.tiktok.com/legal/terms-of-service"
    
    result = await scraper.scrape_terms_content(terms_url)
    
    if result["success"]:
        print(f"Scraped {result['content_length']} characters of terms content")
        print(f"Title: {result['title']}")
        
        # Save to file
        with open("bright_tiktok_terms.html", "w", encoding="utf-8") as f:
            f.write(result["raw_html"])
        
        with open("bright_tiktok_terms.txt", "w", encoding="utf-8") as f:
            f.write(result["text_content"])
    else:
        print(f"Failed to scrape terms: {result['error']}")

if __name__ == "__main__":
    asyncio.run(scrape_app_terms())
```

## Error Handling Best Practices

```python
import asyncio
from typing import Optional

async def robust_scrape(url: str, max_retries: int = 3) -> Optional[Dict]:
    """
    Robust scraping with retry logic and error handling
    """
    scraper = BrightDataScraper(BRIGHT_DATA_AUTH)
    
    for attempt in range(max_retries):
        try:
            result = await scraper.scrape_page(url)
            
            if result["success"]:
                return result
            
            print(f"Attempt {attempt + 1} failed: {result.get('error', 'Unknown error')}")
            
            # Wait before retry
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5  # Progressive backoff
                print(f"Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
                
        except Exception as e:
            print(f"Attempt {attempt + 1} exception: {str(e)}")
            
            if attempt < max_retries - 1:
                await asyncio.sleep(5)
    
    return None
```

## Performance Optimization

```python
# Concurrent scraping (be mindful of rate limits)
async def scrape_multiple_urls(urls: List[str], max_concurrent: int = 3):
    """
    Scrape multiple URLs concurrently with rate limiting
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    scraper = BrightDataScraper(BRIGHT_DATA_AUTH)
    
    async def scrape_with_semaphore(url):
        async with semaphore:
            return await scraper.scrape_page(url)
    
    tasks = [scrape_with_semaphore(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results
```