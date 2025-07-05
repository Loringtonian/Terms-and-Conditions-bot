#!/usr/bin/env python3
"""
Analysis service that coordinates between storage, OpenAI analysis, and results management.
"""
import os
import json
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from .openai_service import OpenAIService, TCAnalysis
from .deep_analysis_service import DeepAnalysisService
from ..utils.storage import StorageManager

class AnalysisService:
    """Service for analyzing terms and conditions using GPT-4o-latest"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the analysis service.
        
        Args:
            openai_api_key: OpenAI API key. If not provided, uses environment variable.
        """
        self.openai_service = OpenAIService(api_key=openai_api_key)
        self.deep_analysis_service = DeepAnalysisService(openai_api_key=openai_api_key)
        self.storage = StorageManager()
        self.results_dir = Path("terms_analysis")
        self.results_dir.mkdir(exist_ok=True)
    
    def get_available_apps(self) -> List[str]:
        """Get list of apps that have terms stored and can be analyzed."""
        terms_dir = Path("terms_storage")
        if not terms_dir.exists():
            return []
        
        apps = []
        for md_file in terms_dir.glob("*.md"):
            # Convert filename back to app name
            app_name = md_file.stem.replace('_', ' ').title()
            # Handle special cases
            if 'google' in app_name.lower():
                app_name = app_name.replace('Google', 'Google')
            apps.append(app_name)
        
        return sorted(apps)
    
    def _load_terms_from_storage(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Load terms from storage directory and extract metadata."""
        terms_content = self.storage.load_terms(app_name)
        if not terms_content:
            return None
        
        # Parse the markdown to extract metadata and content
        lines = terms_content.split('\n')
        
        # Extract metadata from the header
        metadata = {
            'app_name': app_name,
            'version': None,
            'source_url': None,
            'retrieved_at': None
        }
        
        content_start = 0
        for i, line in enumerate(lines):
            if line.startswith('- **Version**:'):
                metadata['version'] = line.split(':', 1)[1].strip()
            elif line.startswith('- **Source URL**:'):
                metadata['source_url'] = line.split(':', 1)[1].strip()
            elif line.startswith('- **Retrieved At**:'):
                metadata['retrieved_at'] = line.split(':', 1)[1].strip()
            elif line.startswith('---'):
                content_start = i + 1
                break
        
        # Extract the actual terms content
        terms_text = '\n'.join(lines[content_start:]).strip()
        
        return {
            'metadata': metadata,
            'content': terms_text
        }
    
    async def analyze_app(self, app_name: str, save_results: bool = True) -> Optional[TCAnalysis]:
        """Analyze terms and conditions for a specific app.
        
        Args:
            app_name: Name of the application to analyze
            save_results: Whether to save the analysis results to disk
            
        Returns:
            TCAnalysis object with the analysis results, or None if app not found
        """
        print(f"🔍 Analyzing terms for: {app_name}")
        
        # Load terms from storage
        terms_data = self._load_terms_from_storage(app_name)
        if not terms_data:
            print(f"❌ No terms found for {app_name}")
            return None
        
        metadata = terms_data['metadata']
        content = terms_data['content']
        
        print(f"📄 Loaded {len(content):,} characters of terms")
        
        # Prepare additional context
        additional_context = {
            'source_url': metadata.get('source_url'),
            'retrieved_at': metadata.get('retrieved_at'),
            'analysis_focus': 'Canadian consumer perspective'
        }
        
        try:
            # Perform the analysis
            analysis = self.openai_service.analyze_terms(
                app_name=app_name,
                terms_text=content,
                app_version=metadata.get('version'),
                additional_context=additional_context
            )
            
            print(f"✅ Analysis complete for {app_name}")
            print(f"   📊 Overall Score: {analysis.overall_score}/10")
            print(f"   🔒 Data Collection Score: {analysis.data_collection_score}/10")
            print(f"   📝 User Friendliness: {analysis.user_friendliness_score}/10")
            print(f"   ⚠️  Red Flags: {len(analysis.red_flags)}")
            
            # Save results if requested
            if save_results:
                self._save_analysis_results(analysis)
            
            # Automatically perform deep analysis if high severity concerns found
            deep_analysis_results = await self.deep_analysis_service.auto_deep_analysis_if_needed(
                app_name=app_name,
                full_terms_text=content,
                analysis_result=analysis
            )
            
            if deep_analysis_results:
                print(f"🔬 Deep analysis completed for {len(deep_analysis_results['concerns_analyzed'])} high severity concerns")
                
                # Add deep analysis data to the main analysis result
                analysis_dict = analysis.dict()
                analysis_dict['deep_analysis'] = self._format_deep_analysis_for_frontend(
                    analysis.privacy_concerns, 
                    deep_analysis_results['concerns_analyzed']
                )
                
                # Re-save with deep analysis included
                self._save_analysis_dict(analysis_dict)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing {app_name}: {str(e)}")
            return None
    
    def _save_analysis_results(self, analysis: TCAnalysis) -> Path:
        """Save analysis results to disk."""
        # Create filename
        safe_name = analysis.app_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
        filename = f"{safe_name}_analysis.json"
        filepath = self.results_dir / filename
        
        # Convert to dict and save
        analysis_dict = analysis.dict()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Analysis saved to: {filepath}")
        print(f"📁 Results directory: terms_analysis/")
        return filepath
    
    def _save_analysis_dict(self, analysis_dict: Dict[str, Any]) -> Path:
        """Save analysis dictionary (with deep analysis) to disk."""
        safe_name = analysis_dict['app_name'].lower().replace(' ', '_').replace('(', '').replace(')', '')
        filename = f"{safe_name}_analysis.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_dict, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def _format_deep_analysis_for_frontend(self, privacy_concerns: List, deep_analysis_concerns: List) -> Dict[int, Dict[str, Any]]:
        """Format deep analysis results for frontend consumption."""
        formatted_deep_analysis = {}
        
        # Map deep analysis results to their corresponding privacy concern indices
        for deep_concern in deep_analysis_concerns:
            original_concern = deep_concern['original_concern']
            
            # Find the index of this concern in the privacy_concerns list
            concern_index = None
            for i, concern in enumerate(privacy_concerns):
                if (concern.clause == original_concern['clause'] and 
                    concern.severity == original_concern['severity']):
                    concern_index = i
                    break
            
            if concern_index is not None:
                clarity_analysis = deep_concern.get('clarity_analysis', {})
                online_research = deep_concern.get('online_research', {})
                
                formatted_deep_analysis[concern_index] = {
                    'unclear_terms': clarity_analysis.get('unclear_terms', []),
                    'practical_meaning': clarity_analysis.get('practical_meaning', ''),
                    'user_action_needed': clarity_analysis.get('user_action_needed', ''),
                    'severity_justification': clarity_analysis.get('severity_justification', ''),
                    'extended_context': deep_concern.get('extended_context', ''),
                    'online_research': {
                        'search_query': online_research.get('search_query', ''),
                        'top_result_url': online_research.get('top_result_url'),
                        'top_result_title': online_research.get('top_result_title'),
                        'summary': online_research.get('summary')
                    } if online_research else None
                }
        
        return formatted_deep_analysis
    
    async def analyze_multiple_apps(self, app_names: List[str], delay_seconds: int = 2) -> Dict[str, Optional[TCAnalysis]]:
        """Analyze multiple apps with rate limiting.
        
        Args:
            app_names: List of app names to analyze
            delay_seconds: Delay between API calls to respect rate limits
            
        Returns:
            Dictionary mapping app names to their analysis results
        """
        results = {}
        
        print(f"🚀 Starting batch analysis of {len(app_names)} apps...")
        
        for i, app_name in enumerate(app_names, 1):
            print(f"\n[{i}/{len(app_names)}] Processing: {app_name}")
            
            result = await self.analyze_app(app_name, save_results=True)
            results[app_name] = result
            
            # Rate limiting
            if i < len(app_names):
                print(f"⏳ Waiting {delay_seconds}s before next analysis...")
                await asyncio.sleep(delay_seconds)
        
        # Summary
        successful = sum(1 for r in results.values() if r is not None)
        failed = len(app_names) - successful
        
        print(f"\n📊 BATCH ANALYSIS COMPLETE:")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        
        return results
    
    def load_analysis_results(self, app_name: str) -> Optional[TCAnalysis]:
        """Load previously saved analysis results."""
        safe_name = app_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
        filename = f"{safe_name}_analysis.json"
        filepath = self.results_dir / filename
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return TCAnalysis(**data)
        except Exception as e:
            print(f"Error loading analysis for {app_name}: {e}")
            return None
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a summary of all completed analyses."""
        results_files = list(self.results_dir.glob("*_analysis.json"))
        
        if not results_files:
            return {"total_analyses": 0, "analyses": []}
        
        analyses = []
        for filepath in results_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                analyses.append({
                    "app_name": data["app_name"],
                    "overall_score": data["overall_score"],
                    "data_collection_score": data.get("data_collection_score"),
                    "user_friendliness_score": data.get("user_friendliness_score"),
                    "red_flags_count": len(data.get("red_flags", [])),
                    "analysis_date": data.get("analysis_date")
                })
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                continue
        
        # Sort by overall score (worst first)
        analyses.sort(key=lambda x: x["overall_score"])
        
        return {
            "total_analyses": len(analyses),
            "analyses": analyses,
            "worst_scoring": analyses[:5] if analyses else [],
            "best_scoring": analyses[-5:] if analyses else []
        }