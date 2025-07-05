from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class PrivacyConcern(BaseModel):
    clause: str
    severity: Severity
    explanation: str
    quote: Optional[str] = None

class TCAnalysis(BaseModel):
    app_name: str
    app_version: str
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    overall_score: float = Field(ge=1, le=10)
    privacy_concerns: List[PrivacyConcern] = []
    summary: str
    red_flags: List[str] = []
    terms_version: Optional[str] = None
    terms_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "app_name": "Example App",
                "app_version": "1.0.0",
                "overall_score": 7.5,
                "privacy_concerns": [
                    {
                        "clause": "Data Sharing with Third Parties",
                        "severity": "high",
                        "explanation": "The app shares user data with multiple third-party advertisers.",
                        "quote": "We may share your personal information with our advertising partners..."
                    }
                ],
                "summary": "The terms contain several concerning clauses about data sharing...",
                "red_flags": [
                    "Shares data with third parties",
                    "Vague data retention policy"
                ],
                "terms_version": "2023-01-01",
                "terms_url": "https://example.com/terms"
            }
        }
