#!/usr/bin/env python3
"""
Finish scraping the final 13 apps
"""
import asyncio
from dotenv import load_dotenv
from src.terms_analyzer.services.tavily_service import TavilyService

load_dotenv()

FINAL_APPS = [
    "PUBG MOBILE",
    "Last War: Survival", 
    "Block Blast",
    "IceBlock",
    "Kingshot",
    "Coin Master",
    "Airbnb",
    "Waze",
    "Google Maps Go",
    "Files by Google",
    "Genshin Impact",
    "Uber Eats",
    "WeChat"
]

async def scrape_final_apps():
    print("🏁 Finishing the final 13 apps...")
    
    tavily = TavilyService()
    successful = 0
    failed = 0
    
    for i, app_name in enumerate(FINAL_APPS, 1):
        print(f"\n[{i}/13] 🔍 Processing: {app_name}")
        
        try:
            terms_data = await tavily.find_terms_for_app(app_name, save_to_storage=True)
            
            if terms_data:
                print(f"✅ Success: {app_name}")
                print(f"   📄 URL: {terms_data['terms_url']}")
                print(f"   📊 Length: {len(terms_data['terms_text']):,} chars")
                successful += 1
            else:
                print(f"❌ No terms found: {app_name}")
                failed += 1
                
        except Exception as e:
            print(f"❌ Error: {app_name} - {str(e)}")
            failed += 1
            
        await asyncio.sleep(3)  # Respectful delay
    
    await tavily.close()
    
    print(f"\n🏁 FINAL BATCH COMPLETE!")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    
    return successful, failed

if __name__ == "__main__":
    asyncio.run(scrape_final_apps())