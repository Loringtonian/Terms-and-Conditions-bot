#!/usr/bin/env python3
"""
Manage terms and conditions tracking.
"""
import sys
import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from terms_analyzer.models import (
    SessionLocal, Service, Category, Document, Analysis,
    ServiceStatus, DocumentType, AnalysisStatus,
    ServiceResponse, DocumentResponse, AnalysisResponse
)
from terms_analyzer.utils.document_loader import default_document_loader
from terms_analyzer.vector_store import default_vector_store
from terms_analyzer.chains import ChainType, get_llm_chain

class TermsManager:
    """Manage terms and conditions tracking."""
    
    def __init__(self, db_session=None):
        """Initialize the terms manager."""
        self.db = db_session or SessionLocal()
    
    def __del__(self):
        """Clean up the database session."""
        if hasattr(self, 'db'):
            self.db.close()
    
    def get_service(self, service_name: str) -> Optional[Service]:
        """Get a service by name."""
        return self.db.query(Service).filter(Service.name == service_name).first()
    
    def list_services(self, status: Optional[str] = None) -> List[Service]:
        """List all services, optionally filtered by status."""
        query = self.db.query(Service)
        if status:
            query = query.filter(Service.status == status)
        return query.order_by(Service.name).all()
    
    def add_service(
        self,
        name: str,
        display_name: Optional[str] = None,
        description: str = "",
        website_url: str = "",
        categories: List[str] = None,
        documents: List[Dict[str, Any]] = None
    ) -> Service:
        """Add a new service to track."""
        # Check if service already exists
        service = self.get_service(name)
        if service:
            print(f"Service '{name}' already exists.")
            return service
        
        # Create new service
        service = Service(
            name=name,
            display_name=display_name or name.title(),
            description=description,
            website_url=website_url,
            status=ServiceStatus.PENDING,
            is_active=True,
            metadata_={"created_at": datetime.now(timezone.utc).isoformat()}
        )
        
        # Add categories
        if categories:
            for cat_name in categories:
                category = self.db.query(Category).filter(
                    func.lower(Category.name) == cat_name.lower()
                ).first()
                if category:
                    service.categories.append(category)
        
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        
        # Add documents if provided
        if documents:
            for doc_data in documents:
                self.add_document(
                    service_id=service.id,
                    **doc_data
                )
        
        print(f"Added service: {service.display_name} (ID: {service.id})")
        return service
    
    def add_document(
        self,
        service_id: int,
        document_type: str,
        source_url: str,
        version: Optional[str] = None,
        language: str = "en",
        file_path: Optional[str] = None,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """Add a document to a service."""
        # Check if document already exists for this service and type
        existing = self.db.query(Document).filter(
            Document.service_id == service_id,
            Document.document_type == document_type,
            Document.is_current == True
        ).first()
        
        if existing:
            print(f"Document of type '{document_type}' already exists for service ID {service_id}.")
            return existing
        
        # Calculate content hash if content is provided
        content_hash = None
        if content:
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # Create new document
        doc = Document(
            service_id=service_id,
            document_type=document_type,
            source_url=source_url,
            version=version,
            language=language,
            content_hash=content_hash,
            raw_content=content,
            file_path=file_path,
            is_current=True,
            metadata_=metadata or {},
            last_retrieved=datetime.now(timezone.utc)
        )
        
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        
        print(f"Added document: {document_type} (ID: {doc.id})")
        return doc
    
    def update_document_content(
        self,
        document_id: int,
        content: str,
        version: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> Optional[Document]:
        """Update a document's content and mark as new version if changed."""
        doc = self.db.query(Document).get(document_id)
        if not doc:
            print(f"Document with ID {document_id} not found.")
            return None
        
        # Calculate content hash
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # Check if content has changed
        if doc.content_hash == content_hash:
            print("Document content has not changed.")
            return doc
        
        # Mark current document as not current
        doc.is_current = False
        self.db.add(doc)
        
        # Create new document version
        new_doc = Document(
            service_id=doc.service_id,
            document_type=doc.document_type,
            source_url=source_url or doc.source_url,
            version=version or doc.version,
            language=doc.language,
            content_hash=content_hash,
            raw_content=content,
            file_path=doc.file_path,
            is_current=True,
            metadata_=doc.metadata_.copy(),
            last_retrieved=datetime.now(timezone.utc),
            effective_date=datetime.now(timezone.utc)
        )
        
        self.db.add(new_doc)
        self.db.commit()
        self.db.refresh(new_doc)
        
        print(f"Updated document: {new_doc.document_type} (New ID: {new_doc.id})")
        return new_doc
    
    def analyze_document(
        self,
        document_id: int,
        analysis_type: str = "full_analysis",
        force: bool = False
    ) -> Optional[Analysis]:
        """Analyze a document using the appropriate chain."""
        doc = self.db.query(Document).get(document_id)
        if not doc:
            print(f"Document with ID {document_id} not found.")
            return None
        
        # Check if analysis already exists and is up to date
        if not force:
            existing = self.db.query(Analysis).filter(
                Analysis.document_id == document_id,
                Analysis.analysis_type == analysis_type,
                Analysis.status == AnalysisStatus.COMPLETED
            ).order_by(Analysis.completed_at.desc()).first()
            
            if existing and existing.completed_at > doc.last_retrieved:
                print(f"Using cached {analysis_type} analysis from {existing.completed_at}")
                return existing
        
        # Get the appropriate chain based on analysis type
        if analysis_type == "summary":
            chain_type = ChainType.SUMMARIZATION
        elif analysis_type == "extraction":
            chain_type = ChainType.EXTRACTION
        else:  # full_analysis
            chain_type = ChainType.ANALYSIS
        
        # Create a new analysis record
        analysis = Analysis(
            document_id=document_id,
            analysis_type=analysis_type,
            status=AnalysisStatus.PROCESSING,
            model_name=settings.openai.model,
            metadata_={"started_at": datetime.now(timezone.utc).isoformat()}
        )
        
        self.db.add(analysis)
        self.db.commit()
        
        try:
            # Get the document content
            content = doc.raw_content
            if not content and doc.file_path and os.path.exists(doc.file_path):
                with open(doc.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            if not content:
                raise ValueError("No content available for analysis")
            
            # Run the analysis
            chain = get_llm_chain(chain_type)
            result = chain.run({"text": content})
            
            # Update the analysis record
            analysis.status = AnalysisStatus.COMPLETED
            analysis.result = result if isinstance(result, dict) else {"output": str(result)}
            analysis.completed_at = datetime.now(timezone.utc)
            analysis.metadata_["completed_at"] = analysis.completed_at.isoformat()
            
            # Update the service status if this is the first successful analysis
            if doc.service.status == ServiceStatus.PENDING:
                doc.service.status = ServiceStatus.COMPLETED
                self.db.add(doc.service)
            
            self.db.commit()
            self.db.refresh(analysis)
            
            print(f"Completed {analysis_type} analysis for document {document_id}")
            return analysis
            
        except Exception as e:
            # Update the analysis record with error
            analysis.status = AnalysisStatus.FAILED
            analysis.error = str(e)
            analysis.completed_at = datetime.now(timezone.utc)
            analysis.metadata_["error"] = str(e)
            
            # Update the service status
            doc.service.status = ServiceStatus.FAILED
            self.db.add(doc.service)
            
            self.db.commit()
            self.db.refresh(analysis)
            
            print(f"Error analyzing document {document_id}: {e}")
            return analysis
    
    def get_service_status(self, service_id: int) -> Dict[str, Any]:
        """Get the status of a service and its documents."""
        service = self.db.query(Service).get(service_id)
        if not service:
            return {"error": f"Service with ID {service_id} not found."}
        
        # Get all documents for this service
        documents = self.db.query(Document).filter(
            Document.service_id == service_id,
            Document.is_current == True
        ).all()
        
        # Get all analyses for these documents
        document_ids = [doc.id for doc in documents]
        analyses = {}
        
        if document_ids:
            analysis_records = self.db.query(Analysis).filter(
                Analysis.document_id.in_(document_ids)
            ).all()
            
            for analysis in analysis_records:
                if analysis.document_id not in analyses:
                    analyses[analysis.document_id] = []
                analyses[analysis.document_id].append({
                    "id": analysis.id,
                    "analysis_type": analysis.analysis_type,
                    "status": analysis.status,
                    "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None
                })
        
        # Format the response
        return {
            "service_id": service.id,
            "name": service.name,
            "display_name": service.display_name,
            "status": service.status,
            "documents": [
                {
                    "id": doc.id,
                    "document_type": doc.document_type,
                    "version": doc.version,
                    "source_url": doc.source_url,
                    "last_retrieved": doc.last_retrieved.isoformat() if doc.last_retrieved else None,
                    "analyses": analyses.get(doc.id, [])
                }
                for doc in documents
            ]
        }

def main():
    """Command-line interface for managing terms and conditions."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage terms and conditions tracking.")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List services
    list_parser = subparsers.add_parser("list", help="List services")
    list_parser.add_argument("--status", help="Filter by status")
    
    # Add service
    add_parser = subparsers.add_parser("add", help="Add a new service")
    add_parser.add_argument("name", help="Service name (unique identifier)")
    add_parser.add_argument("--display-name", help="Display name")
    add_parser.add_argument("--description", help="Service description")
    add_parser.add_argument("--website", help="Service website URL")
    add_parser.add_argument("--categories", nargs="+", help="Category names")
    
    # Add document
    doc_parser = subparsers.add_parser("add-doc", help="Add a document to a service")
    doc_parser.add_argument("service", help="Service name or ID")
    doc_parser.add_argument("type", help="Document type (e.g., terms_of_service, privacy_policy)")
    doc_parser.add_argument("url", help="Source URL")
    doc_parser.add_argument("--version", help="Document version")
    doc_parser.add_argument("--language", default="en", help="Document language code")
    doc_parser.add_argument("--file", help="Path to local file with content")
    
    # Update document content
    update_parser = subparsers.add_parser("update-doc", help="Update document content")
    update_parser.add_argument("document_id", type=int, help="Document ID")
    update_parser.add_argument("file", help="Path to file with new content")
    update_parser.add_argument("--version", help="New version identifier")
    update_parser.add_argument("--url", help="New source URL")
    
    # Analyze document
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a document")
    analyze_parser.add_argument("document_id", type=int, help="Document ID")
    analyze_parser.add_argument("--type", default="full_analysis",
                              choices=["summary", "extraction", "full_analysis"],
                              help="Type of analysis")
    analyze_parser.add_argument("--force", action="store_true",
                               help="Force re-analysis even if already analyzed")
    
    # Get status
    status_parser = subparsers.add_parser("status", help="Get service status")
    status_parser.add_argument("service_id", type=int, help="Service ID")
    
    args = parser.parse_args()
    
    manager = TermsManager()
    
    try:
        if args.command == "list":
            services = manager.list_services(status=args.status)
            for service in services:
                print(f"{service.id}: {service.display_name} ({service.status})")
        
        elif args.command == "add":
            service = manager.add_service(
                name=args.name,
                display_name=args.display_name,
                description=args.description or "",
                website_url=args.website or "",
                categories=args.categories or []
            )
            print(f"Added service: {service.name} (ID: {service.id})")
        
        elif args.command == "add-doc":
            # Find service by name or ID
            try:
                service_id = int(args.service)
                service = manager.db.query(Service).get(service_id)
            except ValueError:
                service = manager.get_service(args.service)
            
            if not service:
                print(f"Service '{args.service}' not found.")
                return 1
            
            # Read file content if provided
            content = None
            if args.file and os.path.exists(args.file):
                with open(args.file, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            doc = manager.add_document(
                service_id=service.id,
                document_type=args.type,
                source_url=args.url,
                version=args.version,
                language=args.language,
                file_path=args.file,
                content=content
            )
            print(f"Added document: {doc.document_type} (ID: {doc.id})")
        
        elif args.command == "update-doc":
            if not os.path.exists(args.file):
                print(f"File not found: {args.file}")
                return 1
            
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc = manager.update_document_content(
                document_id=args.document_id,
                content=content,
                version=args.version,
                source_url=args.url
            )
            
            if doc:
                print(f"Updated document: {doc.document_type} (ID: {doc.id})")
        
        elif args.command == "analyze":
            analysis = manager.analyze_document(
                document_id=args.document_id,
                analysis_type=args.type,
                force=args.force
            )
            
            if analysis:
                if analysis.status == AnalysisStatus.COMPLETED:
                    print(f"Analysis completed successfully (ID: {analysis.id})")
                    print(json.dumps(analysis.result, indent=2))
                else:
                    print(f"Analysis failed: {analysis.error}")
        
        elif args.command == "status":
            status = manager.get_service_status(args.service_id)
            if "error" in status:
                print(status["error"])
                return 1
            
            print(f"Service: {status['display_name']} ({status['name']})")
            print(f"Status: {status['status']}")
            print("\nDocuments:")
            
            for doc in status["documents"]:
                print(f"\n  {doc['document_type'].replace('_', ' ').title()}")
                print(f"  URL: {doc['source_url']}")
                if doc['version']:
                    print(f"  Version: {doc['version']}")
                print(f"  Last Retrieved: {doc['last_retrieved']}")
                
                if doc['analyses']:
                    print("  Analyses:")
                    for analysis in doc['analyses']:
                        print(f"    - {analysis['analysis_type']}: {analysis['status']} "
                              f"(Completed: {analysis['completed_at']})")
        
        else:
            parser.print_help()
    
    finally:
        manager.db.close()

if __name__ == "__main__":
    main()
