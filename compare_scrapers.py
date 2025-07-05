#!/usr/bin/env python3
"""
Compare Tavily vs Bright Data scraping results.
Run both scrapers on the same terms and compare results.
"""
import asyncio
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from src.terms_analyzer.services.tavily_service import TavilyService
from src.terms_analyzer.services.bright_service import BrightDataService

load_dotenv()

class ScraperComparison:
    def __init__(self):
        self.tavily = TavilyService()
        try:
            self.bright = BrightDataService()
            self.bright_available = True
        except Exception as e:
            print(f"⚠️  Bright Data not available: {str(e)}")
            self.bright_available = False
    
    async def test_app_scraping(self, app_name: str, known_url: Optional[str] = None) -> Dict:
        """Test both scrapers on the same app and compare results"""
        
        print(f"\n🔍 TESTING: {app_name}")
        print("=" * 50)
        
        results = {
            "app_name": app_name,
            "test_url": known_url,
            "timestamp": datetime.now().isoformat(),
            "tavily": {"available": True},
            "bright": {"available": self.bright_available},
            "comparison": {}
        }
        
        # Test Tavily
        print(f"🌐 Testing Tavily scraper...")
        tavily_start = time.time()
        
        try:
            if known_url:
                # For direct URL testing, use extract method
                tavily_content = await self.tavily.extract_terms_text(known_url)
                if tavily_content:
                    tavily_result = {
                        "success": True,
                        "content_length": len(tavily_content),
                        "url": known_url,
                        "content": tavily_content[:1000] + "..." if len(tavily_content) > 1000 else tavily_content
                    }
                else:
                    tavily_result = {"success": False, "error": "No content extracted"}
            else:
                # Use search and extract method
                tavily_data = await self.tavily.find_terms_for_app(app_name)
                if tavily_data:
                    tavily_result = {
                        "success": True,
                        "content_length": len(tavily_data["terms_text"]),
                        "url": tavily_data["terms_url"],
                        "content": tavily_data["terms_text"][:1000] + "..." if len(tavily_data["terms_text"]) > 1000 else tavily_data["terms_text"]
                    }
                else:
                    tavily_result = {"success": False, "error": "No terms found"}
            
            tavily_time = time.time() - tavily_start
            tavily_result["execution_time"] = tavily_time
            
        except Exception as e:
            tavily_result = {
                "success": False, 
                "error": str(e),
                "execution_time": time.time() - tavily_start
            }
        
        results["tavily"].update(tavily_result)
        
        # Test Bright Data (if available)
        if self.bright_available:
            print(f"🌟 Testing Bright Data scraper...")
            bright_start = time.time()
            
            try:
                bright_data = await self.bright.scrape_terms_for_app(app_name, known_url)
                if bright_data:
                    bright_result = {
                        "success": True,
                        "content_length": len(bright_data["terms_text"]),
                        "url": bright_data["terms_url"],
                        "content": bright_data["terms_text"][:1000] + "..." if len(bright_data["terms_text"]) > 1000 else bright_data["terms_text"]
                    }
                else:
                    bright_result = {"success": False, "error": "No terms found"}
                
                bright_time = time.time() - bright_start
                bright_result["execution_time"] = bright_time
                
            except Exception as e:
                bright_result = {
                    "success": False,
                    "error": str(e),
                    "execution_time": time.time() - bright_start
                }
            
            results["bright"].update(bright_result)
        
        # Generate comparison
        results["comparison"] = self._compare_results(results["tavily"], results["bright"])
        
        return results
    
    def _compare_results(self, tavily_result: Dict, bright_result: Dict) -> Dict:
        """Compare the results from both scrapers"""
        comparison = {
            "both_successful": False,
            "content_length_diff": None,
            "speed_comparison": None,
            "content_similarity": None,
            "winner": None
        }
        
        if not bright_result.get("available"):
            comparison["winner"] = "tavily_only"
            comparison["note"] = "Bright Data not available"
            return comparison
        
        tavily_success = tavily_result.get("success", False)
        bright_success = bright_result.get("success", False)
        
        if tavily_success and bright_success:
            comparison["both_successful"] = True
            
            # Compare content length
            tavily_length = tavily_result.get("content_length", 0)
            bright_length = bright_result.get("content_length", 0)
            comparison["content_length_diff"] = bright_length - tavily_length
            
            # Compare speed
            tavily_time = tavily_result.get("execution_time", 0)
            bright_time = bright_result.get("execution_time", 0)
            comparison["speed_comparison"] = {
                "tavily_time": tavily_time,
                "bright_time": bright_time,
                "faster": "tavily" if tavily_time < bright_time else "bright"
            }
            
            # Simple content similarity (first 500 chars)
            tavily_content = tavily_result.get("content", "")[:500].lower()
            bright_content = bright_result.get("content", "")[:500].lower()
            
            # Count common words
            tavily_words = set(tavily_content.split())
            bright_words = set(bright_content.split())
            if tavily_words and bright_words:
                common_words = tavily_words.intersection(bright_words)
                similarity = len(common_words) / max(len(tavily_words), len(bright_words))
                comparison["content_similarity"] = similarity
            
            # Determine winner
            if abs(comparison["content_length_diff"]) < 1000:
                comparison["winner"] = "tie"
            elif comparison["content_length_diff"] > 0:
                comparison["winner"] = "bright"
            else:
                comparison["winner"] = "tavily"
                
        elif tavily_success:
            comparison["winner"] = "tavily"
        elif bright_success:
            comparison["winner"] = "bright"
        else:
            comparison["winner"] = "none"
        
        return comparison
    
    def print_results(self, results: Dict):
        """Print formatted comparison results"""
        
        print(f"\n📊 RESULTS FOR {results['app_name'].upper()}")
        print("=" * 60)
        
        # Tavily results
        tavily = results["tavily"]
        print(f"🌐 TAVILY:")
        if tavily.get("success"):
            print(f"   ✅ Success")
            print(f"   📄 URL: {tavily.get('url', 'N/A')}")
            print(f"   📊 Content: {tavily.get('content_length', 0):,} characters")
            print(f"   ⏱️  Time: {tavily.get('execution_time', 0):.2f}s")
        else:
            print(f"   ❌ Failed: {tavily.get('error', 'Unknown error')}")
        
        # Bright Data results
        bright = results["bright"]
        print(f"\n🌟 BRIGHT DATA:")
        if not bright.get("available"):
            print(f"   ⚠️  Not available")
        elif bright.get("success"):
            print(f"   ✅ Success")
            print(f"   📄 URL: {bright.get('url', 'N/A')}")
            print(f"   📊 Content: {bright.get('content_length', 0):,} characters")
            print(f"   ⏱️  Time: {bright.get('execution_time', 0):.2f}s")
        else:
            print(f"   ❌ Failed: {bright.get('error', 'Unknown error')}")
        
        # Comparison
        comp = results["comparison"]
        print(f"\n⚖️  COMPARISON:")
        
        if comp["winner"] == "tie":
            print(f"   🤝 Result: TIE - Both performed similarly")
        elif comp["winner"] == "tavily":
            print(f"   🏆 Winner: TAVILY")
        elif comp["winner"] == "bright":
            print(f"   🏆 Winner: BRIGHT DATA")
        elif comp["winner"] == "tavily_only":
            print(f"   🏆 Winner: TAVILY (only available)")
        else:
            print(f"   💔 Result: Both failed")
        
        if comp.get("content_length_diff") is not None:
            diff = comp["content_length_diff"]
            if diff > 0:
                print(f"   📈 Bright Data got {diff:,} more characters")
            elif diff < 0:
                print(f"   📈 Tavily got {abs(diff):,} more characters")
            else:
                print(f"   📊 Same content length")
        
        if comp.get("speed_comparison"):
            speed = comp["speed_comparison"]
            print(f"   🏃 Faster: {speed['faster'].title()} ({speed[f'{speed['faster']}_time']:.2f}s)")
        
        if comp.get("content_similarity") is not None:
            similarity = comp["content_similarity"] * 100
            print(f"   🔍 Content similarity: {similarity:.1f}%")

