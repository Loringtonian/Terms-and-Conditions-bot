#!/usr/bin/env python3
"""
Test script for the T&C analysis service.

This script demonstrates how to use the OpenAI service to analyze terms and conditions.
"""
import asyncio
import os
from dotenv import load_dotenv
from src.terms_analyzer.services.openai_service import OpenAIService

# Load environment variables
load_dotenv()

# Sample terms and conditions for testing
SAMPLE_TERMS = """
PRIVACY POLICY

Last Updated: January 1, 2023

1. Information We Collect
We collect the following types of information:
- Personal information: name, email, phone number
- Usage data: how you interact with our service
- Device information: IP address, browser type, operating system

2. How We Use Your Information
We use your information to:
- Provide and maintain our service
- Improve user experience
- Send promotional emails
- Share with third-party advertisers

3. Data Sharing
We may share your information with:
- Service providers
- Business partners
- Advertisers
- Law enforcement when required

4. Data Retention
We retain your personal data for as long as necessary to provide our services.

5. Your Rights
You have the right to:
- Access your data
- Request deletion
- Opt-out of marketing

6. Cookies
We use cookies to track your activity on our service.
"""

async def main():
    # Initialize the service
    service = OpenAIService()
    
    print("Analyzing sample terms and conditions...")
    
    # Analyze the terms
    analysis = await service.analyze_terms(
        app_name="Test App",
        terms_text=SAMPLE_TERMS,
        app_version="1.0.0"
    )
    
    # Print the results
    print("\n=== Analysis Results ===")
    print(f"App: {analysis.app_name} v{analysis.app_version}")
    print(f"Overall Score: {analysis.overall_score}/10")
    print(f"\nSummary: {analysis.summary}")
    
    if analysis.red_flags:
        print("\n🚩 Red Flags:")
        for flag in analysis.red_flags:
            print(f"- {flag}")
    
    if analysis.privacy_concerns:
        print("\n🔍 Privacy Concerns:")
        for concern in analysis.privacy_concerns:
            print(f"\n{concern.clause} ({concern.severity}):")
            print(f"  {concern.explanation}")
            if concern.quote:
                print(f"  > {concern.quote}")

if __name__ == "__main__":
    asyncio.run(main())
