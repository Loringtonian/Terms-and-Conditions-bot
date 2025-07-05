#!/usr/bin/env python3
"""
Resilient script to resume scraping remaining apps with better error handling.
"""
import asyncio
import time
from pathlib import Path
from dotenv import load_dotenv
from src.terms_analyzer.services.tavily_service import TavilyService
from src.terms_analyzer.utils.storage import StorageManager

load_dotenv()

# Full app list
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

def get_processed_apps():
    """Get list of already processed apps"""
    storage = StorageManager()
    processed = []
    
    for app in ALL_APPS:
        if storage.load_terms(app):
            processed.append(app)
    
    return processed

async def scrape_with_retry(tavily: TavilyService, app_name: str, max_retries: int = 3) -> dict:
    """Scrape an app with retry logic for network failures"""
    
    for attempt in range(max_retries):
        try:
            print(f"🔍 Processing: {app_name} (attempt {attempt + 1}/{max_retries})")
            
            terms_data = await tavily.find_terms_for_app(app_name, save_to_storage=True)
            
            if terms_data:
                print(f"✅ Success: {app_name}")
                print(f"   📄 URL: {terms_data['terms_url']}")
                print(f"   📊 Length: {len(terms_data['terms_text']):,} chars")
                return {
                    "app_name": app_name,
                    "status": "success",
                    "url": terms_data['terms_url'],
                    "length": len(terms_data['terms_text']),
                    "saved_path": terms_data['saved_path']
                }
            else:
                print(f"❌ No terms found: {app_name}")
                return {
                    "app_name": app_name,
                    "status": "no_terms",
                    "error": "No terms found"
                }
                
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️  Error on attempt {attempt + 1}: {app_name} - {error_msg}")
            
            if "nodename nor servname" in error_msg or "Connection" in error_msg:
                # Network error - wait and retry
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # Progressive backoff
                    print(f"⏳ Network error, waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                    continue
            else:
                # Non-network error - don't retry
                break
    
    # All retries failed
    return {
        "app_name": app_name,
        "status": "failed",
        "error": f"Failed after {max_retries} attempts"
    }

async def main():
    print("🔄 Resuming bulk scraping with improved error handling...")
    
    # Get remaining apps
    processed = get_processed_apps()
    remaining = [app for app in ALL_APPS if app not in processed]
    
    print(f"📊 Status:")
    print(f"   📱 Total apps: {len(ALL_APPS)}")
    print(f"   ✅ Processed: {len(processed)}")
    print(f"   ⏳ Remaining: {len(remaining)}")
    
    if not remaining:
        print("🎉 All apps already processed!")
        return
    
    # Initialize service
    tavily = TavilyService()
    results = []
    successful = 0
    failed = 0
    
    print(f"\n🚀 Starting to process {len(remaining)} remaining apps...")
    
    for i, app_name in enumerate(remaining, 1):
        print(f"\n[{i}/{len(remaining)}] Processing: {app_name}")
        
        result = await scrape_with_retry(tavily, app_name)
        results.append(result)
        
        if result["status"] == "success":
            successful += 1
        else:
            failed += 1
            
        # Progress update every 10 apps
        if i % 10 == 0:
            print(f"\n📈 Progress: {i}/{len(remaining)} apps processed")
            print(f"   ✅ Success: {successful}")
            print(f"   ❌ Failed: {failed}")
        
        # Respectful delay between requests
        await asyncio.sleep(3)
    
    await tavily.close()
    
    # Final summary
    total_processed = len(get_processed_apps())
    print(f"\n🏁 SCRAPING COMPLETE!")
    print(f"✅ This session: {successful} successful, {failed} failed")
    print(f"📱 Total processed: {total_processed}/{len(ALL_APPS)}")
    
    # Save results
    with open("final_scraping_results.txt", "w") as f:
        f.write(f"Final Scraping Results\n")
        f.write(f"=====================\n\n")
        f.write(f"Total apps: {len(ALL_APPS)}\n")
        f.write(f"Successfully processed: {total_processed}\n")
        f.write(f"This session successful: {successful}\n")
        f.write(f"This session failed: {failed}\n\n")
        
        if successful > 0:
            f.write("SUCCESSFUL THIS SESSION:\n")
            f.write("-" * 30 + "\n")
            for result in results:
                if result["status"] == "success":
                    f.write(f"✅ {result['app_name']}\n")
        
        if failed > 0:
            f.write(f"\nFAILED THIS SESSION:\n")
            f.write("-" * 30 + "\n")
            for result in results:
                if result["status"] != "success":
                    f.write(f"❌ {result['app_name']}: {result.get('error', 'Unknown')}\n")
    
    if total_processed == len(ALL_APPS):
        print("🎉 ALL APPS SUCCESSFULLY SCRAPED!")
    else:
        print(f"⚠️  {len(ALL_APPS) - total_processed} apps still need attention")

if __name__ == "__main__":
    asyncio.run(main())