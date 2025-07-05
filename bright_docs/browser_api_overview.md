# Bright Data Browser API Documentation

## Overview
Bright Data's Browser API is a scraping browser that works like other automated browsers and is controlled by common high-level APIs like Puppeteer and Playwright, but is the only browser with built-in website unblocking capabilities.

## Key Features
- **Automatic Website Unblocking**: CAPTCHA solving, browser fingerprinting, automatic retries
- **Multi-Language Support**: Node.js, Python, Java/C#
- **Framework Support**: Puppeteer, Playwright, Selenium
- **Built-in Proxy Infrastructure**: Premium proxy network included

## Authentication & Configuration

### Credentials Setup
- Username and Password found in Browser API zone "Overview" tab
- Format: `brd-customer-hl_ccf234f3-zone-terms_and_conditions:r5tk64g5ywyt`

### Connection Endpoints
- **Puppeteer/Playwright WebSocket**: `wss://AUTH@brd.superproxy.io:9222`
- **Selenium HTTP**: `https://AUTH@brd.superproxy.io:9515`

### Session Limits
- **Idle Timeout**: 5 minutes
- **Maximum Session Length**: 30 minutes
- **Navigation Timeout**: Up to 2 minutes for complex sites

## Python Implementation Examples

### Playwright Example
```python
from playwright.async_api import async_playwright
import asyncio

async def scrape_with_bright_data(url):
    auth = "brd-customer-hl_ccf234f3-zone-terms_and_conditions:r5tk64g5ywyt"
    endpoint_url = f'wss://{auth}@brd.superproxy.io:9222'
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(endpoint_url)
        page = await browser.new_page()
        
        # Navigate with extended timeout for complex sites
        await page.goto(url, timeout=2*60_000)
        
        # Extract content
        content = await page.content()
        
        await browser.close()
        return content
```

### Puppeteer Python Example
```python
from pyppeteer import connect
import asyncio

async def scrape_with_pyppeteer(url):
    auth = "brd-customer-hl_ccf234f3-zone-terms_and_conditions:r5tk64g5ywyt"
    endpoint_url = f'wss://{auth}@brd.superproxy.io:9222'
    
    browser = await connect(browserWSEndpoint=endpoint_url)
    page = await browser.newPage()
    
    await page.goto(url, timeout=120000)
    content = await page.content()
    
    await browser.close()
    return content
```

## Bandwidth Optimization Tips
1. **Block Unnecessary Requests**: Images, CSS, fonts when only extracting text
2. **Use Page Caching**: Cache results to avoid repeat requests
3. **Limit Concurrent Sessions**: Manage multiple browser instances efficiently
4. **Prefer APIs**: Use direct APIs when available instead of full page scraping

## Billing Information
- **Cost Model**: Based on data transfer (gigabytes)
- **No Time Charges**: No cost for instances or session time
- **Premium Domains**: Higher cost per gigabyte for protected sites

## Country/Location Targeting
- **Recommended**: Let Bright Data auto-select optimal location
- **Manual Selection**: Add `-country-[code]` flag if needed
- **EU Targeting**: Use `-country-eu` for European locations

## Error Codes & Troubleshooting
- **407**: Remote browser port issue - check endpoint configuration
- **403**: Authentication error - verify credentials
- **503**: Service temporarily unavailable - retry with backoff

## Best Practices
1. Set navigation timeout to 2 minutes for complex sites
2. Handle sessions gracefully with proper cleanup
3. Use appropriate error handling and retries
4. Monitor bandwidth usage for cost optimization
5. Leverage built-in CAPTCHA solving rather than manual handling