async def main():
    """Run comparison tests"""
    
    print("🔥 SCRAPER COMPARISON TEST")
    print("Tavily vs Bright Data")
    print("=" * 50)
    
    comparison = ScraperComparison()
    
    # Test cases
    test_cases = [
        {
            "app_name": "TikTok",
            "url": "https://www.tiktok.com/legal/terms-of-service"
        },
        {
            "app_name": "Instagram", 
            "url": "https://help.instagram.com/581066165581870"
        },
        {
            "app_name": "Netflix",
            "url": None  # Test auto-discovery
        }
    ]
    
    all_results = []
    
    for test_case in test_cases:
        result = await comparison.test_app_scraping(
            test_case["app_name"], 
            test_case["url"]
        )
        
        comparison.print_results(result)
        all_results.append(result)
        
        # Delay between tests
        await asyncio.sleep(3)
    
    # Overall summary
    print(f"\n🏁 OVERALL SUMMARY")
    print("=" * 50)
    
    tavily_wins = sum(1 for r in all_results if r["comparison"]["winner"] == "tavily")
    bright_wins = sum(1 for r in all_results if r["comparison"]["winner"] == "bright")
    ties = sum(1 for r in all_results if r["comparison"]["winner"] == "tie")
    
    print(f"📊 Results out of {len(all_results)} tests:")
    print(f"   🌐 Tavily wins: {tavily_wins}")
    print(f"   🌟 Bright Data wins: {bright_wins}")
    print(f"   🤝 Ties: {ties}")
    
    if tavily_wins > bright_wins:
        print(f"\n🏆 Overall winner: TAVILY")
    elif bright_wins > tavily_wins:
        print(f"\n🏆 Overall winner: BRIGHT DATA")
    else:
        print(f"\n🤝 Overall result: TIE")
    
    # Cleanup
    await comparison.tavily.close()
    if comparison.bright_available:
        await comparison.bright.close()

if __name__ == "__main__":
    asyncio.run(main())