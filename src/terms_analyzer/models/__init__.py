"""Database models for the Terms & Conditions Analyzer."""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, validator
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Enum as SQLEnum,
    JSON,
    ForeignKey,
    Table,
    Boolean,
    create_engine,
    event,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session as DBSession
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql import func

from ..config import settings, logger

# Create SQLAlchemy engine and session
engine = create_engine(
    settings.database.url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database.url else {},
    poolclass=StaticPool if "sqlite" in settings.database.url else None,
    echo=settings.database.echo,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Association table for many-to-many relationship between Service and Category
service_category = Table(
    "service_category",
    Base.metadata,
    Column("service_id", Integer, ForeignKey("services.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)

class ServiceStatus(str, Enum):
    """Status of a service's terms and conditions tracking."""
    PENDING = "pending"  # Not yet processed
    PROCESSING = "processing"  # Currently being processed
    COMPLETED = "completed"  # Successfully processed
    FAILED = "failed"  # Processing failed
    OUTDATED = "outdated"  # Needs update (new version available)

class DocumentType(str, Enum):
    """Type of legal document."""
    TERMS_OF_SERVICE = "terms_of_service"
    PRIVACY_POLICY = "privacy_policy"
    COOKIE_POLICY = "cookie_policy"
    COMMUNITY_GUIDELINES = "community_guidelines"
    EULA = "eula"  # End User License Agreement
    SERVICE_AGREEMENT = "service_agreement"
    OTHER = "other"

class Service(Base):
    """A service or application with terms and conditions to track."""
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    website_url = Column(String(512), nullable=True)
    status = Column(SQLEnum(ServiceStatus), default=ServiceStatus.PENDING, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    metadata_ = Column("metadata", JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    documents = relationship("Document", back_populates="service", cascade="all, delete-orphan")
    categories = relationship("Category", secondary=service_category, back_populates="services")
    
    def __repr__(self):
        return f"<Service(name='{self.name}', status='{self.status}')>"

class Category(Base):
    """Category for organizing services (e.g., Social Media, Cloud Storage)."""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    services = relationship("Service", secondary=service_category, back_populates="categories")
    
    def __repr__(self):
        return f"<Category(name='{self.name}')>"

class Document(Base):
    """A document containing terms and conditions or related legal text."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    document_type = Column(SQLEnum(DocumentType), nullable=False, index=True)
    version = Column(String(50), nullable=True)
    source_url = Column(String(1024), nullable=False)
    language = Column(String(10), default="en", nullable=False)
    content_hash = Column(String(64), nullable=True, index=True)  # For detecting changes
    raw_content = Column(Text, nullable=True)  # Raw text content
    file_path = Column(String(512), nullable=True)  # Path to stored file if applicable
    is_current = Column(Boolean, default=True, nullable=False)
    metadata_ = Column("metadata", JSON, default=dict, nullable=False)
    last_retrieved = Column(DateTime(timezone=True), server_default=func.now())
    effective_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    service = relationship("Service", back_populates="documents")
    analyses = relationship("Analysis", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(service_id={self.service_id}, type='{self.document_type}', version='{self.version}')>"

class AnalysisStatus(str, Enum):
    """Status of a document analysis."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Analysis(Base):
    """Analysis of a document's content."""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    analysis_type = Column(String(100), nullable=False, index=True)  # e.g., "summary", "full_analysis"
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False)
    model_name = Column(String(100), nullable=True)  # e.g., "gpt-4o"
    result = Column(JSON, nullable=True)  # Structured analysis results
    error = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="analyses")
    
    def __repr__(self):
        return f"<Analysis(document_id={self.document_id}, type='{self.analysis_type}', status='{self.status}')>"

# Pydantic models for API responses and requests
ServiceBase = sqlalchemy_to_pydantic(Service, exclude=["documents", "categories"])
CategoryBase = sqlalchemy_to_pydantic(Category, exclude=["services"])
DocumentBase = sqlalchemy_to_pydantic(Document, exclude=["service", "analyses"])
AnalysisBase = sqlalchemy_to_pydantic(Analysis, exclude=["document"])

class ServiceCreate(ServiceBase):
    """Schema for creating a new service."""
    category_names: List[str] = Field(default_factory=list)

class ServiceResponse(ServiceBase):
    """Schema for service response with relationships."""
    id: int
    categories: List[CategoryBase] = []
    documents: List[DocumentBase] = []
    
    class Config:
        orm_mode = True

class DocumentCreate(DocumentBase):
    """Schema for creating a new document."""
    pass

class DocumentResponse(DocumentBase):
    """Schema for document response with relationships."""
    id: int
    service: Optional[ServiceBase] = None
    analyses: List[AnalysisBase] = []
    
    class Config:
        orm_mode = True

class AnalysisCreate(AnalysisBase):
    """Schema for creating a new analysis."""
    pass

class AnalysisResponse(AnalysisBase):
    """Schema for analysis response with relationships."""
    id: int
    document: Optional[DocumentBase] = None
    
    class Config:
        orm_mode = True

# Create database tables
def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)

# Database session dependency
def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database on startup
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite."""
    if "sqlite" in settings.database.url:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Create tables when this module is imported
create_tables()

# Export public API
__all__ = [
    # Models
    "Service",
    "Category",
    "Document",
    "Analysis",
    "ServiceStatus",
    "DocumentType",
    "AnalysisStatus",
    
    # Schemas
    "ServiceBase",
    "ServiceCreate",
    "ServiceResponse",
    "CategoryBase",
    "DocumentBase",
    "DocumentCreate",
    "DocumentResponse",
    "AnalysisBase",
    "AnalysisCreate",
    "AnalysisResponse",
    
    # Database
    "SessionLocal",
    "get_db",
    "create_tables",
]
