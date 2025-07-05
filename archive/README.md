# Archive Directory

This directory contains archived files from the terms and conditions scraping project.

## Contents

### scraping_scripts/
Temporary scripts used during the bulk scraping process:
- `check_remaining.py` - Script to check remaining apps to scrape
- `finish_scraping.py` - Script to complete the final apps
- `resume_scraping.py` - Resilient script with retry logic
- `scrape_first_10.py` - Initial test script for first 10 apps
- `scrape_remaining_apps.py` - Bulk scraping script

## Scraping Results Summary
- **Total Apps:** 100
- **Successfully Scraped:** 97 (97% success rate)
- **Failed:** 3 (PUBG MOBILE, Uber Eats, WeChat)
- **Storage Location:** `../terms_storage/`

## Date Archived
July 5, 2025

## Note
These scripts were used for the one-time bulk scraping of terms and conditions. The functional production script `scrape_terms.py` remains in the main directory.