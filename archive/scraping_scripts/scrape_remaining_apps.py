#!/usr/bin/env python3
"""
Script to scrape terms and conditions for remaining apps.
Skips apps that are already processed.
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from src.terms_analyzer.services.tavily_service import TavilyService
from src.terms_analyzer.utils.storage import StorageManager

load_dotenv()

# Full app list from terms_and_conditions.md
ALL_APPS = [
    "Google Play Services", "YouTube", "Google Maps", "Google Chrome", "Gmail", 
    "Google Photos", "Google Drive", "Google (Search)", "Google Calendar", "Google Meet", 
    "Google Messages", "Google Pay", "Google Assistant", "Google Translate", "Google Keep", 
    "Google Docs", "Google Sheets", "Google Slides", "YouTube Music", "Gboard", 
    "Android System WebView", "Android Accessibility Suite", "Speech Services by Google", 
    "Facebook", "Messenger", "WhatsApp Messenger", "WhatsApp Business", "Instagram", 
    "Threads", "TikTok", "Snapchat", "X", "Telegram", "LinkedIn", "Zoom", 
    "Microsoft Teams", "Microsoft Word", "Microsoft Excel", "Microsoft PowerPoint", 
    "Microsoft OneDrive", "Microsoft Outlook", "Dropbox", "PayPal", "Amazon Shopping", 
    "eBay", "SHEIN", "DoorDash", "Uber", "Lyft", "Spotify", "Netflix", 
    "Disney+", "Peacock TV", "Max", "Hulu", "Prime Video", "CapCut", "Canva", 
    "Picsart", "SHAREit", "MX Player", "Truecaller", "Google One", "Google Lens", 
    "Tinder", "Bumble", "Hinge", "Duolingo", "Audible", "Kindle", "Shazam", 
    "Google TV", "Crunchyroll", "Roblox", "Fortnite", "PUBG MOBILE", "Free Fire", 
    "Candy Crush Saga", "Subway Surfers", "Temple Run 2", "Clash of Clans", 
    "Clash Royale", "8 Ball Pool", "Hill Climb Racing", "Pokémon GO", "Royal Match", 
    "Last War: Survival", "Block Blast", "IceBlock", "Kingshot", "Coin Master", 
    "Whiteout Survival", "Paramount+", "Airbnb", "Waze", "Google Maps Go", 
    "Files by Google", "Genshin Impact", "Uber Eats", "WeChat"
]

def get_already_processed_apps():
    """Get list of apps that have already been processed"""
    storage = StorageManager()
    processed = []
    
    for app in ALL_APPS:
        if storage.load_terms(app):
            processed.append(app)
    
    return processed

def get_remaining_apps():
    """Get list of apps that still need to be processed"""
    processed = get_already_processed_apps()
    remaining = [app for app in ALL_APPS if app not in processed]
    
    print(f"📋 Total apps: {len(ALL_APPS)}")
    print(f"✅ Already processed: {len(processed)}")
    print(f"⏳ Remaining to process: {len(remaining)}")
    
    if processed:
        print(f"\n📄 Already processed apps:")
        for app in processed:
            print(f"   ✅ {app}")
    
    return remaining

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
    print("🚀 Starting bulk scraper for remaining apps...")
    
    # Get remaining apps to process
    remaining_apps = get_remaining_apps()
    
    if not remaining_apps:
        print("🎉 All apps have already been processed!")
        return
    
    print(f"\n📋 Apps to process: {len(remaining_apps)}")
    
    # Initialize service
    tavily = TavilyService()
    results = []
    successful = 0
    failed = 0
    
    # Process each remaining app
    for i, app_name in enumerate(remaining_apps, 1):
        result = await scrape_app(tavily, app_name, i, len(remaining_apps))
        results.append(result)
        
        if result["status"] == "success":
            successful += 1
        else:
            failed += 1
            
        # Add delay between requests to be respectful to API
        if i < len(remaining_apps):
            await asyncio.sleep(2)
    
    await tavily.close()
    
    # Print summary
    print(f"\n📊 BATCH SCRAPING COMPLETE!")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 All terms saved to: terms_storage/")
    
    # Save detailed results
    with open("bulk_scraping_results.txt", "w", encoding="utf-8") as f:
        f.write(f"Bulk Terms and Conditions Scraping Results\n")
        f.write(f"=========================================\n\n")
        f.write(f"Total remaining apps processed: {len(remaining_apps)}\n")
        f.write(f"Successful: {successful}\n")
        f.write(f"Failed: {failed}\n\n")
        
        if successful > 0:
            f.write("SUCCESSFUL EXTRACTIONS:\n")
            f.write("-" * 50 + "\n")
            for result in results:
                if result["status"] == "success":
                    f.write(f"✅ {result['app_name']}\n")
                    f.write(f"   URL: {result['url']}\n")
                    f.write(f"   Length: {result['length']:,} characters\n")
                    f.write(f"   Saved: {result['saved_path']}\n\n")
        
        if failed > 0:
            f.write("FAILED EXTRACTIONS:\n")
            f.write("-" * 50 + "\n")
            for result in results:
                if result["status"] != "success":
                    f.write(f"❌ {result['app_name']}: {result.get('error', 'Unknown error')}\n")
    
    print(f"📋 Detailed results saved to: bulk_scraping_results.txt")
    
    # Final summary
    total_processed = len(get_already_processed_apps())
    print(f"\n🎯 FINAL STATUS:")
    print(f"📱 Total apps in list: {len(ALL_APPS)}")
    print(f"✅ Successfully processed: {total_processed}")
    print(f"❌ Failed/Missing: {len(ALL_APPS) - total_processed}")
    
    if total_processed == len(ALL_APPS):
        print("🎉 ALL APPS SUCCESSFULLY SCRAPED!")
    else:
        print(f"⚠️  {len(ALL_APPS) - total_processed} apps still need attention")

if __name__ == "__main__":
    asyncio.run(main())