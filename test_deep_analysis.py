#!/usr/bin/env python3
"""
Test script for deep analysis using existing Netflix results.
NO NEW ANALYSES - just testing the deep dive on existing high severity concerns.
"""
import asyncio
import json
from pathlib import Path
from src.terms_analyzer.services.deep_analysis_service import DeepAnalysisService
from src.terms_analyzer.utils.storage import StorageManager

async def test_netflix_deep_analysis():
    """Test deep analysis on the existing Netflix high severity concern."""
    
    # Load existing Netflix analysis
    netflix_analysis_file = Path("terms_analysis/netflix_in_your_neighbourhood_analysis.json")
    
    if not netflix_analysis_file.exists():
        print("❌ Netflix analysis file not found")
        return
    
    print("📋 Loading existing Netflix analysis...")
    with open(netflix_analysis_file, 'r') as f:
        netflix_analysis = json.load(f)
    
    # Find high severity concerns
    high_severity_concerns = [
        concern for concern in netflix_analysis.get('privacy_concerns', [])
        if concern.get('severity', '').lower() == 'high'
    ]
    
    if not high_severity_concerns:
        print("ℹ️  No high severity concerns found in Netflix analysis")
        return
    
    print(f"🚨 Found {len(high_severity_concerns)} high severity concern(s)")
    
    for concern in high_severity_concerns:
        print(f"\n🔍 High Severity Concern:")
        print(f"   Clause: {concern['clause']}")
        print(f"   Quote: {concern['quote'][:100]}...")
        print(f"   Issue: {concern['explanation'][:150]}...")
    
    # Load the original Netflix terms for context
    print(f"\n📄 Loading original Netflix terms for context extraction...")
    storage = StorageManager()
    terms_content = storage.load_terms("Netflix")
    
    if not terms_content:
        print("❌ Could not load original Netflix terms")
        return
    
    # Extract just the terms content (skip metadata)
    lines = terms_content.split('\n')
    content_start = 0
    for i, line in enumerate(lines):
        if line.startswith('---'):
            content_start = i + 1
            break
    
    full_terms_text = '\n'.join(lines[content_start:]).strip()
    print(f"📊 Loaded {len(full_terms_text):,} characters of terms content")
    
    # Initialize deep analysis service
    deep_service = DeepAnalysisService()
    
    # Convert to the format expected by deep analysis
    from src.terms_analyzer.services.openai_service import PrivacyConcern
    
    concern_objects = [
        PrivacyConcern(
            clause=concern['clause'],
            severity=concern['severity'],
            explanation=concern['explanation'],
            quote=concern.get('quote', '')
        )
        for concern in high_severity_concerns
    ]
    
    print(f"\n🔬 Starting deep analysis on Netflix 'Experience' concern...")
    
    # Perform deep analysis
    deep_results = await deep_service.perform_deep_analysis(
        app_name="Netflix",
        full_terms_text=full_terms_text,
        high_severity_concerns=concern_objects
    )
    
    print(f"\n✅ Deep analysis complete!")
    print(f"📁 Results saved to: terms_analysis/deep_analysis/")
    
    # Show a summary
    for i, analysis in enumerate(deep_results['concerns_analyzed'], 1):
        print(f"\n📋 DEEP ANALYSIS RESULT {i}:")
        print(f"=" * 50)
        
        clarity = analysis.get('clarity_analysis', {})
        unclear_terms = clarity.get('unclear_terms', [])
        
        if unclear_terms:
            print(f"🤔 UNCLEAR TERMS IDENTIFIED:")
            for term in unclear_terms:
                print(f"   • {term['term']}")
                print(f"     Explanation: {term['explanation']}")
                print(f"     Impact: {term['user_impact']}")
        
        practical_meaning = clarity.get('practical_meaning', '')
        if practical_meaning:
            print(f"\n💡 PRACTICAL MEANING:")
            print(f"   {practical_meaning}")
        
        user_action = clarity.get('user_action_needed', '')
        if user_action:
            print(f"\n👤 USER ACTION NEEDED:")
            print(f"   {user_action}")

if __name__ == "__main__":
    asyncio.run(test_netflix_deep_analysis())