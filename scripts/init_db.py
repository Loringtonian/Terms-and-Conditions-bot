#!/usr/bin/env python3
"""
Initialize the database with initial data.
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from terms_analyzer.models import (
    SessionLocal, Service, Category, Document, Analysis,
    ServiceStatus, DocumentType, AnalysisStatus
)

# Common categories
CATEGORIES = [
    "Social Media",
    "Cloud Storage",
    "Streaming Services",
    "E-commerce",
    "Productivity",
    "Communication",
    "Gaming",
    "Finance",
    "Health & Fitness",
    "News & Media"
]

# Common services with their categories
SERVICES = [
    {
        "name": "tiktok",
        "display_name": "TikTok",
        "description": "Short-form video hosting service",
        "website_url": "https://www.tiktok.com",
        "categories": ["Social Media", "Entertainment"],
        "documents": [
            {
                "document_type": "terms_of_service",
                "source_url": "https://www.tiktok.com/legal/page/us/terms-of-service/en",
                "version": "November 2023",
                "language": "en",
                "file_path": "tiktok_terms.txt"
            },
            {
                "document_type": "privacy_policy",
                "source_url": "https://www.tiktok.com/legal/page/us/privacy-policy/en",
                "version": "November 2023",
                "language": "en"
            }
        ]
    },
    {
        "name": "instagram",
        "display_name": "Instagram",
        "description": "Photo and video sharing social networking service",
        "website_url": "https://www.instagram.com",
        "categories": ["Social Media"],
        "documents": [
            {
                "document_type": "terms_of_service",
                "source_url": "https://help.instagram.com/581066165582870",
                "language": "en"
            },
            {
                "document_type": "privacy_policy",
                "source_url": "https://privacycenter.instagram.com/policy",
                "language": "en"
            }
        ]
    },
    {
        "name": "netflix",
        "display_name": "Netflix",
        "description": "Subscription streaming service and production company",
        "website_url": "https://www.netflix.com",
        "categories": ["Streaming Services", "Entertainment"],
        "documents": [
            {
                "document_type": "terms_of_service",
                "source_url": "https://help.netflix.com/legal/termsofuse",
                "language": "en"
            },
            {
                "document_type": "privacy_policy",
                "source_url": "https://www.netflix.com/privacy",
                "language": "en"
            }
        ]
    },
    {
        "name": "spotify",
        "display_name": "Spotify",
        "description": "Audio streaming and media services provider",
        "website_url": "https://www.spotify.com",
        "categories": ["Streaming Services", "Music"],
        "documents": [
            {
                "document_type": "terms_of_service",
                "source_url": "https://www.spotify.com/us/legal/end-user-agreement/",
                "language": "en"
            },
            {
                "document_type": "privacy_policy",
                "source_url": "https://www.spotify.com/us/legal/privacy-policy/",
                "language": "en"
            }
        ]
    },
    {
        "name": "dropbox",
        "display_name": "Dropbox",
        "description": "File hosting service",
        "website_url": "https://www.dropbox.com",
        "categories": ["Cloud Storage", "Productivity"],
        "documents": [
            {
                "document_type": "terms_of_service",
                "source_url": "https://www.dropbox.com/terms",
                "language": "en"
            },
            {
                "document_type": "privacy_policy",
                "source_url": "https://www.dropbox.com/privacy",
                "language": "en"
            }
        ]
    }
]

def init_database():
    """Initialize the database with initial data."""
    db = SessionLocal()
    
    try:
        # Create categories
        category_map = {}
        for category_name in CATEGORIES:
            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                category = Category(name=category_name)
                db.add(category)
                db.commit()
                db.refresh(category)
            category_map[category_name.lower()] = category
        
        # Create services and their documents
        for service_data in SERVICES:
            # Check if service already exists
            service = db.query(Service).filter(Service.name == service_data["name"]).first()
            
            if not service:
                # Create new service
                service = Service(
                    name=service_data["name"],
                    display_name=service_data.get("display_name", service_data["name"].title()),
                    description=service_data.get("description", ""),
                    website_url=service_data.get("website_url", ""),
                    status=ServiceStatus.PENDING,
                    is_active=True,
                    metadata_={"source": "initial_data"}
                )
                db.add(service)
                db.commit()
                db.refresh(service)
                
                # Add categories to service
                for cat_name in service_data.get("categories", []):
                    category = category_map.get(cat_name.lower())
                    if category:
                        service.categories.append(category)
                
                # Add documents
                for doc_data in service_data.get("documents", []):
                    doc = Document(
                        service_id=service.id,
                        document_type=doc_data["document_type"],
                        source_url=doc_data["source_url"],
                        version=doc_data.get("version"),
                        language=doc_data.get("language", "en"),
                        file_path=doc_data.get("file_path"),
                        is_current=True,
                        metadata_={"source": "initial_data"},
                        last_retrieved=datetime.now(timezone.utc)
                    )
                    db.add(doc)
                
                db.commit()
                print(f"Added service: {service.display_name}")
            else:
                print(f"Service already exists: {service.display_name}")
        
        print("\nDatabase initialization complete!")
        
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
