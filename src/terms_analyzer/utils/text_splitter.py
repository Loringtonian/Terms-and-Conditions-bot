"""Text splitting utilities for document processing."""
from typing import List, Optional, Dict, Any, Callable
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    HTMLHeaderTextSplitter,
    TokenTextSplitter
)
from langchain_core.documents import Document
from ..config import settings, logger

class DocumentSplitter:
    """Handles splitting of documents into smaller chunks for processing."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None,
        length_function: Callable[[str], int] = len,
        **kwargs
    ):
        """Initialize the document splitter.
        
        Args:
            chunk_size: Maximum size of chunks to create.
            chunk_overlap: Number of characters to overlap between chunks.
            separators: List of separators to use for splitting.
            length_function: Function to calculate the length of text.
            **kwargs: Additional arguments to pass to the splitter.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or [
            "\n\n", "\n", ". ", " ", ""  # Default separators
        ]
        self.length_function = length_function
        self.kwargs = kwargs
    
    def split_documents(self, documents: List[Document], **kwargs) -> List[Document]:
        """Split documents into smaller chunks.
        
        Args:
            documents: List of documents to split.
            **kwargs: Additional arguments to override the defaults.
            
        Returns:
            List of split documents.
        """
        # Use provided kwargs or fall back to instance defaults
        chunk_size = kwargs.get('chunk_size', self.chunk_size)
        chunk_overlap = kwargs.get('chunk_overlap', self.chunk_overlap)
        separators = kwargs.get('separators', self.separators)
        
        # Initialize the splitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=self.length_function,
            **{k: v for k, v in self.kwargs.items() if k not in kwargs}
        )
        
        # Split the documents
        return splitter.split_documents(documents)
    
    def split_text(self, text: str, **kwargs) -> List[str]:
        """Split a single text into chunks.
        
        Args:
            text: The text to split.
            **kwargs: Additional arguments to override the defaults.
            
        Returns:
            List of text chunks.
        """
        # Use provided kwargs or fall back to instance defaults
        chunk_size = kwargs.get('chunk_size', self.chunk_size)
        chunk_overlap = kwargs.get('chunk_overlap', self.chunk_overlap)
        separators = kwargs.get('separators', self.separators)
        
        # Initialize the splitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=self.length_function,
            **{k: v for k, v in self.kwargs.items() if k not in kwargs}
        )
        
        # Split the text
        return splitter.split_text(text)


class MarkdownSplitter:
    """Specialized splitter for Markdown documents with header awareness."""
    
    def __init__(
        self,
        headers_to_split_on: Optional[List[tuple[str, str]]] = None,
        **kwargs
    ):
        """Initialize the Markdown splitter.
        
        Args:
            headers_to_split_on: List of tuples of (header, header_level) to split on.
            **kwargs: Additional arguments to pass to the splitter.
        """
        self.headers_to_split_on = headers_to_split_on or [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        self.kwargs = kwargs
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split Markdown documents by headers.
        
        Args:
            documents: List of Markdown documents to split.
            
        Returns:
            List of split documents with header metadata.
        """
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            **self.kwargs
        )
        
        split_docs = []
        for doc in documents:
            try:
                splits = markdown_splitter.split_text(doc.page_content)
                # Copy metadata from original document to each split
                for split in splits:
                    split.metadata.update(doc.metadata)
                split_docs.extend(splits)
            except Exception as e:
                logger.error(f"Error splitting Markdown document: {e}")
                # Fall back to regular text splitting if Markdown splitting fails
                splitter = DocumentSplitter()
                split_docs.extend(splitter.split_documents([doc]))
        
        return split_docs


class HTMLSplitter:
    """Specialized splitter for HTML documents with header awareness."""
    
    def __init__(
        self,
        headers_to_split_on: Optional[List[tuple[str, str]]] = None,
        **kwargs
    ):
        """Initialize the HTML splitter.
        
        Args:
            headers_to_split_on: List of tuples of (header_tag, header_name) to split on.
            **kwargs: Additional arguments to pass to the splitter.
        """
        self.headers_to_split_on = headers_to_split_on or [
            ("h1", "Header 1"),
            ("h2", "Header 2"),
            ("h3", "Header 3"),
            ("h4", "Header 4"),
            ("h5", "Header 5"),
            ("h6", "Header 6"),
        ]
        self.kwargs = kwargs
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split HTML documents by headers.
        
        Args:
            documents: List of HTML documents to split.
            
        Returns:
            List of split documents with header metadata.
        """
        html_splitter = HTMLHeaderTextSplitter(
            headers_to_split_on={
                tag: name for tag, name in self.headers_to_split_on
            },
            **self.kwargs
        )
        
        split_docs = []
        for doc in documents:
            try:
                splits = html_splitter.split_text(doc.page_content)
                # Copy metadata from original document to each split
                for split in splits:
                    split.metadata.update(doc.metadata)
                split_docs.extend(splits)
            except Exception as e:
                logger.error(f"Error splitting HTML document: {e}")
                # Fall back to regular text splitting if HTML splitting fails
                splitter = DocumentSplitter()
                split_docs.extend(splitter.split_documents([doc]))
        
        return split_docs


# Create default instances for easy use
default_splitter = DocumentSplitter()
markdown_splitter = MarkdownSplitter()
html_splitter = HTMLSplitter()

# Export public API
__all__ = [
    "DocumentSplitter", 
    "MarkdownSplitter", 
    "HTMLSplitter",
    "default_splitter",
    "markdown_splitter",
    "html_splitter"
]
