"""LangChain chains for the Terms & Conditions Analyzer."""
from typing import Dict, Any, List, Optional, Union
from langchain.chains import (
    LLMChain,
    SequentialChain,
    RetrievalQA,
    ConversationalRetrievalChain,
    APIChain,
    create_structured_output_chain,
    create_extraction_chain,
    create_tagging_chain,
)
from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    FewShotChatMessagePromptTemplate,
)
from langchain_core.output_parsers import (
    PydanticOutputParser,
    OutputFixingParser,
    RetryOutputParser,
)
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    PromptTemplate,
)
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    get_buffer_string,
)
from langchain_core.runnables import RunnablePassthrough
from langchain_core.pydantic_v1 import BaseModel, Field
from enum import Enum
import json

from ..config import settings, logger

# Import any custom output schemas
from .schemas import (
    TermExtraction,
    TermAnalysis,
    TermComparison,
    TermSummary,
    LegalClause,
)

class ChainType(str, Enum):
    """Types of chains available in the application."""
    EXTRACTION = "extraction"
    ANALYSIS = "analysis"
    COMPARISON = "comparison"
    SUMMARIZATION = "summarization"
    QA = "qa"
    CONVERSATIONAL = "conversational"


def get_llm_chain(
    chain_type: Union[ChainType, str],
    llm=None,
    **kwargs
) -> Union[LLMChain, SequentialChain, RetrievalQA]:
    """Get a pre-configured chain for the specified type.
    
    Args:
        chain_type: Type of chain to create.
        llm: Language model to use. If None, a default will be used.
        **kwargs: Additional arguments to pass to the chain.
        
    Returns:
        A configured chain instance.
    """
    from langchain_openai import ChatOpenAI
    
    # Convert string to enum if needed
    if isinstance(chain_type, str):
        chain_type = ChainType(chain_type.lower())
    
    # Use provided LLM or create a default one
    if llm is None:
        llm = ChatOpenAI(
            model_name=settings.openai.model,
            temperature=settings.openai.temperature,
            max_tokens=settings.openai.max_tokens,
            **kwargs.pop("llm_kwargs", {})
        )
    
    # Get the appropriate chain based on the type
    if chain_type == ChainType.EXTRACTION:
        return _create_extraction_chain(llm, **kwargs)
    elif chain_type == ChainType.ANALYSIS:
        return _create_analysis_chain(llm, **kwargs)
    elif chain_type == ChainType.COMPARISON:
        return _create_comparison_chain(llm, **kwargs)
    elif chain_type == ChainType.SUMMARIZATION:
        return _create_summarization_chain(llm, **kwargs)
    elif chain_type == ChainType.QA:
        return _create_qa_chain(llm, **kwargs)
    elif chain_type == ChainType.CONVERSATIONAL:
        return _create_conversational_chain(llm, **kwargs)
    else:
        raise ValueError(f"Unsupported chain type: {chain_type}")


def _create_extraction_chain(llm, **kwargs):
    """Create a chain for extracting terms and clauses from text."""
    # Define the prompt template
    system_template = """You are an expert at analyzing legal documents and extracting key terms and clauses. 
    Extract all important terms, conditions, and legal clauses from the provided text. 
    Be thorough and include all relevant information, even if it seems obvious.
    """
    
    human_template = """Extract all important terms, conditions, and legal clauses from the following text:
    
    {text}
    
    {format_instructions}
    """
    
    # Create the parser for the output format
    parser = PydanticOutputParser(pydantic_object=TermExtraction)
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", human_template)
    ]).partial(
        format_instructions=parser.get_format_instructions()
    )
    
    # Create the chain
    chain = create_structured_output_chain(
        output_schema=TermExtraction,
        llm=llm,
        prompt=prompt,
        **kwargs
    )
    
    return chain


