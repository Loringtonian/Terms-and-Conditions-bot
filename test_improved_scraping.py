#!/usr/bin/env python3
"""
Test the improved scraping methodology on high-priority services.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / 'src'))

from terms_analyzer.services.improved_tavily_service import ImprovedTavilyService

async def test_improved_scraping():
    """Test improved scraping on key services that failed before."""
    
    # High-priority services that we know failed
    test_services = [
        "Facebook",
        "TikTok", 
        "Instagram",
        "Netflix",
        "Google Chrome",
        "Spotify"
    ]
    
    print("🧪 Testing Improved Scraping Methodology")
    print("=" * 50)
    
    service = ImprovedTavilyService()
    results = {}
    
    try:
        for app_name in test_services:
            print(f"\n🎯 Testing: {app_name}")
            print("-" * 30)
            
            # Test without saving to avoid conflicts
            result = await service.find_actual_terms_for_app(app_name, save_to_storage=False)
            
            if result:
                results[app_name] = {
                    "success": True,
                    "url": result["terms_url"],
                    "content_length": result["content_length"],
                    "quality_score": result["quality_score"],
                    "search_query": result["search_query"]
                }
                print(f"✅ SUCCESS!")
                print(f"   URL: {result['terms_url']}")
                print(f"   Content Length: {result['content_length']:,} chars")
                print(f"   Quality Score: {result['quality_score']:.1f}")
                print(f"   Found via: {result['search_query']}")
            else:
                results[app_name] = {
                    "success": False,
                    "reason": "No valid terms found"
                }
                print(f"❌ FAILED: No valid terms found")
    
    finally:
        await service.close()
    
    # Summary report
    print(f"\n📊 SUMMARY REPORT")
    print("=" * 50)
    
    successful = sum(1 for r in results.values() if r["success"])
    total = len(test_services)
    
    print(f"Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")
    print(f"\nSuccessful Services:")
    for app, result in results.items():
        if result["success"]:
            print(f"✅ {app}: {result['content_length']:,} chars from {result['url']}")
    
    print(f"\nFailed Services:")
    for app, result in results.items():
        if not result["success"]:
            print(f"❌ {app}: {result['reason']}")
    
    if successful > 0:
        print(f"\n🎉 Improved methodology is working! Ready for bulk re-scraping.")
    else:
        print(f"\n😞 Need to further refine the methodology.")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_improved_scraping())