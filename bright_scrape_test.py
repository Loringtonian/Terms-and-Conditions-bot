#!/usr/bin/env python3
"""
Test script for Bright Data scraping service.
Parallel to the Tavily test, but using Bright Data Browser API.
"""
import asyncio
import os
from dotenv import load_dotenv
from src.terms_analyzer.services.bright_service import BrightDataService

load_dotenv()

async def test_bright_scraping():
    """Test Bright Data scraping with a known terms URL"""
    
    # Check if credentials are available
    auth = os.getenv("BRIGHT_DATA_AUTH")
    if not auth:
        print("❌ BRIGHT_DATA_AUTH environment variable not set")
        print("Please add your Bright Data credentials to .env file:")
        print("BRIGHT_DATA_AUTH=brd-customer-hl_ccf234f3-zone-terms_and_conditions:r5tk64g5ywyt")
        return
    
    print("🚀 Testing Bright Data scraping service...")
    print(f"📊 Using auth: {auth[:20]}...")
    
    try:
        # Initialize service
        bright_service = BrightDataService()
        
        # Test with TikTok terms (known working URL)
        app_name = "TikTok"
        terms_url = "https://www.tiktok.com/legal/terms-of-service"
        
        print(f"\n🔍 Testing with {app_name} terms...")
        print(f"📄 URL: {terms_url}")
        
        # Scrape terms
        result = await bright_service.scrape_terms_for_app(app_name, terms_url)
        
        if result:
            print(f"\n✅ SUCCESS!")
            print(f"📱 App: {result['app_name']}")
            print(f"🌐 URL: {result['terms_url']}")
            print(f"📊 Content length: {len(result['terms_text']):,} characters")
            print(f"🕒 Scraped at: {result['metadata']['scraped_at']}")
            
            # Show preview
            preview = result['terms_text'][:500]
            print(f"\n📝 Content preview:")
            print("-" * 50)
            print(f"{preview}...")
            print("-" * 50)
            
            # Save to bright_storage
            print(f"\n💾 Saving to bright_storage...")
            saved_path = await bright_service.scrape_and_save_terms(app_name, terms_url)
            
            if saved_path:
                print(f"✅ Saved to: {saved_path}")
            else:
                print("❌ Failed to save")
                
        else:
            print(f"❌ Failed to scrape terms for {app_name}")
        
        await bright_service.close()
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_auto_discovery():
    """Test automatic discovery of terms URLs"""
    
    print("\n🔍 Testing automatic terms discovery...")
    
    try:
        bright_service = BrightDataService()
        
        # Test auto-discovery for an app without providing URL
        app_name = "Spotify"
        
        print(f"🎵 Testing auto-discovery for {app_name}...")
        
        result = await bright_service.scrape_terms_for_app(app_name)
        
        if result:
            print(f"✅ Auto-discovered terms for {app_name}!")
            print(f"🌐 Found URL: {result['terms_url']}")
            print(f"📊 Content length: {len(result['terms_text']):,} characters")
        else:
            print(f"❌ Could not auto-discover terms for {app_name}")
        
        await bright_service.close()
        
    except Exception as e:
        print(f"❌ Error during auto-discovery test: {str(e)}")

async def compare_with_existing():
    """Compare Bright Data results with existing Tavily results"""
    
    print("\n⚖️  Comparing Bright Data with existing results...")
    
    # Check if we have existing TikTok results from Tavily
    tavily_file = "terms_storage/tiktok.md"
    bright_file = "bright_storage/tiktok.md"
    
    if os.path.exists(tavily_file):
        print(f"📄 Found existing Tavily result: {tavily_file}")
        
        # Read Tavily result
        with open(tavily_file, 'r', encoding='utf-8') as f:
            tavily_content = f.read()
        
        print(f"📊 Tavily content length: {len(tavily_content):,} characters")
    else:
        print("❌ No existing Tavily results found for comparison")
    
    if os.path.exists(bright_file):
        print(f"📄 Found Bright Data result: {bright_file}")
        
        # Read Bright Data result
        with open(bright_file, 'r', encoding='utf-8') as f:
            bright_content = f.read()
        
        print(f"📊 Bright Data content length: {len(bright_content):,} characters")
        
        if os.path.exists(tavily_file):
            # Simple comparison
            if len(bright_content) > len(tavily_content):
                print("🏆 Bright Data retrieved more content")
            elif len(tavily_content) > len(bright_content):
                print("🏆 Tavily retrieved more content")
            else:
                print("🤝 Similar content length")
    else:
        print("❌ No Bright Data results found for comparison")

async def main():
    """Run all tests"""
    
    print("🌟 BRIGHT DATA SCRAPING TEST SUITE")
    print("=" * 50)
    
    # Test 1: Basic scraping with known URL
    await test_bright_scraping()
    
    # Test 2: Auto-discovery
    await test_auto_discovery()
    
    # Test 3: Comparison with existing results
    await compare_with_existing()
    
    print("\n🏁 Testing complete!")

if __name__ == "__main__":
    asyncio.run(main())