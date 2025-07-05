"""Vector store module for document embeddings and similarity search."""
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from ..config import settings, logger

class VectorStoreManager:
    """Manages the vector store for document embeddings and similarity search."""
    
    def __init__(self, collection_name: Optional[str] = None):
        """Initialize the vector store manager.
        
        Args:
            collection_name: Name of the collection to use. If None, uses the default from settings.
        """
        self.collection_name = collection_name or settings.vector_store.collection_name
        self.embedding_model = self._get_embedding_model()
        self.vector_store = self._initialize_vector_store()
    
    def _get_embedding_model(self):
        """Initialize the embedding model."""
        try:
            logger.info(f"Loading embedding model: {settings.vector_store.embedding_model}")
            return HuggingFaceEmbeddings(
                model_name=settings.vector_store.embedding_model,
                model_kwargs={'device': 'cpu'},  # Use 'cuda' if GPU is available
                encode_kwargs={'normalize_embeddings': True}
            )
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def _initialize_vector_store(self):
        """Initialize the vector store."""
        try:
            logger.info(f"Initializing vector store at {settings.vector_store.persist_directory}")
            return Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding_model,
                persist_directory=settings.vector_store.persist_directory
            )
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    async def add_documents(self, documents: List[Document], **kwargs) -> List[str]:
        """Add documents to the vector store.
        
        Args:
            documents: List of Document objects to add.
            **kwargs: Additional arguments to pass to the vector store.
            
        Returns:
            List of document IDs that were added.
        """
        try:
            logger.info(f"Adding {len(documents)} documents to vector store")
            return await self.vector_store.aadd_documents(documents, **kwargs)
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {e}")
            raise
    
    async def similarity_search(
        self, 
        query: str, 
        k: int = 4, 
        filter: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Document]:
        """Perform a similarity search.
        
        Args:
            query: The query string.
            k: Number of results to return.
            filter: Optional filter to apply to the search.
            **kwargs: Additional arguments to pass to the similarity search.
            
        Returns:
            List of documents most similar to the query.
        """
        try:
            logger.debug(f"Performing similarity search for query: {query[:100]}...")
            return await self.vector_store.asimilarity_search(
                query=query,
                k=k,
                filter=filter,
                **kwargs
            )
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise
    
    def persist(self):
        """Persist the vector store to disk."""
        try:
            self.vector_store.persist()
            logger.info("Vector store persisted to disk")
        except Exception as e:
            logger.error(f"Failed to persist vector store: {e}")
            raise
    
    def delete_collection(self):
        """Delete the current collection."""
        try:
            self.vector_store.delete_collection()
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise

# Create a default instance for easy import
default_vector_store = VectorStoreManager()

# Export public API
__all__ = ["VectorStoreManager", "default_vector_store"]
