#!/usr/bin/env python3
"""
Script to scrape terms and conditions for multiple apps.
Reads app list from terms_and_conditions.md and saves each as structured markdown.
"""
import asyncio
import re
from pathlib import Path
from dotenv import load_dotenv
from src.terms_analyzer.services.tavily_service import TavilyService

load_dotenv()

def parse_app_list(file_path: str) -> list[str]:
    """Parse the app list from terms_and_conditions.md"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract the comma-separated app list (assuming it's on line 2)
        lines = content.strip().split('\n')
        if len(lines) >= 2:
            app_line = lines[1]  # Second line contains the app list
            apps = [app.strip() for app in app_line.split(',')]
            return [app for app in apps if app]  # Remove empty strings
        return []
    except Exception as e:
        print(f"Error parsing app list: {e}")
        return []

async def scrape_single_app(tavily: TavilyService, app_name: str) -> dict:
    """Scrape terms for a single app"""
    print(f"\n🔍 Processing: {app_name}")
    
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
    # Parse the app list
    app_list = parse_app_list("terms_and_conditions.md")
    
    if not app_list:
        print("❌ No apps found in terms_and_conditions.md")
        return
    
    print(f"📋 Found {len(app_list)} apps to process")
    
    # Initialize the service
    tavily = TavilyService()
    
    # Process apps
    results = []
    successful = 0
    failed = 0
    
    for i, app_name in enumerate(app_list, 1):
        print(f"\n[{i}/{len(app_list)}] Processing: {app_name}")
        
        result = await scrape_single_app(tavily, app_name)
        results.append(result)
        
        if result["status"] == "success":
            successful += 1
        else:
            failed += 1
            
        # Add a small delay to be respectful to the API
        await asyncio.sleep(1)
    
    # Clean up
    await tavily.close()
    
    # Print summary
    print(f"\n📊 SUMMARY:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Terms saved to: terms_storage/")
    
    # Save detailed results
    with open("scraping_results.txt", "w", encoding="utf-8") as f:
        f.write(f"Terms and Conditions Scraping Results\n")
        f.write(f"=====================================\n\n")
        f.write(f"Total apps processed: {len(app_list)}\n")
        f.write(f"Successful: {successful}\n")
        f.write(f"Failed: {failed}\n\n")
        
        f.write("SUCCESSFUL EXTRACTIONS:\n")
        f.write("-" * 50 + "\n")
        for result in results:
            if result["status"] == "success":
                f.write(f"✅ {result['app_name']}\n")
                f.write(f"   URL: {result['url']}\n")
                f.write(f"   Length: {result['length']:,} characters\n")
                f.write(f"   Saved: {result['saved_path']}\n\n")
        
        f.write("\nFAILED EXTRACTIONS:\n")
        f.write("-" * 50 + "\n")
        for result in results:
            if result["status"] != "success":
                f.write(f"❌ {result['app_name']}: {result.get('error', 'Unknown error')}\n")
    
    print(f"📋 Detailed results saved to: scraping_results.txt")

if __name__ == "__main__":
    asyncio.run(main())