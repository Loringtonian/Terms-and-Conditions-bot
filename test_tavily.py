#!/usr/bin/env python3
"""
Test script for Tavily MCP integration.

This script demonstrates how to use the Tavily service to find and analyze terms and conditions.
"""
import asyncio
import os
from dotenv import load_dotenv
from src.terms_analyzer.services.tavily_service import TavilyService

# Load environment variables
load_dotenv()

async def main():
    # Initialize the service
    tavily = TavilyService()
    
    # Test search
    app_name = "WhatsApp"
    print(f"Searching for terms and conditions for {app_name}...")
    
    # Option 1: Just search for terms
    print("\n=== Search Results ===")
    search_results = await tavily.search_terms_and_conditions(app_name)
    for i, result in enumerate(search_results[:3], 1):
        print(f"\nResult {i}:")
        print(f"Title: {result['title']}")
        print(f"URL: {result['url']}")
        print(f"Score: {result.get('score', 'N/A')}")
        print(f"Preview: {result['content'][:200]}...")
    
    # Option 2: Find and extract terms
    print("\n=== Extracting Terms ===")
    terms_data = await tavily.find_terms_for_app(app_name)
    if terms_data:
        print(f"\nFound terms for {app_name}:")
        print(f"URL: {terms_data['terms_url']}")
        print(f"Content length: {len(terms_data['terms_text'])} characters")
        print("\nPreview:")
        print(terms_data['terms_text'][:500] + "...")
    else:
        print("\nCould not find terms and conditions")
    
    # Clean up
    await tavily.close()

if __name__ == "__main__":
    asyncio.run(main())
