#!/usr/bin/env python3
"""
Bright Data bulk scraper for all apps in the terms_and_conditions.md list.
Parallel to the Tavily bulk scraper, using Bright Data Browser API.
"""
import asyncio
import os
import time
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
from src.terms_analyzer.services.bright_service import BrightDataService

load_dotenv()

class BrightBulkScraper:
    def __init__(self):
        """Initialize the Bright Data bulk scraper"""
        try:
            self.bright_service = BrightDataService()
            print("✅ Bright Data service initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Bright Data service: {str(e)}")
            raise
        
        self.apps_list = self._load_apps_list()
        self.successful_scrapes = 0
        self.failed_scrapes = 0
        self.start_time = time.time()
    
    def _load_apps_list(self) -> List[str]:
        """Load and parse the apps list from terms_and_conditions.md"""
        try:
            with open("terms_and_conditions.md", "r", encoding="utf-8") as f:
                content = f.read().strip()
            
            # Parse the comma-separated list
            all_apps = [app.strip() for app in content.split(",")]
            print(f"📱 Loaded {len(all_apps)} total apps from list")
            
            # Check which apps are already scraped
            already_scraped = self._get_already_scraped_apps()
            remaining_apps = [app for app in all_apps if app not in already_scraped]
            
            print(f"✅ Already scraped: {len(already_scraped)} apps")
            print(f"🔄 Remaining to scrape: {len(remaining_apps)} apps")
            
            if already_scraped:
                print(f"📋 Skipping: {', '.join(already_scraped[:5])}{' ...' if len(already_scraped) > 5 else ''}")
            
            return remaining_apps
        except Exception as e:
            print(f"❌ Error loading apps list: {str(e)}")
            return []
    
    def _get_already_scraped_apps(self) -> List[str]:
        """Get list of apps that have already been scraped"""
        import os
        from pathlib import Path
        
        storage_dir = Path("bright_storage")
        if not storage_dir.exists():
            return []
        
        already_scraped = []
        for file_path in storage_dir.glob("*.md"):
            # Convert filename back to app name
            # e.g., "google_play_services.md" -> "Google Play Services"
            filename = file_path.stem
            
            # Convert underscores to spaces and title case
            app_name = filename.replace("_", " ").title()
            
            # Handle special cases for better matching
            app_name_corrections = {
                "Google Play Services": "Google Play Services",
                "Youtube": "YouTube", 
                "Tiktok": "TikTok",
                "Pubg Mobile": "PUBG Mobile",
                "Peacock Tv": "Peacock TV",
                "X": "X"
            }
            
            app_name = app_name_corrections.get(app_name, app_name)
            already_scraped.append(app_name)
        
        return already_scraped
    
    async def scrape_app_with_retry(self, app_name: str, max_retries: int = 1) -> Dict:
        """
        Scrape a single app with retry logic
        
        Args:
            app_name: Name of the app to scrape
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary with scraping results
        """
        for attempt in range(max_retries + 1):
            try:
                print(f"\n🔍 [{attempt + 1}/{max_retries + 1}] Scraping: {app_name}")
                
                result = await self.bright_service.scrape_and_save_terms(app_name)
                
                if result:
                    self.successful_scrapes += 1
                    print(f"✅ SUCCESS: {app_name} → {result}")
                    return {
                        "app_name": app_name,
                        "status": "success",
                        "file_path": str(result),
                        "attempt": attempt + 1
                    }
                else:
                    print(f"❌ No terms found for {app_name}")
                    
            except Exception as e:
                print(f"❌ Error scraping {app_name} (attempt {attempt + 1}): {str(e)}")
                
                if attempt < max_retries:
                    wait_time = 30  # Longer retry delay for rate limits
                    print(f"⏳ Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
        
        # All attempts failed
        self.failed_scrapes += 1
        return {
            "app_name": app_name,
            "status": "failed",
            "attempts": max_retries + 1
        }
    
    async def run_bulk_scraping(self, start_index: int = 0, batch_size: int = 5):
        """
        Run bulk scraping with rate limiting and progress tracking
        
        Args:
            start_index: Index to start scraping from (for resume functionality)
            batch_size: Number of concurrent scraping operations
        """
        print(f"🚀 BRIGHT DATA BULK SCRAPING")
        print(f"📱 Total apps: {len(self.apps_list)}")
        print(f"🔄 Starting from index: {start_index}")
        print(f"⚡ Batch size: {batch_size}")
        print("=" * 60)
        
        apps_to_process = self.apps_list[start_index:]
        results = []
        
        # Process in batches to respect rate limits
        for i in range(0, len(apps_to_process), batch_size):
            batch = apps_to_process[i:i + batch_size]
            batch_number = (i // batch_size) + 1
            total_batches = (len(apps_to_process) + batch_size - 1) // batch_size
            
            print(f"\n📦 BATCH {batch_number}/{total_batches}: {len(batch)} apps")
            print(f"📋 Apps: {', '.join(batch)}")
            
            # Create tasks for this batch
            tasks = [self.scrape_app_with_retry(app) for app in batch]
            
            # Run batch concurrently
            batch_start = time.time()
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            batch_time = time.time() - batch_start
            
            # Process results
            for result in batch_results:
                if isinstance(result, Exception):
                    print(f"❌ Batch error: {str(result)}")
                    self.failed_scrapes += 1
                else:
                    results.append(result)
            
            # Progress update
            current_app = start_index + i + len(batch)
            total_progress = (current_app / len(self.apps_list)) * 100
            
            print(f"\n📊 BATCH {batch_number} COMPLETE")
            print(f"⏱️  Batch time: {batch_time:.1f}s")
            print(f"✅ Success: {self.successful_scrapes}")
            print(f"❌ Failed: {self.failed_scrapes}")
            print(f"📈 Overall progress: {total_progress:.1f}% ({current_app}/{len(self.apps_list)})")
            
            # Much longer delay to respect rate limits
            if i + batch_size < len(apps_to_process):
                delay = 120  # 2 minute delay between batches to respect rate limits
                print(f"⏳ Waiting {delay}s before next batch to respect rate limits...")
                await asyncio.sleep(delay)
        
        return results
    
    async def generate_summary_report(self, results: List[Dict]):
        """Generate a summary report of the scraping session"""
        total_time = time.time() - self.start_time
        
        print(f"\n" + "=" * 60)
        print(f"🏁 BRIGHT DATA BULK SCRAPING COMPLETE")
        print(f"=" * 60)
        print(f"📱 Total apps processed: {len(self.apps_list)}")
        print(f"✅ Successful scrapes: {self.successful_scrapes}")
        print(f"❌ Failed scrapes: {self.failed_scrapes}")
        print(f"📊 Success rate: {(self.successful_scrapes / len(self.apps_list) * 100):.1f}%")
        print(f"⏱️  Total time: {total_time / 60:.1f} minutes")
        print(f"⚡ Average time per app: {total_time / len(self.apps_list):.1f}s")
        
        # List failed apps
        failed_apps = [r["app_name"] for r in results if r["status"] == "failed"]
        if failed_apps:
            print(f"\n❌ Failed apps ({len(failed_apps)}):")
            for app in failed_apps:
                print(f"   • {app}")
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"bright_scraping_report_{timestamp}.txt"
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(f"Bright Data Bulk Scraping Report\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(f"Total apps: {len(self.apps_list)}\n")
            f.write(f"Successful: {self.successful_scrapes}\n")
            f.write(f"Failed: {self.failed_scrapes}\n")
            f.write(f"Success rate: {(self.successful_scrapes / len(self.apps_list) * 100):.1f}%\n")
            f.write(f"Total time: {total_time / 60:.1f} minutes\n\n")
            
            if failed_apps:
                f.write("Failed apps:\n")
                for app in failed_apps:
                    f.write(f"- {app}\n")
        
        print(f"📄 Report saved to: {report_file}")
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.bright_service.close()

async def main():
    """Main execution function"""
    scraper = None
    
    try:
        scraper = BrightBulkScraper()
        
        # Check if we have any apps to process
        if not scraper.apps_list:
            print("❌ No apps found to process")
            return
        
        # Run the bulk scraping with conservative rate limits
        results = await scraper.run_bulk_scraping(
            start_index=0,  # Start from beginning
            batch_size=2    # Conservative batch size to respect rate limits
        )
        
        # Generate summary report
        await scraper.generate_summary_report(results)
        
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if scraper:
            await scraper.cleanup()

if __name__ == "__main__":
    asyncio.run(main())