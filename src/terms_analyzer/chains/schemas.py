"""Pydantic models for structured LLM outputs in the Terms & Conditions Analyzer."""
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime


class TermType(str, Enum):
    """Types of terms that can be extracted from documents."""
    PRIVACY = "privacy"
    PAYMENT = "payment"
    LIABILITY = "liability"
    TERMINATION = "termination"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    GOVERNING_LAW = "governing_law"
    DISPUTE_RESOLUTION = "dispute_resolution"
    LIMITATION_OF_LIABILITY = "limitation_of_liability"
    DATA_USAGE = "data_usage"
    COOKIES = "cookies"
    THIRD_PARTY = "third_party"
    USER_RIGHTS = "user_rights"
    OTHER = "other"


class SeverityLevel(str, Enum):
    """Severity levels for terms and conditions analysis."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class LegalClause(BaseModel):
    """A legal clause extracted from terms and conditions."""
    title: str = Field(..., description="Title or name of the clause")
    content: str = Field(..., description="Full text of the clause")
    type: TermType = Field(..., description="Type of the clause")
    summary: str = Field(..., description="Brief summary of the clause")
    severity: SeverityLevel = Field(..., description="Severity level of the clause")
    concerns: List[str] = Field(
        default_factory=list, 
        description="List of potential concerns or red flags"
    )
    user_rights: List[str] = Field(
        default_factory=list,
        description="List of user rights mentioned in this clause"
    )
    obligations: List[str] = Field(
        default_factory=list,
        description="List of user obligations mentioned in this clause"
    )
    related_clauses: List[str] = Field(
        default_factory=list,
        description="Titles of related clauses within the document"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the clause"
    )


class TermExtraction(BaseModel):
    """Structured output for term extraction from documents."""
    document_title: str = Field(..., description="Title of the document")
    document_source: str = Field(..., description="Source URL or identifier of the document")
    extracted_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp of when the extraction was performed"
    )
    clauses: List[LegalClause] = Field(
        default_factory=list,
        description="List of legal clauses extracted from the document"
    )
    key_terms: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of key terms and their definitions"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the extraction"
    )


class TermAnalysis(BaseModel):
    """Structured output for term analysis."""
    document_title: str = Field(..., description="Title of the analyzed document")
    overall_severity: SeverityLevel = Field(..., description="Overall severity assessment")
    summary: str = Field(..., description="Brief summary of the terms and conditions")
    
    # Analysis sections
    key_points: List[str] = Field(
        ...,
        description="List of key points from the analysis"
    )
    privacy_concerns: List[str] = Field(
        default_factory=list,
        description="List of privacy-related concerns"
    )
    user_rights: List[str] = Field(
        default_factory=list,
        description="List of user rights mentioned in the terms"
    )
    obligations: List[str] = Field(
        default_factory=list,
        description="List of user obligations mentioned in the terms"
    )
    
    # Detailed analysis
    clauses: List[LegalClause] = Field(
        default_factory=list,
        description="Detailed analysis of individual clauses"
    )
    
    # Recommendations
    recommendations: List[str] = Field(
        default_factory=list,
        description="List of recommendations based on the analysis"
    )
    
    # Metadata
    analyzed_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp of when the analysis was performed"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the analysis"
    )


class TermComparison(BaseModel):
    """Structured output for comparing two sets of terms and conditions."""
    document1_title: str = Field(..., description="Title of the first document")
    document2_title: str = Field(..., description="Title of the second document")
    
    # Comparison summary
    summary: str = Field(..., description="Brief summary of the comparison")
    overall_similarity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall similarity between the two documents (0.0 to 1.0)"
    )
    
    # Key differences
    key_differences: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of key differences between the documents"
    )
    
    # Missing clauses
    missing_in_doc1: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Clauses present in document 2 but missing in document 1"
    )
    missing_in_doc2: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Clauses present in document 1 but missing in document 2"
    )
    
    # Severity analysis
    severity_changes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Changes in severity of clauses between the documents"
    )
    
    # Metadata
    compared_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp of when the comparison was performed"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the comparison"
    )


class TermSummary(BaseModel):
    """Structured output for summarizing terms and conditions."""
    document_title: str = Field(..., description="Title of the summarized document")
    summary: str = Field(..., description="Concise summary of the terms and conditions")
    
    # Key information
    key_points: List[str] = Field(
        ...,
        description="List of key points from the terms"
    )
    
    # Important clauses
    important_clauses: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of important clauses with their summaries"
    )
    
    # User actions
    user_actions: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Recommended actions for the user based on the terms"
    )
    
    # Metadata
    summarized_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp of when the summary was generated"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the summary"
    )


# Export all models
__all__ = [
    "TermType",
    "SeverityLevel",
    "LegalClause",
    "TermExtraction",
    "TermAnalysis",
    "TermComparison",
    "TermSummary"
]
