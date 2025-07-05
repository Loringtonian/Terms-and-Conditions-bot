#!/usr/bin/env python3
"""
Deep analysis service for investigating high severity privacy concerns.
Uses multiple strategies to understand unclear or concerning terms.
"""
import re
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from .openai_service import OpenAIService, PrivacyConcern
from .tavily_service import TavilyService

class DeepAnalysisService:
    """Service for performing deep analysis on high severity privacy concerns."""
    
    def __init__(self, openai_api_key: Optional[str] = None, tavily_api_key: Optional[str] = None):
        self.openai_service = OpenAIService(api_key=openai_api_key)
        self.tavily_service = TavilyService(api_key=tavily_api_key)
        self.deep_analysis_dir = Path("terms_analysis/deep_analysis")
        self.deep_analysis_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_context_around_concern(self, full_terms_text: str, concern_quote: str, context_chars: int = 1000) -> str:
        """Extract surrounding context from the terms document around a specific quote."""
        if not concern_quote or len(concern_quote) < 10:
            return ""
        
        # Find the quote in the full text (case insensitive, handle truncation)
        quote_start = concern_quote[:50].strip()  # Use first 50 chars to find location
        
        # Try to find the quote location
        text_lower = full_terms_text.lower()
        quote_lower = quote_start.lower()
        
        position = text_lower.find(quote_lower)
        if position == -1:
            # Try finding by first few words
            words = quote_lower.split()[:5]  # First 5 words
            if words:
                search_phrase = " ".join(words)
                position = text_lower.find(search_phrase)
        
        if position == -1:
            return f"Could not locate quote in document: {concern_quote[:100]}..."
        
        # Extract context around the position
        start = max(0, position - context_chars // 2)
        end = min(len(full_terms_text), position + len(concern_quote) + context_chars // 2)
        
        context = full_terms_text[start:end]
        
        # Add markers to show where we are in the document
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(full_terms_text) else ""
        
        return f"{prefix}{context}{suffix}"
    
    def analyze_unclear_terms(self, app_name: str, concern: PrivacyConcern, context: str) -> Dict[str, Any]:
        """Use GPT-4o to analyze unclear terms and provide clarification."""
        
        system_prompt = """You are a legal analyst specializing in clarifying confusing or unclear terms and conditions language. 
        
        Your job is to:
        1. Identify what specific unclear terms, jargon, or concepts need explanation
        2. Provide clear, consumer-friendly explanations of what these terms actually mean
        3. Explain the practical implications for users
        4. Suggest what questions users should ask or what to look out for
        
        Focus on making complex legal language understandable to average consumers.
        
        Return your analysis as JSON with this structure:
        {
            "unclear_terms": [
                {
                    "term": "string (the unclear term/phrase)",
                    "explanation": "string (clear explanation)",
                    "user_impact": "string (what this means for the user)",
                    "questions_to_ask": ["string (questions users should consider)"]
                }
            ],
            "practical_meaning": "string (what this clause actually means in practice)",
            "user_action_needed": "string (what users should do about this)",
            "severity_justification": "string (why this was flagged as high severity)"
        }
        """
        
        user_message = f"""Analyze this HIGH SEVERITY privacy concern from {app_name}'s terms:

CONCERN: {concern.clause}
SEVERITY: {concern.severity}
EXPLANATION: {concern.explanation}
QUOTE: {concern.quote}

FULL CONTEXT FROM DOCUMENT:
{context}

Help clarify what this actually means for users and why it's concerning."""

        try:
            response = self.openai_service.client.chat.completions.create(
                model=self.openai_service.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=1500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Error in unclear terms analysis: {e}")
            return {
                "error": str(e),
                "unclear_terms": [],
                "practical_meaning": "Analysis failed",
                "user_action_needed": "Manual review required",
                "severity_justification": "Could not analyze"
            }
    
    async def research_context_online(self, app_name: str, unclear_terms: List[str], concern_clause: str) -> Dict[str, Any]:
        """Use Tavily to research unclear terms or concepts online."""
        research_results = {}
        
        try:
            # Create search query focusing on the app and unclear terms
            search_terms = " ".join(unclear_terms[:3])  # Limit to first 3 terms
            query = f'"{app_name}" {search_terms} terms conditions privacy policy explanation'
            
            print(f"🔍 Researching online: {query}")
            
            # Search for explanations and context
            search_results = await self.tavily_service.search_terms_and_conditions(query)
            
            if search_results:
                # Get the most relevant result
                top_result = search_results[0]
                
                # Try to extract more detailed content
                if 'url' in top_result:
                    detailed_content = await self.tavily_service.extract_terms_text(top_result['url'])
                    
                    research_results = {
                        "search_query": query,
                        "top_result_url": top_result['url'],
                        "top_result_title": top_result.get('title', ''),
                        "summary": top_result.get('content', '')[:500],
                        "detailed_content_available": len(detailed_content or '') > 0,
                        "additional_context": detailed_content[:1000] if detailed_content else None
                    }
            else:
                research_results = {
                    "search_query": query,
                    "no_results": True,
                    "message": "No additional context found online"
                }
                
        except Exception as e:
            research_results = {
                "error": str(e),
                "search_attempted": True
            }
        
        return research_results
    
    async def perform_deep_analysis(self, app_name: str, full_terms_text: str, high_severity_concerns: List[PrivacyConcern]) -> Dict[str, Any]:
        """Perform comprehensive deep analysis on high severity concerns."""
        
        print(f"🔬 Starting deep analysis for {app_name} - {len(high_severity_concerns)} high severity concerns")
        
        deep_analysis_results = {
            "app_name": app_name,
            "total_high_severity_concerns": len(high_severity_concerns),
            "analysis_timestamp": "2025-07-05",
            "concerns_analyzed": []
        }
        
        for i, concern in enumerate(high_severity_concerns, 1):
            print(f"  📋 Analyzing concern {i}/{len(high_severity_concerns)}: {concern.clause}")
            
            # Step 1: Extract more context around the concerning quote
            context = self.extract_context_around_concern(full_terms_text, concern.quote or "")
            
            # Step 2: Analyze unclear terms with GPT-4o
            clarity_analysis = self.analyze_unclear_terms(app_name, concern, context)
            
            # Step 3: Research online for additional context (if we found unclear terms)
            online_research = {}
            if clarity_analysis.get("unclear_terms"):
                unclear_term_list = [term["term"] for term in clarity_analysis["unclear_terms"]]
                online_research = await self.research_context_online(app_name, unclear_term_list, concern.clause)
            
            # Compile results for this concern
            concern_analysis = {
                "original_concern": {
                    "clause": concern.clause,
                    "severity": concern.severity,
                    "explanation": concern.explanation,
                    "quote": concern.quote
                },
                "extended_context": context,
                "clarity_analysis": clarity_analysis,
                "online_research": online_research
            }
            
            deep_analysis_results["concerns_analyzed"].append(concern_analysis)
        
        # Save the deep analysis results
        self._save_deep_analysis(app_name, deep_analysis_results)
        
        return deep_analysis_results
    
    def _save_deep_analysis(self, app_name: str, analysis_results: Dict[str, Any]) -> Path:
        """Save deep analysis results to file."""
        safe_name = app_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
        filename = f"{safe_name}_deep_analysis.json"
        filepath = self.deep_analysis_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Deep analysis saved to: {filepath}")
        return filepath
    
    async def auto_deep_analysis_if_needed(self, app_name: str, full_terms_text: str, analysis_result) -> Optional[Dict[str, Any]]:
        """Automatically perform deep analysis if high severity concerns are found."""
        
        # Check if there are any high severity concerns
        high_severity_concerns = [
            concern for concern in analysis_result.privacy_concerns 
            if concern.severity.lower() == 'high'
        ]
        
        if not high_severity_concerns:
            print(f"✅ No high severity concerns found for {app_name} - no deep analysis needed")
            return None
        
        print(f"🚨 Found {len(high_severity_concerns)} high severity concerns for {app_name}")
        print(f"📊 Starting automatic deep analysis...")
        
        # Perform deep analysis
        deep_results = await self.perform_deep_analysis(app_name, full_terms_text, high_severity_concerns)
        
        return deep_results