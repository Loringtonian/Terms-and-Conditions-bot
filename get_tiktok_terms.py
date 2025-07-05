#!/usr/bin/env python3
"""
Script to fetch TikTok Terms and Conditions using Tavily
"""
import asyncio
from dotenv import load_dotenv
from src.terms_analyzer.services.tavily_service import TavilyService

load_dotenv()

async def main():
    tavily = TavilyService()
    
    print("🔍 Searching for TikTok Terms and Conditions...")
    
    # Search for TikTok terms
    terms_data = await tavily.find_terms_for_app("TikTok")
    
    if terms_data:
        print(f"\n✅ Found TikTok terms:")
        print(f"📄 URL: {terms_data['terms_url']}")
        print(f"📊 Content length: {len(terms_data['terms_text']):,} characters")
        print(f"\n📝 Preview:")
        print(terms_data['terms_text'][:1000] + "...")
        
        # Save to file
        with open("tiktok_terms.txt", "w", encoding="utf-8") as f:
            f.write(f"TikTok Terms and Conditions\n")
            f.write(f"Source: {terms_data['terms_url']}\n")
            f.write(f"Retrieved via Tavily\n")
            f.write("=" * 50 + "\n\n")
            f.write(terms_data['terms_text'])
        
        print(f"\n💾 Saved to: tiktok_terms.txt")
        
    else:
        print("❌ Could not find TikTok terms and conditions")
    
    await tavily.close()

if __name__ == "__main__":
    asyncio.run(main())