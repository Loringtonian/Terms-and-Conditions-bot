#!/usr/bin/env python3
"""
Bright Data service for scraping terms and conditions using Browser API.
Parallel implementation to Tavily service using Bright Data's scraping infrastructure.
"""
import os
import re
import json
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed. Install with: pip install playwright")

from ..utils.storage import StorageManager

class BrightDataService:
    """Service for scraping terms and conditions using Bright Data Browser API"""
    
    def __init__(self, auth_string: Optional[str] = None):
        """Initialize the Bright Data service.
        
        Args:
            auth_string: Bright Data authentication string. If not provided, uses BRIGHT_DATA_AUTH from environment.
        """
        self.auth = auth_string or os.getenv("BRIGHT_DATA_AUTH")
        if not self.auth:
            raise ValueError("Bright Data authentication string is required. Set BRIGHT_DATA_AUTH environment variable.")
        
        self.endpoint = f"wss://{self.auth}@brd.superproxy.io:9222"
        self.storage = StorageManager(base_dir="bright_storage")
        
        # Browser connection management
        self.browser = None
        self.playwright = None
        
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is required for Bright Data service. Install with: pip install playwright")
    
    async def _scrape_page_with_browser(self, url: str, wait_for_selector: Optional[str] = None) -> Dict:
        """
        Scrape a single page using existing browser connection
        
        Args:
            url: Target URL to scrape
            wait_for_selector: Optional CSS selector to wait for
            
        Returns:
            dict: Contains page content, title, and metadata
        """
        try:
            # Create new page (reuse browser connection)
            page = await self.browser.new_page()
            
            # Block unnecessary resources to save bandwidth
            await page.route("**/*.{png,jpg,jpeg,gif,svg,css,font,woff,woff2}", 
                            lambda route: route.abort())
            
            print(f"📄 Navigating to page...")
            
            # Navigate to page with optimized timeout
            response = await page.goto(url, 
                                     wait_until="domcontentloaded",
                                     timeout=30000)
            
            # Wait for specific content if needed
            if wait_for_selector:
                try:
                    await page.wait_for_selector(wait_for_selector, timeout=10000)
                except Exception as e:
                    print(f"⚠️  Warning: Could not find selector '{wait_for_selector}': {str(e)}")
            
            # Extract page data
            title = await page.title()
            content = await page.content()
            
            # Get page metadata
            metadata = {
                "url": url,
                "title": title,
                "status": response.status if response else None,
                "scraped_at": datetime.now().isoformat(),
                "content_length": len(content),
                "scraper": "bright_data"
            }
            
            # Close only the page, not the browser
            await page.close()
            
            print(f"✅ Successfully scraped {len(content):,} characters")
            
            return {
                "success": True,
                "content": content,
                "metadata": metadata
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Scraping failed: {error_msg}")
            
            # Check if it's a rate limiting error
            if "cooldown" in error_msg.lower() or "limit reached" in error_msg.lower():
                print("⚠️  Rate limit detected - will need longer delays")
                return {
                    "success": False,
                    "error": error_msg,
                    "url": url,
                    "rate_limited": True
                }
            
            return {
                "success": False,
                "error": error_msg,
                "url": url
            }
    
    async def scrape_page(self, url: str, wait_for_selector: Optional[str] = None) -> Dict:
        """
        Scrape a single page using Bright Data Browser API (legacy method)
        
        Args:
            url: Target URL to scrape
            wait_for_selector: Optional CSS selector to wait for
            
        Returns:
            dict: Contains page content, title, and metadata
        """
        await self._ensure_browser_connection()
        return await self._scrape_page_with_browser(url, wait_for_selector)
    
    def extract_text_content(self, html_content: str) -> str:
        """Extract clean text content from HTML"""
        # Remove script and style elements
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text_content = re.sub(r'<[^>]+>', '', html_content)
        
        # Clean up whitespace
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        return text_content
    
    async def find_terms_links(self, domain_url: str) -> List[str]:
        """
        Find terms and conditions links on a website
        
        Args:
            domain_url: Main website URL to search
            
        Returns:
            List of potential terms and conditions URLs
        """
        print(f"🔍 Searching for terms links on: {domain_url}")
        
        result = await self.scrape_page(domain_url)
        
        if not result["success"]:
            print(f"❌ Failed to load main page: {result.get('error', 'Unknown error')}")
            return []
        
        # Look for terms-related links
        terms_patterns = [
            r'href="([^"]*(?:terms|conditions|legal|privacy|policy)[^"]*)"',
            r'href="([^"]*(?:tos|eula|agreement)[^"]*)"',
            r'href="([^"]*(?:termos|condiciones|legales)[^"]*)"'  # Multi-language support
        ]
        
        found_links = []
        content = result["content"]
        
        for pattern in terms_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Convert relative URLs to absolute
                full_url = urljoin(domain_url, match)
                if full_url not in found_links and self._is_valid_terms_url(full_url):
                    found_links.append(full_url)
        
        print(f"📋 Found {len(found_links)} potential terms links")
        return found_links
    
    def _is_valid_terms_url(self, url: str) -> bool:
        """Check if URL is likely to contain terms and conditions"""
        # Filter out obviously non-terms URLs
        exclude_patterns = [
            r'\.(?:jpg|jpeg|png|gif|pdf|doc|docx)$',
            r'facebook\.com|twitter\.com|instagram\.com',
            r'mailto:',
            r'javascript:',
            r'#'
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return True
    
    async def _ensure_browser_connection(self):
        """Ensure browser connection is established and reuse it"""
        if self.browser is None or self.playwright is None:
            self.playwright = await async_playwright().start()
            print(f"🌐 Connecting to Bright Data browser...")
            self.browser = await self.playwright.chromium.connect_over_cdp(self.endpoint)
            print(f"✅ Browser connected successfully")
    
    async def scrape_terms_for_app(self, app_name: str, known_terms_url: Optional[str] = None) -> Optional[Dict]:
        """
        Scrape terms and conditions for a specific app
        
        Args:
            app_name: Name of the application
            known_terms_url: Direct URL to terms if known
            
        Returns:
            Dictionary with extracted terms content or None if not found
        """
        print(f"🔍 Scraping terms for: {app_name}")
        
        urls_to_try = []
        
        if known_terms_url:
            urls_to_try.append(known_terms_url)
        else:
            # Check for specific known URLs first
            specific_urls = self._get_specific_terms_urls(app_name)
            if specific_urls:
                urls_to_try.extend(specific_urls)
            else:
                # Generate common terms URLs for the app (prioritize direct URLs)
                app_domain = self._guess_app_domain(app_name)
                if app_domain:
                    # Most common terms URLs first
                    common_terms_paths = [
                        f"https://{app_domain}/terms",
                        f"https://{app_domain}/terms-of-service",
                        f"https://{app_domain}/legal/terms",
                        f"https://{app_domain}/legal/terms-of-service",
                        f"https://{app_domain}/privacy",
                        f"https://{app_domain}/legal/privacy",
                    ]
                    urls_to_try.extend(common_terms_paths)
                    
                    # Skip link discovery for now - it's too slow
                    # If direct URLs fail, we can add this back as a fallback
        
        # Ensure browser connection
        await self._ensure_browser_connection()
        
        # Try each URL until we find terms (reuse browser connection)
        for i, url in enumerate(urls_to_try, 1):
            print(f"📄 Trying URL {i}/{len(urls_to_try)}: {url}")
            
            result = await self._scrape_page_with_browser(url)
            
            if result["success"]:
                text_content = self.extract_text_content(result["content"])
                
                # Check if this looks like terms and conditions
                if self._looks_like_terms_content(text_content):
                    print(f"✅ Found terms content: {len(text_content):,} characters")
                    
                    return {
                        "app_name": app_name,
                        "terms_url": url,
                        "terms_text": text_content,
                        "raw_html": result["content"],
                        "metadata": result["metadata"],
                        "source": "bright_data"
                    }
                else:
                    print(f"⚠️  Content doesn't look like terms and conditions")
            else:
                print(f"❌ Failed to load: {result.get('error', 'Unknown error')}")
            
            # Longer delay to avoid rate limiting and cooldowns
            await asyncio.sleep(5)
        
        print(f"❌ Could not find terms and conditions for {app_name}")
        return None
    
    def _guess_app_domain(self, app_name: str) -> Optional[str]:
        """Guess the domain name for an app"""
        # Simple mapping for common apps
        domain_mapping = {
            "tiktok": "tiktok.com",
            "instagram": "instagram.com", 
            "facebook": "facebook.com",
            "twitter": "twitter.com",
            "x": "x.com",
            "youtube": "youtube.com",
            "netflix": "netflix.com",
            "spotify": "spotify.com",
            "amazon": "amazon.com",
            "google": "google.com",
            "microsoft": "microsoft.com",
            "apple": "apple.com",
            "linkedin": "linkedin.com",
            "snapchat": "snapchat.com",
            "telegram": "telegram.org",
            "whatsapp": "whatsapp.com",
            "discord": "discord.com",
            "reddit": "reddit.com",
            "pinterest": "pinterest.com",
            "zoom": "zoom.us"
        }
        
        app_lower = app_name.lower().replace(" ", "").replace("-", "")
        
        # Check direct mapping first
        if app_lower in domain_mapping:
            return domain_mapping[app_lower]
        
        # Check partial matches
        for key, domain in domain_mapping.items():
            if key in app_lower or app_lower in key:
                return domain
        
        # Fallback: try app name as domain
        simple_name = re.sub(r'[^a-zA-Z]', '', app_name.lower())
        if simple_name:
            return f"{simple_name}.com"
        
        return None
    
    def _get_specific_terms_urls(self, app_name: str) -> List[str]:
        """Get specific known terms URLs for popular apps"""
        app_lower = app_name.lower().replace(" ", "").replace("-", "")
        
        # Known specific URLs for popular apps
        specific_urls = {
            # Google services all use the same terms URL
            "googleplayservices": ["https://policies.google.com/terms"],
            "youtube": ["https://policies.google.com/terms"],
            "googlemaps": ["https://policies.google.com/terms"],
            "googlechrome": ["https://www.google.com/chrome/terms/", "https://policies.google.com/terms"],
            "gmail": ["https://policies.google.com/terms"],
            "google": ["https://policies.google.com/terms"],
            "googlephotos": ["https://policies.google.com/terms"],
            "googledrive": ["https://policies.google.com/terms"],
            "googlesearch": ["https://policies.google.com/terms"],
            "googlecalendar": ["https://policies.google.com/terms"],
            "googlemeet": ["https://policies.google.com/terms"],
            "googlemessages": ["https://policies.google.com/terms"],
            "googlepay": ["https://policies.google.com/terms"],
            "googleassistant": ["https://policies.google.com/terms"],
            "googletranslate": ["https://policies.google.com/terms"],
            "googlekeep": ["https://policies.google.com/terms"],
            "googledocs": ["https://policies.google.com/terms"],
            "googlesheets": ["https://policies.google.com/terms"],
            "googleslides": ["https://policies.google.com/terms"],
            "youtubemusic": ["https://policies.google.com/terms"],
            "gboard": ["https://policies.google.com/terms"],
            "androidwebview": ["https://policies.google.com/terms"],
            "androidsystemwebview": ["https://policies.google.com/terms"],
            "androidaccessibilitysuite": ["https://policies.google.com/terms"],
            "speechservicesbygoogle": ["https://policies.google.com/terms"],
            "googleone": ["https://policies.google.com/terms"],
            "googlelens": ["https://policies.google.com/terms"],
            "googletv": ["https://policies.google.com/terms"],
            "googlemapsgo": ["https://policies.google.com/terms"],
            "filesbygoogle": ["https://policies.google.com/terms"],
            
            # Other major services
            "tiktok": ["https://www.tiktok.com/legal/terms-of-service"],
            "instagram": ["https://help.instagram.com/581066165581870"],
            "facebook": ["https://www.facebook.com/terms.php"],
            "whatsapp": ["https://www.whatsapp.com/legal/terms-of-service"],
            "twitter": ["https://twitter.com/en/tos"],
            "x": ["https://x.com/en/tos"],
            "netflix": ["https://help.netflix.com/legal/termsofuse"],
            "spotify": ["https://www.spotify.com/us/legal/end-user-agreement/"],
            "amazon": ["https://www.amazon.com/gp/help/customer/display.html?nodeId=508088"],
            "apple": ["https://www.apple.com/legal/internet-services/terms/site.html"],
            "microsoft": ["https://www.microsoft.com/en-us/servicesagreement/"],
            "discord": ["https://discord.com/terms"],
            "reddit": ["https://www.redditinc.com/policies/user-agreement"],
            "snapchat": ["https://snap.com/en-US/terms"],
            "telegram": ["https://telegram.org/tos"],
            "zoom": ["https://explore.zoom.us/en/terms/"],
            "linkedin": ["https://www.linkedin.com/legal/user-agreement"],
            "pinterest": ["https://policy.pinterest.com/en/terms-of-service"]
        }
        
        return specific_urls.get(app_lower, [])
    
    def _looks_like_terms_content(self, text: str) -> bool:
        """Check if text content looks like terms and conditions"""
        if len(text) < 500:  # Too short to be real terms
            return False
        
        # Look for common terms and conditions indicators
        terms_indicators = [
            "terms of service", "terms of use", "user agreement", "privacy policy",
            "acceptable use", "code of conduct", "license agreement", "end user",
            "by using", "by accessing", "these terms", "this agreement",
            "intellectual property", "limitation of liability", "governing law"
        ]
        
        text_lower = text.lower()
        indicator_count = sum(1 for indicator in terms_indicators if indicator in text_lower)
        
        # If we find at least 3 indicators, it's probably terms content
        return indicator_count >= 3
    
    async def scrape_and_save_terms(self, app_name: str, known_url: Optional[str] = None) -> Optional[Path]:
        """
        Scrape terms for an app and save using the storage manager
        
        Args:
            app_name: Name of the application
            known_url: Optional direct URL to terms
            
        Returns:
            Path to saved file or None if failed
        """
        # Close existing browser connection to reset rate limits
        await self.close()
        
        terms_data = await self.scrape_terms_for_app(app_name, known_url)
        
        if not terms_data:
            return None
        
        # Save using storage manager
        saved_path = self.storage.save_terms(
            app_name=app_name,
            content=terms_data["terms_text"],
            source_url=terms_data["terms_url"],
            version=None
        )
        
        print(f"💾 Saved terms to: {saved_path}")
        return saved_path
    
    async def close(self):
        """Cleanup method - close browser and playwright"""
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None