import os
import json
from typing import Optional, Dict, Any, List
from openai import OpenAI
from pydantic import BaseModel
from datetime import datetime

class PrivacyConcern(BaseModel):
    clause: str
    severity: str  # low, medium, high
    explanation: str
    quote: Optional[str] = None

class TCAnalysis(BaseModel):
    app_name: str
    app_version: Optional[str] = None
    overall_score: float  # 1-10 scale
    privacy_concerns: List[PrivacyConcern] = []
    summary: str
    red_flags: List[str] = []
    user_friendliness_score: Optional[float] = None  # 1-10 scale
    data_collection_score: Optional[float] = None    # 1-10 scale (lower = more invasive)
    legal_complexity_score: Optional[float] = None   # 1-10 scale (lower = more complex)
    terms_version: Optional[str] = None
    terms_url: Optional[str] = None
    analysis_date: Optional[str] = None

class OpenAIService:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI service with an API key.
        
        Args:
            api_key: OpenAI API key. If not provided, will use OPENAI_API_KEY from environment.
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-2024-11-20"  # Specific GPT-4o version
        
    def analyze_terms(
        self,
        app_name: str,
        terms_text: str,
        app_version: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> TCAnalysis:
        """Analyze terms and conditions text using OpenAI.
        
        Args:
            app_name: Name of the application
            terms_text: Full text of the terms and conditions
            app_version: Version of the application (optional)
            additional_context: Any additional context for the analysis (e.g., country, language)
            
        Returns:
            TCAnalysis object with the analysis results
        """
        # Prepare the comprehensive system message
        system_prompt = """You are an expert legal analyst specializing in terms and conditions analysis. Your role is to evaluate terms and conditions from a Canadian consumer perspective, focusing on user privacy, data protection, and fairness.

        ANALYSIS FRAMEWORK:
        1. Overall Score (1-10): Rate how user-friendly these terms are overall
        2. User Friendliness (1-10): How clear, fair, and reasonable are the terms?
        3. Data Collection (1-10): How respectful is the app of user privacy? (10 = minimal data collection, 1 = very invasive)
        4. Legal Complexity (1-10): How easy are the terms to understand? (10 = very clear, 1 = very complex)

        FOCUS AREAS:
        - Data collection and sharing practices
        - User rights and protections
        - Termination and account deletion policies
        - Third-party integrations and data sharing
        - Advertising and tracking practices
        - Geographic restrictions or differences
        - Changes to terms notification policies
        - Dispute resolution mechanisms

        RED FLAGS TO IDENTIFY:
        - Excessive data collection beyond app functionality
        - Broad rights to share data with third parties
        - Difficult account deletion processes
        - Automatic binding arbitration clauses
        - Overly broad content licensing rights
        - Unclear or missing privacy protections
        - Terms that heavily favor the company

        Your response MUST be valid JSON matching this exact schema:
        {
            "app_name": "string",
            "app_version": "string or null",
            "overall_score": "number (1-10, can be decimal)",
            "user_friendliness_score": "number (1-10, can be decimal)",
            "data_collection_score": "number (1-10, can be decimal)",
            "legal_complexity_score": "number (1-10, can be decimal)",
            "privacy_concerns": [{
                "clause": "string (brief description)",
                "severity": "low|medium|high",
                "explanation": "string (detailed explanation)",
                "quote": "string (exact quote if available)"
            }],
            "summary": "string (2-3 sentence overview)",
            "red_flags": ["string (specific concerning practices)"],
            "terms_version": "string or null",
            "terms_url": "string or null",
            "analysis_date": "string (ISO date)"
        }
        """
        
        # Prepare the user message with smart truncation
        max_terms_length = 15000  # Leave room for system prompt and response
        if len(terms_text) > max_terms_length:
            # Try to find a good breaking point
            truncated_text = terms_text[:max_terms_length]
            last_period = truncated_text.rfind('.')
            if last_period > max_terms_length * 0.8:  # If we can find a sentence end in the last 20%
                truncated_text = truncated_text[:last_period + 1]
            truncated_text += "\n\n[NOTE: Terms truncated for analysis - this represents the first portion of the document]"
        else:
            truncated_text = terms_text
            
        user_message = f"""Analyze the terms and conditions for {app_name} (version: {app_version or 'N/A'}):

        {truncated_text}
        
        Additional context: {json.dumps(additional_context) if additional_context else 'None'}
        """
        
        try:
            # Make the API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse the response
            result = json.loads(response.choices[0].message.content)
            
            # Ensure analysis_date is set
            if 'analysis_date' not in result or not result['analysis_date']:
                result['analysis_date'] = datetime.now().isoformat()
            
            # Convert to our model
            return TCAnalysis(**result)
            
        except Exception as e:
            # Log the error and return a default response
            print(f"Error analyzing terms: {str(e)}")
            return TCAnalysis(
                app_name=app_name,
                app_version=app_version or "unknown",
                overall_score=1.0,
                summary="Error analyzing terms and conditions. Please try again later.",
                privacy_concerns=[],
                red_flags=["Analysis failed"],
                analysis_date=datetime.now().isoformat()
            )
