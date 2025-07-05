#!/usr/bin/env python3
"""
Quick test to verify Bright Data is still working with TikTok
"""
import asyncio
import os
from dotenv import load_dotenv
from src.terms_analyzer.services.bright_service import BrightDataService

load_dotenv()

async def test_tiktok():
    print("🚀 Quick Bright Data test with TikTok...")
    
    try:
        service = BrightDataService()
        
        # Test the exact same TikTok URL that worked before
        result = await service.scrape_terms_for_app("TikTok", "https://www.tiktok.com/legal/terms-of-service")
        
        if result:
            print(f"✅ SUCCESS: Got {len(result['terms_text']):,} characters")
            print(f"🌐 URL: {result['terms_url']}")
            print(f"📝 Preview: {result['terms_text'][:200]}...")
            
            # Try to save it
            saved_path = await service.scrape_and_save_terms("TikTok", "https://www.tiktok.com/legal/terms-of-service")
            if saved_path:
                print(f"💾 Saved to: {saved_path}")
            
        else:
            print("❌ FAILED: No result returned")
        
        await service.close()
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tiktok())