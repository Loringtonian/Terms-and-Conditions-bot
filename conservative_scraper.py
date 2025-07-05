#!/usr/bin/env python3
"""
Conservative Bright Data scraper that respects rate limits.
This version uses much slower, sustainable scraping to avoid rate limits.
"""
import asyncio
import time
import logging
from datetime import datetime, timedelta
from bright_bulk_scraper import BrightBulkScraper

# Configure logging with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def log_with_timestamp(message):
    """Print message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")
    logger.info(message)

async def run_conservative_scraping():
    """Run bulk scraping with conservative rate limits"""
    log_with_timestamp("🐌 CONSERVATIVE BRIGHT DATA SCRAPING")
    log_with_timestamp("=" * 60)
    log_with_timestamp("⏰ This version uses slower, sustainable scraping")
    log_with_timestamp("📊 Batch size: 2 apps")
    log_with_timestamp("⏳ Delay between batches: 60 seconds (increased)")
    log_with_timestamp("🔄 Delay between apps: 15 seconds (increased)")
    log_with_timestamp("💡 This should avoid rate limits completely")
    log_with_timestamp("=" * 60)
    
    # Calculate estimated time
    total_apps = 100  # From your list
    batch_size = 2
    batches = (total_apps + batch_size - 1) // batch_size
    
    # Time per app: ~60s scraping + 15s delay = 75s per app  
    # Time per batch: 2 apps * 75s = 150s + 60s inter-batch delay = 210s per batch
    total_time_seconds = batches * 210
    total_time_hours = total_time_seconds / 3600
    
    log_with_timestamp(f"📈 Estimated total time: {total_time_hours:.1f} hours ({batches} batches)")
    log_with_timestamp(f"🏁 Estimated completion: {(datetime.now() + timedelta(seconds=total_time_seconds)).strftime('%Y-%m-%d %H:%M:%S')}")
    log_with_timestamp("")
    
    # Auto-confirm for background processing
    log_with_timestamp("🚀 Starting conservative scraping automatically...")
    
    start_time = time.time()
    scraper = BrightBulkScraper()
    
    try:
        # Run with more conservative settings to avoid rate limits
        results = await scraper.run_bulk_scraping(
            start_index=0,
            batch_size=1  # Single app per batch to avoid rate limits
        )
        
        await scraper.generate_summary_report(results)
        
        total_time = time.time() - start_time
        print(f"\n🎉 Conservative scraping completed in {total_time/3600:.1f} hours")
        
    except Exception as e:
        print(f"❌ Error during conservative scraping: {e}")
    finally:
        await scraper.cleanup()

def estimate_retry_time():
    """Estimate when we can retry based on rate limits"""
    print("⏰ RATE LIMIT RECOVERY ESTIMATION")
    print("=" * 50)
    print("Based on observed rate limit patterns:")
    print()
    print("🔄 Domain cooldowns: ~5-15 minutes")
    print("📊 Navigation limits: Reset every ~20 minutes (session timeout)")
    print("🚫 Account limits: May need 1-24 hours depending on usage")
    print()
    
    now = datetime.now()
    recommended_times = [
        ("Conservative retry", now + timedelta(minutes=30)),
        ("Safe retry", now + timedelta(hours=2)),
        ("Guaranteed fresh start", now + timedelta(hours=24))
    ]
    
    for desc, time_est in recommended_times:
        print(f"✅ {desc}: {time_est.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print()
    print("💡 Recommendation: Wait at least 30 minutes, then use conservative mode")

if __name__ == "__main__":
    print("🚀 AUTOMATED CONSERVATIVE BRIGHT DATA SCRAPING")
    print("=" * 60)
    asyncio.run(run_conservative_scraping())