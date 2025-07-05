import os
import httpx
import re
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel, HttpUrl
from ..utils.storage import StorageManager

class TavilySearchResult(BaseModel):
    """Model for Tavily search results"""
    url: HttpUrl
    title: str
    content: str
    score: Optional[float] = None

class ImprovedTavilyService:
    """Improved service for finding actual terms and conditions documents"""
    
    def __init__(self, base_url: str = "https://api.tavily.com", api_key: Optional[str] = None):
        """Initialize the improved Tavily service."""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.client = httpx.AsyncClient(timeout=45.0)  # Increased timeout
        self.storage = StorageManager()
        
        # Known patterns for legitimate terms URLs
        self.terms_url_patterns = [
            r'terms.*service',
            r'terms.*use',
            r'terms.*condition',
            r'privacy.*policy',
            r'user.*agreement',
            r'service.*agreement',
            r'legal.*terms',
            r'eula',
            r'acceptable.*use'
        ]
        
        # Patterns to avoid (government, news, etc.)
        self.bad_url_patterns = [
            r'canada\.ca',
            r'gov\.ca',
            r'government',
            r'news\.',
            r'blog\.',
            r'help\.',
            r'support\.',
            r'about\.',
            r'contact\.',
            r'career',
            r'job',
            r'press',
            r'media',
            r'investor'
        ]
    
    def _score_url_quality(self, url: str, title: str) -> float:
        """Score how likely a URL is to contain actual terms content."""
        score = 0.0
        url_lower = url.lower()
        title_lower = title.lower()
        
        # Positive indicators
        for pattern in self.terms_url_patterns:
            if re.search(pattern, url_lower) or re.search(pattern, title_lower):
                score += 2.0
        
        # Official domain bonus
        if any(domain in url_lower for domain in ['.com/', '.net/', '.org/']):
            score += 1.0
        
        # Legal section indicators
        if any(term in url_lower for term in ['legal/', 'terms/', 'privacy/', 'policy/']):
            score += 1.5
        
        # Negative indicators
        for pattern in self.bad_url_patterns:
            if re.search(pattern, url_lower):
                score -= 5.0
        
        # Third-party content indicators
        if any(term in url_lower for term in ['reddit.com', 'wikipedia.org', 'stackoverflow.com']):
            score -= 3.0
        
        return score
    
    def _validate_terms_content(self, content: str, app_name: str) -> Tuple[bool, str]:
        """Validate that extracted content is actually terms and conditions."""
        if not content or len(content) < 1000:
            return False, "Content too short for terms document"
        
        content_lower = content.lower()
        app_name_lower = app_name.lower()
        
        # Check for news/government content indicators
        bad_indicators = [
            'dear ms.', 'dear mr.', 'government of canada', 'we welcome this opportunity',
            'consultation', 'regulatory framework', 'innovation, science and economic development',
            'canadian heritage', 'committee', 'parliament', 'legislation',
            'breaking news', 'reuters', 'associated press', 'photo illustration',
            'about us', 'contact us', 'our story', 'careers', 'press release'
        ]
        
        for indicator in bad_indicators:
            if indicator in content_lower:
                return False, f"Contains non-terms indicator: {indicator}"
        
        # Check for positive terms indicators
        positive_indicators = [
            'terms of service', 'terms of use', 'privacy policy', 'user agreement',
            'data collection', 'personal information', 'cookies', 'intellectual property',
            'limitation of liability', 'governing law', 'arbitration', 'termination',
            'prohibited conduct', 'disclaimers', 'acceptable use'
        ]
        
        positive_count = sum(1 for indicator in positive_indicators if indicator in content_lower)
        
        if positive_count < 3:
            return False, f"Insufficient terms indicators: only {positive_count} found"
        
        # Check if it's just navigation/header content
        if content.count('\n') < 10 and len(content) < 2000:
            return False, "Content appears to be navigation/header only"
        
        return True, f"Valid terms content with {positive_count} positive indicators"
    
    async def search_terms_with_improved_queries(self, app_name: str) -> List[Dict]:
        """Search with multiple improved queries targeting actual terms documents."""
        
        # Multiple search strategies
        search_queries = [
            f'site:{app_name.lower().replace(" ", "")}.com terms of service',
            f'site:{app_name.lower().replace(" ", "")}.com privacy policy',
            f'"{app_name}" terms of service legal document',
            f'"{app_name}" privacy policy official',
            f'"{app_name}" user agreement terms conditions',
            f'inurl:terms "{app_name}" OR inurl:privacy "{app_name}"'
        ]
        
        all_results = []
        
        for query in search_queries:
            try:
                response = await self.client.post(
                    f"{self.base_url}/search",
                    json={
                        "api_key": self.api_key,
                        "query": query,
                        "include_answer": False,
                        "include_raw_content": True,
                        "max_results": 3,  # Fewer but more targeted results
                        "search_depth": "advanced",  # More thorough search
                        "include_domains": [".com", ".org", ".net"],
                        "exclude_domains": [
                            "reddit.com", "wikipedia.org", "stackoverflow.com",
                            "canada.ca", "gov.ca", "news.com", "cnn.com", "bbc.com"
                        ]
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                response.raise_for_status()
                results = response.json()
                
                for result in results.get("results", []):
                    url = result.get("url", "")
                    title = result.get("title", "")
                    content = result.get("content", "")
                    
                    # Score and filter results
                    quality_score = self._score_url_quality(url, title)
                    
                    if quality_score > 0:  # Only keep positive scoring URLs
                        all_results.append({
                            "url": url,
                            "title": title,
                            "content": content,
                            "score": result.get("score", 0.0),
                            "quality_score": quality_score,
                            "query": query
                        })
                        
            except Exception as e:
                print(f"Error with query '{query}': {str(e)}")
                continue
        
        # Sort by quality score and remove duplicates
        unique_results = {}
        for result in all_results:
            url = result["url"]
            if url not in unique_results or result["quality_score"] > unique_results[url]["quality_score"]:
                unique_results[url] = result
        
        # Return top results sorted by quality
        sorted_results = sorted(unique_results.values(), key=lambda x: x["quality_score"], reverse=True)
        return sorted_results[:5]  # Top 5 results
    
    async def extract_full_terms_content(self, url: str) -> Optional[str]:
        """Extract complete terms content with better parsing."""
        try:
            response = await self.client.post(
                f"{self.base_url}/extract",
                json={
                    "api_key": self.api_key,
                    "urls": [url],
                    "include_raw_content": True,
                    "include_links": False
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            
            # Try different extraction paths
            content = None
            if isinstance(data, dict) and "results" in data:
                results = data["results"]
                if results and len(results) > 0:
                    first_result = results[0]
                    content = (first_result.get("raw_content") or 
                             first_result.get("content") or 
                             first_result.get("text", ""))
            elif isinstance(data, dict):
                content = (data.get("raw_content") or 
                          data.get("content") or 
                          data.get("text", ""))
            
            # Clean up content
            if content:
                # Remove excessive whitespace and navigation elements
                content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
                content = re.sub(r'^\s*[•\-\*]\s*$', '', content, flags=re.MULTILINE)
                content = content.strip()
            
            return content
            
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None
    
    async def find_actual_terms_for_app(self, app_name: str, save_to_storage: bool = True) -> Optional[Dict]:
        """Find actual terms and conditions with improved methodology."""
        print(f"🔍 Searching for ACTUAL terms and conditions for {app_name}...")
        
        # Search with improved queries
        search_results = await self.search_terms_with_improved_queries(app_name)
        if not search_results:
            print("❌ No search results found")
            return None
        
        print(f"📊 Found {len(search_results)} potential sources, evaluating quality...")
        
        # Try to extract and validate content from top results
        for i, result in enumerate(search_results, 1):
            url = result["url"]
            quality_score = result["quality_score"]
            query = result["query"]
            
            print(f"🔗 [{i}] Trying {url} (quality: {quality_score:.1f}, from: '{query}')")
            
            content = await self.extract_full_terms_content(url)
            if not content:
                print(f"⚠️  Failed to extract content")
                continue
            
            # Validate content
            is_valid, reason = self._validate_terms_content(content, app_name)
            print(f"✓ Validation: {reason}")
            
            if is_valid:
                terms_data = {
                    "app_name": app_name,
                    "terms_url": url,
                    "terms_text": content,
                    "source": "improved_tavily",
                    "quality_score": quality_score,
                    "search_query": query,
                    "content_length": len(content)
                }
                
                # Save to storage if requested
                if save_to_storage:
                    saved_path = self.storage.save_terms(
                        app_name=app_name,
                        content=content,
                        source_url=url
                    )
                    terms_data["saved_path"] = str(saved_path)
                    print(f"💾 Saved legitimate terms to: {saved_path}")
                
                print(f"✅ Successfully found actual terms for {app_name}!")
                return terms_data
            else:
                print(f"❌ Invalid content: {reason}")
        
        print(f"😞 No legitimate terms and conditions found for {app_name}")
        return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()