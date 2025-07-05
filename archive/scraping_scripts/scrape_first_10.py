#!/usr/bin/env python3
"""
Script to scrape terms and conditions for the first 10 apps.
"""
import asyncio
from dotenv import load_dotenv
from src.terms_analyzer.services.tavily_service import TavilyService

load_dotenv()

# First 10 apps from the list
FIRST_10_APPS = [
    "Google Play Services",
    "YouTube", 
    "Google Maps",
    "Google Chrome",
    "Gmail",
    "Google Photos",
    "Google Drive",
    "Google (Search)",
    "Google Calendar",
    "Google Meet"
]

async def scrape_app(tavily: TavilyService, app_name: str, index: int, total: int) -> dict:
    """Scrape terms for a single app with progress tracking"""
    print(f"\n[{index}/{total}] 🔍 Processing: {app_name}")
    
    try:
        terms_data = await tavily.find_terms_for_app(app_name, save_to_storage=True)
        
        if terms_data:
            print(f"✅ Successfully scraped {app_name}")
            print(f"   📄 URL: {terms_data['terms_url']}")
            print(f"   📊 Length: {len(terms_data['terms_text']):,} characters")
            print(f"   💾 Saved to: {terms_data['saved_path']}")
            return {
                "app_name": app_name,
                "status": "success",
                "url": terms_data['terms_url'],
                "length": len(terms_data['terms_text']),
                "saved_path": terms_data['saved_path']
            }
        else:
            print(f"❌ Failed to find terms for {app_name}")
            return {
                "app_name": app_name,
                "status": "failed",
                "error": "No terms found"
            }
    except Exception as e:
        print(f"❌ Error processing {app_name}: {str(e)}")
        return {
            "app_name": app_name,
            "status": "error",
            "error": str(e)
        }

async def main():
    print("🚀 Starting scraper for first 10 apps...")
    print(f"📋 Apps to process: {', '.join(FIRST_10_APPS)}")
    
    tavily = TavilyService()
    results = []
    successful = 0
    failed = 0
    
    for i, app_name in enumerate(FIRST_10_APPS, 1):
        result = await scrape_app(tavily, app_name, i, len(FIRST_10_APPS))
        results.append(result)
        
        if result["status"] == "success":
            successful += 1
        else:
            failed += 1
            
        # Add delay between requests to be respectful
        if i < len(FIRST_10_APPS):
            await asyncio.sleep(2)
    
    await tavily.close()
    
    # Print summary
    print(f"\n📊 SUMMARY:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 All terms saved to: terms_storage/")
    
    # Show successful extractions
    print(f"\n📄 SUCCESSFUL EXTRACTIONS:")
    print("-" * 50)
    for result in results:
        if result["status"] == "success":
            print(f"✅ {result['app_name']}")
            print(f"   File: {result['saved_path']}")
            print(f"   Size: {result['length']:,} characters")
    
    # Show failed extractions
    if failed > 0:
        print(f"\n❌ FAILED EXTRACTIONS:")
        print("-" * 50)
        for result in results:
            if result["status"] != "success":
                print(f"❌ {result['app_name']}: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())