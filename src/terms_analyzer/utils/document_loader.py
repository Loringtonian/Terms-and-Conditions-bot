"""Document loading utilities for the Terms & Conditions Analyzer."""
import logging
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredFileLoader,
    WebBaseLoader,
    SeleniumURLLoader
)
from langchain_core.documents import Document
from ..config import settings, logger

class DocumentLoader:
    """Handles loading of documents from various sources and formats."""
    
    @staticmethod
    def load_document(file_path: Union[str, Path], **kwargs) -> List[Document]:
        """Load a single document from a file path.
        
        Args:
            file_path: Path to the document file.
            **kwargs: Additional arguments to pass to the loader.
            
        Returns:
            List of Document objects.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        loader = DocumentLoader._get_loader(file_path, **kwargs)
        return loader.load()
    
    @staticmethod
    def load_documents(directory: Union[str, Path], **kwargs) -> List[Document]:
        """Load multiple documents from a directory.
        
        Args:
            directory: Directory containing document files.
            **kwargs: Additional arguments to pass to the loaders.
            
        Returns:
            List of Document objects from all files in the directory.
        """
        directory = Path(directory)
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")
            
        documents = []
        for file_path in directory.glob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    docs = DocumentLoader.load_document(file_path, **kwargs)
                    documents.extend(docs)
                    logger.info(f"Loaded {len(docs)} documents from {file_path.name}")
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")
                    continue
        
        return documents
    
    @staticmethod
    def load_web_document(url: str, **kwargs) -> List[Document]:
        """Load a document from a web URL.
        
        Args:
            url: URL of the web document.
            **kwargs: Additional arguments to pass to the loader.
            
        Returns:
            List of Document objects.
        """
        try:
            # Try WebBaseLoader first (simpler, faster for most cases)
            loader = WebBaseLoader([url], **kwargs)
            return loader.load()
        except Exception as e:
            logger.warning(f"WebBaseLoader failed, falling back to Selenium: {e}")
            # Fall back to Selenium if WebBaseLoader fails
            loader = SeleniumURLLoader([url], **kwargs)
            return loader.load()
    
    @staticmethod
    def _get_loader(file_path: Path, **kwargs):
        """Get the appropriate loader for the given file path.
        
        Args:
            file_path: Path to the file to load.
            **kwargs: Additional arguments to pass to the loader.
            
        Returns:
            A document loader instance.
            
        Raises:
            ValueError: If the file type is not supported.
        """
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()
        
        # Map file extensions to their respective loaders
        loader_map = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.txt': TextLoader,
            '.md': TextLoader,
            '.html': TextLoader,
            '.htm': TextLoader,
        }
        
        # Get the appropriate loader class
        loader_class = loader_map.get(suffix)
        
        if loader_class:
            # Special handling for PDFs to extract metadata
            if suffix == '.pdf':
                kwargs.setdefault('extract_images', False)
                kwargs.setdefault('extract_metadata', True)
            return loader_class(str(file_path), **kwargs)
        
        # Fall back to UnstructuredFileLoader for other file types
        try:
            return UnstructuredFileLoader(str(file_path), **kwargs)
        except Exception as e:
            raise ValueError(
                f"Unsupported file type: {suffix}. "
                f"Supported types: {', '.join(loader_map.keys())}"
            ) from e

# Create a default instance for easy use
default_document_loader = DocumentLoader()

# Export public API
__all__ = ["DocumentLoader", "default_document_loader"]
