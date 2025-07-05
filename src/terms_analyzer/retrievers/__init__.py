"""Retriever module for document retrieval using vector stores."""
from typing import List, Dict, Any, Optional, Union
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.retrievers import (
    ContextualCompressionRetriever,
    MultiQueryRetriever,
    EnsembleRetriever,
    BM25Retriever
)
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline,
    EmbeddingsFilter,
    LLMChainExtractor,
    LLMChainFilter,
)
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..vector_store import default_vector_store
from ..config import settings, logger

class VectorStoreRetriever(BaseRetriever):
    """A retriever that uses a vector store for similarity search."""
    
    def __init__(
        self,
        vector_store=None,
        search_type: str = "similarity",
        search_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize the vector store retriever.
        
        Args:
            vector_store: The vector store to use. If None, uses the default vector store.
            search_type: Type of search to perform ("similarity", "mmr", "similarity_score_threshold").
            search_kwargs: Additional keyword arguments for the search.
            **kwargs: Additional arguments to pass to the base retriever.
        """
        super().__init__(**kwargs)
        self.vector_store = vector_store or default_vector_store.vector_store
        self.search_type = search_type
        self.search_kwargs = search_kwargs or {"k": 4}
    
    def _get_relevant_documents(
        self, 
        query: str, 
        *, 
        run_manager: CallbackManagerForRetrieverRun = None,
        **kwargs
    ) -> List[Document]:
        """Get documents relevant to the query.
        
        Args:
            query: The query string.
            run_manager: Callback manager for the retriever run.
            **kwargs: Additional keyword arguments for the search.
            
        Returns:
            List of relevant documents.
        """
        try:
            logger.debug(f"Retrieving documents for query: {query[:100]}...")
            
            # Merge instance search_kwargs with any provided in the method call
            search_kwargs = {**self.search_kwargs, **kwargs}
            
            # Perform the search based on the search type
            if self.search_type == "mmr":
                docs = self.vector_store.max_marginal_relevance_search(
                    query=query,
                    **search_kwargs
                )
            elif self.search_type == "similarity_score_threshold":
                docs_and_scores = self.vector_store.similarity_search_with_score(
                    query=query,
                    **search_kwargs
                )
                docs = [doc for doc, score in docs_and_scores]
            else:  # Default to similarity search
                docs = self.vector_store.similarity_search(
                    query=query,
                    **search_kwargs
                )
            
            logger.info(f"Retrieved {len(docs)} documents for query")
            return docs
            
        except Exception as e:
            logger.error(f"Error in vector store retrieval: {e}")
            raise


def get_compression_retriever(
    base_retriever: BaseRetriever,
    compression_type: str = "embeddings",
    **kwargs
) -> ContextualCompressionRetriever:
    """Get a compression retriever with the specified compression type.
    
    Args:
        base_retriever: The base retriever to compress results from.
        compression_type: Type of compression to apply ("embeddings", "llm_chain", "extraction").
        **kwargs: Additional keyword arguments for the compressor.
        
    Returns:
        A ContextualCompressionRetriever instance.
    """
    from langchain.embeddings import OpenAIEmbeddings
    from ..chains.llm import get_llm_chain
    
    # Get the appropriate compressor based on the compression type
    if compression_type == "embeddings":
        embeddings = OpenAIEmbeddings()
        compressor = EmbeddingsFilter(
            embeddings=embeddings,
            similarity_threshold=kwargs.get("similarity_threshold", 0.76)
        )
    elif compression_type == "llm_chain":
        compressor = LLMChainFilter.from_llm(
            llm=get_llm_chain().llm,
            **kwargs
        )
    elif compression_type == "extraction":
        compressor = LLMChainExtractor.from_llm(
            llm=get_llm_chain().llm,
            **kwargs
        )
    else:
        raise ValueError(f"Unsupported compression type: {compression_type}")
    
    # Create a pipeline with the compressor
    pipeline_compressor = DocumentCompressorPipeline(transformers=[compressor])
    
    # Return the compression retriever
    return ContextualCompressionRetriever(
        base_compressor=pipeline_compressor,
        base_retriever=base_retriever
    )


def get_multi_query_retriever(
    vector_store=None,
    llm=None,
    **kwargs
) -> MultiQueryRetriever:
    """Get a multi-query retriever that generates multiple queries.
    
    Args:
        vector_store: The vector store to use. If None, uses the default vector store.
        llm: The language model to use for query generation.
        **kwargs: Additional keyword arguments for the retriever.
        
    Returns:
        A MultiQueryRetriever instance.
    """
    from ..chains.llm import get_llm_chain
    
    vector_store = vector_store or default_vector_store.vector_store
    llm = llm or get_llm_chain().llm
    
    return MultiQueryRetriever.from_llm(
        retriever=vector_store.as_retriever(**kwargs),
        llm=llm
    )


def get_ensemble_retriever(
    retrievers: List[BaseRetriever],
    weights: Optional[List[float]] = None
) -> EnsembleRetriever:
    """Get an ensemble retriever that combines multiple retrievers.
    
    Args:
        retrievers: List of retrievers to combine.
        weights: Optional list of weights for each retriever.
        
    Returns:
        An EnsembleRetriever instance.
    """
    if not retrievers:
        raise ValueError("At least one retriever must be provided")
    
    if weights and len(weights) != len(retrievers):
        raise ValueError("Number of weights must match number of retrievers")
    
    return EnsembleRetriever(
        retrievers=retrievers,
        weights=weights or [1.0 / len(retrievers)] * len(retrievers)
    )


# Create a default retriever for easy import
default_retriever = VectorStoreRetriever()

# Export public API
__all__ = [
    "VectorStoreRetriever",
    "get_compression_retriever",
    "get_multi_query_retriever",
    "get_ensemble_retriever",
    "default_retriever"
]
