#!/usr/bin/env python3
"""
Comprehensive analysis script for all terms and conditions files.
This script will analyze all .md files in terms_storage/ using GPT-4.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.terms_analyzer.services.analysis_service import AnalysisService

async def analyze_all_terms():
    """Analyze all terms and conditions files in the storage directory."""
    
    # Initialize the analysis service
    print("🚀 Initializing Analysis Service...")
    analysis_service = AnalysisService()
    
    # Get the terms storage directory
    terms_storage_dir = project_root / 'terms_storage'
    
    if not terms_storage_dir.exists():
        print("❌ Error: terms_storage directory not found!")
        return
    
    # Get all .md files
    terms_files = list(terms_storage_dir.glob('*.md'))
    print(f"📁 Found {len(terms_files)} terms files to analyze")
    
    if not terms_files:
        print("❌ No terms files found!")
        return
    
    # Convert filenames to app names
    app_names = []
    for terms_file in terms_files:
        # Convert filename to app name (remove .md and replace underscores)
        app_name = terms_file.stem.replace('_', ' ').title()
        
        # Handle special cases
        if 'google' in app_name.lower():
            app_name = app_name.replace('Google', 'Google')
        elif 'netflix' in app_name.lower():
            if 'neighbourhood' in app_name.lower():
                app_name = 'Netflix in Your Neighbourhood'
            else:
                app_name = 'Netflix'
        elif 'facebook' in app_name.lower():
            app_name = 'Facebook'
        elif 'instagram' in app_name.lower():
            app_name = 'Instagram'
        elif 'tiktok' in app_name.lower():
            app_name = 'TikTok'
        elif 'youtube' in app_name.lower():
            app_name = 'YouTube'
        
        app_names.append((terms_file.stem, app_name))
    
    print(f"📋 Apps to analyze:")
    for i, (file_stem, app_name) in enumerate(app_names[:10], 1):
        print(f"   {i}. {app_name} ({file_stem})")
    if len(app_names) > 10:
        print(f"   ... and {len(app_names) - 10} more")
    
    # Information about the analysis
    print(f"\n⚠️  This will analyze {len(app_names)} apps using GPT-4.")
    print("💰 This will consume significant OpenAI API credits.")
    print("⏱️  Estimated time: ~10-15 minutes (with rate limiting)")
    print("🚀 Starting analysis automatically...")
    
    print(f"\n🚀 Starting batch analysis of {len(app_names)} apps...")
    print("📊 Rate limiting: 3 seconds between requests to respect OpenAI limits")
    
    # Run the analysis with rate limiting
    try:
        # Use the built-in batch analysis method
        app_name_list = [app_name for _, app_name in app_names]
        results = await analysis_service.analyze_multiple_apps(
            app_names=app_name_list,
            delay_seconds=3  # 3 seconds between requests
        )
        
        # Print final summary
        print(f"\n🎉 BATCH ANALYSIS COMPLETE!")
        print(f"✅ Successfully analyzed: {sum(1 for r in results.values() if r is not None)}")
        print(f"❌ Failed to analyze: {sum(1 for r in results.values() if r is None)}")
        
        # Show results directory
        results_dir = project_root / 'terms_analysis'
        if results_dir.exists():
            analysis_files = list(results_dir.glob('*_analysis.json'))
            print(f"💾 Analysis files saved in: {results_dir}")
            print(f"📁 Total analysis files: {len(analysis_files)}")
        
        print(f"\n🌐 You can now view the results in your web interface!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Analysis interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")

if __name__ == "__main__":
    # Run the analysis
    asyncio.run(analyze_all_terms())