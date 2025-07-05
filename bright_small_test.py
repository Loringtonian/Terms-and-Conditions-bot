#!/usr/bin/env python3
"""
Test Bright Data scraper with first few apps from the list
"""
import asyncio
import os
from dotenv import load_dotenv
from src.terms_analyzer.services.bright_service import BrightDataService

load_dotenv()

async def test_first_apps():
    print("🚀 Testing Bright Data with first 5 apps...")
    
    # First 5 apps from the list
    test_apps = [
        "Google Play Services",
        "YouTube", 
        "Google Maps",
        "Google Chrome",
        "Gmail"
    ]
    
    try:
        service = BrightDataService()
        results = []
        
        for i, app in enumerate(test_apps, 1):
            print(f"\n📱 [{i}/{len(test_apps)}] Testing: {app}")
            print("-" * 50)
            
            try:
                result = await service.scrape_and_save_terms(app)
                
                if result:
                    print(f"✅ SUCCESS: {app} → {result}")
                    results.append({"app": app, "status": "success", "path": result})
                else:
                    print(f"❌ FAILED: {app} - No terms found")
                    results.append({"app": app, "status": "failed", "reason": "No terms found"})
                    
            except Exception as e:
                print(f"❌ ERROR: {app} - {str(e)}")
                results.append({"app": app, "status": "error", "reason": str(e)})
            
            # Increased delay between apps to prevent rate limiting
            await asyncio.sleep(10)
        
        await service.close()
        
        # Summary
        print(f"\n📊 SUMMARY")
        print("=" * 50)
        successful = len([r for r in results if r["status"] == "success"])
        print(f"✅ Successful: {successful}/{len(test_apps)}")
        print(f"❌ Failed: {len(test_apps) - successful}/{len(test_apps)}")
        
        for result in results:
            status_emoji = "✅" if result["status"] == "success" else "❌"
            print(f"{status_emoji} {result['app']}: {result['status']}")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_first_apps())