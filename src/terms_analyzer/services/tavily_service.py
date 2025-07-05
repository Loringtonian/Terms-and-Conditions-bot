import os
import httpx
from typing import List, Dict, Optional
from pydantic import BaseModel, HttpUrl
from ..models.analysis import TCAnalysis

class TavilySearchResult(BaseModel):
    """Model for Tavily search results"""
    url: HttpUrl
    title: str
    content: str
    score: Optional[float] = None

class TavilyService:
    """Service for interacting with Tavily MCP server"""
    
    def __init__(self, base_url: str = "https://api.tavily.com", api_key: Optional[str] = None):
        """Initialize the Tavily service.
        
        Args:
            base_url: Base URL of the Tavily API
            api_key: Tavily API key. If not provided, will use TAVILY_API_KEY from environment.
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def search_terms_and_conditions(self, app_name: str) -> List[Dict]:
        """Search for terms and conditions for a given app.
        
        Args:
            app_name: Name of the application to search for
            
        Returns:
            List of search results with URLs and snippets
        """
        query = f'"{app_name}" terms of service OR privacy policy canada'
        
        try:
            response = await self.client.post(
                f"{self.base_url}/search",
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "include_answer": False,
                    "include_raw_content": True,
                    "max_results": 5,
                    "include_domains": ["com", "ca"],
                    "exclude_domains": ["facebook.com", "twitter.com"],
                    "search_depth": "basic"
                },
                headers={
                    "Content-Type": "application/json"
                }
            )
            
            response.raise_for_status()
            results = response.json()
            
            # Process and return the results
            return [
                {
                    "url": result["url"],
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0)
                }
                for result in results.get("results", [])
            ]
            
        except Exception as e:
            print(f"Error searching with Tavily: {str(e)}")
            return []
    
    async def extract_terms_text(self, url: str) -> Optional[str]:
        """Extract the main text content from a terms and conditions page.
        
        Args:
            url: URL of the terms and conditions page
            
        Returns:
            Extracted text content or None if extraction fails
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/extract",
                json={
                    "api_key": self.api_key,
                    "urls": [url]
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            # Handle the response format - could be a list of results or direct text
            if isinstance(data, dict) and "results" in data:
                results = data["results"]
                if results and len(results) > 0:
                    first_result = results[0]
                    return first_result.get("raw_content", first_result.get("content", first_result.get("text", "")))
            elif isinstance(data, dict) and "content" in data:
                return data["content"]
            return data.get("text", "")
            
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None
    
    async def find_terms_for_app(self, app_name: str) -> Optional[Dict]:
        """Find and extract terms and conditions for an app.
        
        Args:
            app_name: Name of the application
            
        Returns:
            Dictionary with terms text and metadata, or None if not found
        """
        print(f"Searching for terms and conditions for {app_name}...")
        
        # First, search for potential terms pages
        search_results = await self.search_terms_and_conditions(app_name)
        if not search_results:
            print("No search results found")
            return None
            
        # Try to extract content from the top results
        for result in search_results[:3]:  # Limit to top 3 results
            url = result["url"]
            print(f"Trying to extract content from: {url}")
            
            content = await self.extract_terms_text(url)
            if content and len(content) > 500:  # Lowered threshold for testing
                return {
                    "app_name": app_name,
                    "terms_url": url,
                    "terms_text": content,
                    "source": "tavily"
                }
                
        print("No suitable terms and conditions found")
        return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
