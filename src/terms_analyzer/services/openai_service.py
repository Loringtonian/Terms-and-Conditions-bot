import os
import json
from typing import Optional, Dict, Any
from openai import OpenAI
from ..models.analysis import TCAnalysis

class OpenAIService:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI service with an API key.
        
        Args:
            api_key: OpenAI API key. If not provided, will use OPENAI_API_KEY from environment.
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"
        
    async def analyze_terms(
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
        # Prepare the system message
        system_prompt = """You are an expert in legal document analysis, specializing in terms and conditions. 
        Analyze the provided terms and conditions and provide a detailed assessment.
        
        Your response MUST be valid JSON that matches this schema:
        {
            "app_name": "string",
            "app_version": "string",
            "overall_score": "number (1-10)",
            "privacy_concerns": [{
                "clause": "string",
                "severity": "low|medium|high",
                "explanation": "string",
                "quote": "string (optional exact quote)"
            }],
            "summary": "string",
            "red_flags": ["string"],
            "terms_version": "string (optional)",
            "terms_url": "string (optional)"
        }
        """
        
        # Prepare the user message
        user_message = f"""Analyze the terms and conditions for {app_name} (version: {app_version or 'N/A'}):
        
        {terms_text[:12000]}  # Truncate to avoid context window limits
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
                red_flags=["Analysis failed"]
            )