def _create_analysis_chain(llm, **kwargs):
    """Create a chain for analyzing terms and conditions."""
    # Define the prompt template
    system_template = """You are a legal expert specializing in analyzing terms and conditions. 
    Analyze the provided terms and conditions text and provide a detailed analysis.
    Be thorough and consider legal implications, potential risks, and important clauses.
    """
    
    human_template = """Analyze the following terms and conditions:
    
    {text}
    
    {format_instructions}
    """
    
    # Create the parser for the output format
    parser = PydanticOutputParser(pydantic_object=TermAnalysis)
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", human_template)
    ]).partial(
        format_instructions=parser.get_format_instructions()
    )
    
    # Create the chain
    chain = create_structured_output_chain(
        output_schema=TermAnalysis,
        llm=llm,
        prompt=prompt,
        **kwargs
    )
    
    return chain


def _create_comparison_chain(llm, **kwargs):
    """Create a chain for comparing two sets of terms and conditions."""
    # Define the prompt template
    system_template = """You are a legal expert specializing in comparing terms and conditions. 
    Compare the two provided sets of terms and conditions and highlight the key differences.
    Be thorough and consider legal implications, potential risks, and important clauses.
    """
    
    human_template = """Compare the following two sets of terms and conditions:
    
    TERMS 1:
    {terms1}
    
    TERMS 2:
    {terms2}
    
    {format_instructions}
    """
    
    # Create the parser for the output format
    parser = PydanticOutputParser(pydantic_object=TermComparison)
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", human_template)
    ]).partial(
        format_instructions=parser.get_format_instructions()
    )
    
    # Create the chain
    chain = create_structured_output_chain(
        output_schema=TermComparison,
        llm=llm,
        prompt=prompt,
        **kwargs
    )
    
    return chain


def _create_summarization_chain(llm, **kwargs):
    """Create a chain for summarizing terms and conditions."""
    # Define the prompt template
    system_template = """You are a legal expert specializing in summarizing terms and conditions. 
    Create a concise yet comprehensive summary of the provided terms and conditions.
    Focus on the most important points that users should be aware of.
    """
    
    human_template = """Summarize the following terms and conditions:
    
    {text}
    
    {format_instructions}
    """
    
    # Create the parser for the output format
    parser = PydanticOutputParser(pydantic_object=TermSummary)
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", human_template)
    ]).partial(
        format_instructions=parser.get_format_instructions()
    )
    
    # Create the chain
    chain = create_structured_output_chain(
        output_schema=TermSummary,
        llm=llm,
        prompt=prompt,
        **kwargs
    )
    
    return chain


def _create_qa_chain(llm, retriever=None, **kwargs):
    """Create a question-answering chain for terms and conditions."""
    from ..retrievers import default_retriever
    
    # Use the provided retriever or the default one
    retriever = retriever or default_retriever
    
    # Define the prompt template
    system_template = """You are a helpful assistant that answers questions about terms and conditions.
    Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    
    {context}
    """
    
    human_template = """Question: {question}
    Helpful Answer:"""
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", human_template)
    ])
    
    # Create the chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
        **kwargs
    )
    
    return chain


def _create_conversational_chain(llm, retriever=None, **kwargs):
    """Create a conversational chain for discussing terms and conditions."""
    from ..retrievers import default_retriever
    
    # Use the provided retriever or the default one
    retriever = retriever or default_retriever
    
    # Define the prompt template
    system_template = """You are a helpful assistant that answers questions about terms and conditions.
    Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    
    {context}
    
    Chat History:
    {chat_history}
    
    Human: {question}
    Assistant:"""
    
    # Create the prompt
    prompt = PromptTemplate(
        template=system_template,
        input_variables=["context", "chat_history", "question"]
    )
    
    # Create the chain
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True,
        **kwargs
    )
    
    return chain


# Create default chains for easy import
default_extraction_chain = get_llm_chain(ChainType.EXTRACTION)
default_analysis_chain = get_llm_chain(ChainType.ANALYSIS)
default_comparison_chain = get_llm_chain(ChainType.COMPARISON)
default_summarization_chain = get_llm_chain(ChainType.SUMMARIZATION)
default_qa_chain = get_llm_chain(ChainType.QA)
default_conversational_chain = get_llm_chain(ChainType.CONVERSATIONAL)

# Export public API
__all__ = [
    "ChainType",
    "get_llm_chain",
    "default_extraction_chain",
    "default_analysis_chain",
    "default_comparison_chain",
    "default_summarization_chain",
    "default_qa_chain",
    "default_conversational_chain"
]
