"""Tools for the Terms & Conditions Analyzer agents."""
from typing import Dict, List, Any, Optional, Union
import json
from pathlib import Path
import logging
from langchain.tools import BaseTool, tool
from langchain_core.tools import ToolException
from langchain_core.callbacks.manager import CallbackManagerForToolRun

from ..config import settings, logger
from ..chains import (
    get_llm_chain,
    ChainType,
    TermExtraction,
    TermAnalysis,
    TermComparison,
    TermSummary,
)
from ..vector_store import default_vector_store
from ..retrievers import default_retriever

# Set up logging
logger = logging.getLogger(__name__)

# Helper function to handle tool errors
def handle_tool_error(error: Exception) -> str:
    """Handle errors in tool execution and return a user-friendly message."""
    logger.error(f"Tool error: {error}", exc_info=True)
    return f"An error occurred while executing the tool: {str(error)}. Please try again or check the logs for more details."

@tool
async def search_terms_conditions(
    query: str,
    max_results: int = 3,
    **kwargs
) -> str:
    """Search for terms and conditions documents based on a query.
    
    Args:
        query: The search query (e.g., "Spotify terms of service 2023").
        max_results: Maximum number of results to return (default: 3).
        **kwargs: Additional keyword arguments for the search.
        
    Returns:
        A string containing the search results.
    """
    try:
        # Use the Tavily MCP server for web search
        from mcp import MCPClient
        
        # Initialize the MCP client
        client = MCPClient()
        
        # Execute the search
        results = client.search(
            query=query,
            max_results=max_results,
            include_raw_content=True,
            **kwargs
        )
        
        # Format the results
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append(
                f"{i}. {result.get('title', 'No title')}\n"
                f"   URL: {result.get('url', 'No URL')}\n"
                f"   Snippet: {result.get('content', 'No content')[:200]}..."
            )
        
        return "\n\n".join(formatted_results) if formatted_results \
            else "No results found. Try a different search query."
            
    except Exception as e:
        return handle_tool_error(e)

@tool
async def analyze_terms(
    text: str,
    format_output: bool = True,
    **kwargs
) -> Union[str, Dict[str, Any]]:
    """Analyze terms and conditions text and provide a detailed analysis.
    
    Args:
        text: The terms and conditions text to analyze.
        format_output: Whether to format the output as a string (True) or return raw data (False).
        **kwargs: Additional keyword arguments for the analysis.
        
    Returns:
        A string or dictionary containing the analysis results.
    """
    try:
        # Get the analysis chain
        chain = get_llm_chain(ChainType.ANALYSIS, **kwargs)
        
        # Run the analysis
        result = await chain.ainvoke({"text": text})
        
        # Format the output if requested
        if format_output:
            analysis = result.get("text", {})
            if isinstance(analysis, dict):
                output = [
                    f"# Analysis of Terms and Conditions",
                    f"## Summary\n{analysis.get('summary', 'No summary available.')}",
                    f"## Overall Severity: {analysis.get('overall_severity', 'N/A')}",
                    "## Key Points"
                ]
                
                # Add key points
                for i, point in enumerate(analysis.get('key_points', []), 1):
                    output.append(f"{i}. {point}")
                
                # Add privacy concerns if any
                if analysis.get('privacy_concerns'):
                    output.append("\n## Privacy Concerns")
                    for i, concern in enumerate(analysis.get('privacy_concerns', []), 1):
                        output.append(f"{i}. {concern}")
                
                # Add recommendations if any
                if analysis.get('recommendations'):
                    output.append("\n## Recommendations")
                    for i, rec in enumerate(analysis.get('recommendations', []), 1):
                        output.append(f"{i}. {rec}")
                
                return "\n".join(output)
            return str(analysis)
        
        return result.get("text", {})
        
    except Exception as e:
        return handle_tool_error(e)

@tool
async def compare_terms(
    terms1: str,
    terms2: str,
    format_output: bool = True,
    **kwargs
) -> Union[str, Dict[str, Any]]:
    """Compare two sets of terms and conditions and highlight differences.
    
    Args:
        terms1: First set of terms and conditions.
        terms2: Second set of terms and conditions to compare with the first.
        format_output: Whether to format the output as a string (True) or return raw data (False).
        **kwargs: Additional keyword arguments for the comparison.
        
    Returns:
        A string or dictionary containing the comparison results.
    """
    try:
        # Get the comparison chain
        chain = get_llm_chain(ChainType.COMPARISON, **kwargs)
        
        # Run the comparison
        result = await chain.ainvoke({"terms1": terms1, "terms2": terms2})
        
        # Format the output if requested
        if format_output:
            comparison = result.get("text", {})
            if isinstance(comparison, dict):
                output = [
                    f"# Comparison of Terms and Conditions",
                    f"## Summary\n{comparison.get('summary', 'No summary available.')}",
                    f"## Overall Similarity: {comparison.get('overall_similarity', 0) * 100:.1f}%"
                ]
                
                # Add key differences
                if comparison.get('key_differences'):
                    output.append("\n## Key Differences")
                    for i, diff in enumerate(comparison.get('key_differences', []), 1):
                        output.append(f"{i}. {diff.get('description', 'No description')}")
                
                # Add missing clauses
                if comparison.get('missing_in_doc1'):
                    output.append("\n## Clauses in Document 2 but missing in Document 1")
                    for i, clause in enumerate(comparison.get('missing_in_doc1', []), 1):
                        output.append(f"{i}. {clause.get('title', 'Untitled')}")
                
                if comparison.get('missing_in_doc2'):
                    output.append("\n## Clauses in Document 1 but missing in Document 2")
                    for i, clause in enumerate(comparison.get('missing_in_doc2', []), 1):
                        output.append(f"{i}. {clause.get('title', 'Untitled')}")
                
                return "\n".join(output)
            return str(comparison)
        
        return result.get("text", {})
        
    except Exception as e:
        return handle_tool_error(e)

@tool
async def summarize_terms(
    text: str,
    format_output: bool = True,
    **kwargs
) -> Union[str, Dict[str, Any]]:
    """Generate a concise summary of terms and conditions.
    
    Args:
        text: The terms and conditions text to summarize.
        format_output: Whether to format the output as a string (True) or return raw data (False).
        **kwargs: Additional keyword arguments for the summarization.
        
    Returns:
        A string or dictionary containing the summary.
    """
    try:
        # Get the summarization chain
        chain = get_llm_chain(ChainType.SUMMARIZATION, **kwargs)
        
        # Run the summarization
        result = await chain.ainvoke({"text": text})
        
        # Format the output if requested
        if format_output:
            summary = result.get("text", {})
            if isinstance(summary, dict):
                output = [
                    f"# Summary of Terms and Conditions",
                    f"## {summary.get('document_title', 'Untitled Document')}",
                    f"\n{summary.get('summary', 'No summary available.')}",
                ]
                
                # Add key points
                if summary.get('key_points'):
                    output.append("\n## Key Points")
                    for i, point in enumerate(summary.get('key_points', []), 1):
                        output.append(f"{i}. {point}")
                
                # Add important clauses
                if summary.get('important_clauses'):
                    output.append("\n## Important Clauses")
                    for i, clause in enumerate(summary.get('important_clauses', []), 1):
                        output.append(f"{i}. **{clause.get('title', 'Untitled')}**")
                        output.append(f"   {clause.get('summary', 'No summary')}")
                
                return "\n".join(output)
            return str(summary)
        
        return result.get("text", {})
        
    except Exception as e:
        return handle_tool_error(e)

@tool
async def extract_clauses(
    text: str,
    clause_types: Optional[List[str]] = None,
    format_output: bool = True,
    **kwargs
) -> Union[str, Dict[str, Any]]:
    """Extract specific legal clauses from terms and conditions.
    
    Args:
        text: The terms and conditions text to extract clauses from.
        clause_types: List of clause types to extract (e.g., ["privacy", "payment"]).
                     If None, extracts all clauses.
        format_output: Whether to format the output as a string (True) or return raw data (False).
        **kwargs: Additional keyword arguments for the extraction.
        
    Returns:
        A string or dictionary containing the extracted clauses.
    """
    try:
        # Get the extraction chain
        chain = get_llm_chain(ChainType.EXTRACTION, **kwargs)
        
        # Run the extraction
        result = await chain.ainvoke({"text": text})
        
        # Filter clauses by type if specified
        if clause_types:
            if isinstance(result.get("text"), dict):
                result["text"]["clauses"] = [
                    clause for clause in result["text"].get("clauses", [])
                    if clause.get("type") in clause_types
                ]
        
        # Format the output if requested
        if format_output:
            extraction = result.get("text", {})
            if isinstance(extraction, dict):
                output = [
                    f"# Extracted Clauses",
                    f"## {extraction.get('document_title', 'Untitled Document')}",
                ]
                
                # Group clauses by type
                clauses_by_type = {}
                for clause in extraction.get("clauses", []):
                    clause_type = clause.get("type", "other")
                    if clause_type not in clauses_by_type:
                        clauses_by_type[clause_type] = []
                    clauses_by_type[clause_type].append(clause)
                
                # Add clauses by type
                for clause_type, clauses in clauses_by_type.items():
                    output.append(f"\n## {clause_type.replace('_', ' ').title()} Clauses")
                    for i, clause in enumerate(clauses, 1):
                        output.append(f"\n### {i}. {clause.get('title', 'Untitled Clause')}")
                        output.append(f"**Severity:** {clause.get('severity', 'N/A')}")
                        output.append(f"\n{clause.get('summary', 'No summary available.')}")
                        
                        # Add concerns if any
                        if clause.get('concerns'):
                            output.append("\n**Potential Concerns:**")
                            for j, concern in enumerate(clause.get('concerns', []), 1):
                                output.append(f"  {j}. {concern}")
                        
                        # Add user rights if any
                        if clause.get('user_rights'):
                            output.append("\n**User Rights:**")
                            for j, right in enumerate(clause.get('user_rights', []), 1):
                                output.append(f"  {j}. {right}")
                
                return "\n".join(output)
            return str(extraction)
        
        return result.get("text", {})
        
    except Exception as e:
        return handle_tool_error(e)

@tool
async def answer_question(
    question: str,
    context: Optional[str] = None,
    format_output: bool = True,
    **kwargs
) -> str:
    """Answer a question about terms and conditions.
    
    Args:
        question: The question to answer.
        context: Optional context or terms and conditions text to use for answering.
        format_output: Whether to format the output as a string (True) or return raw data (False).
        **kwargs: Additional keyword arguments for the QA chain.
        
    Returns:
        A string containing the answer to the question.
    """
    try:
        # If context is provided, use it directly
        if context:
            chain = get_llm_chain(ChainType.QA, **kwargs)
            result = await chain.ainvoke({"question": question, "context": context})
        else:
            # Otherwise, use the retriever to find relevant context
            from langchain.chains import RetrievalQA
            
            qa_chain = RetrievalQA.from_chain_type(
                llm=get_llm_chain(ChainType.QA, **kwargs).llm,
                chain_type="stuff",
                retriever=default_retriever,
                return_source_documents=True,
                **kwargs
            )
            
            result = await qa_chain.ainvoke({"query": question, "input_documents": []})
        
        # Format the output
        if format_output:
            answer = result.get("result", "I couldn't find an answer to that question.")
            sources = result.get("source_documents", [])
            
            if sources:
                answer += "\n\n**Sources:**"
                for i, doc in enumerate(sources, 1):
                    source = doc.metadata.get("source", "Unknown source")
                    answer += f"\n{i}. {source}"
            
            return answer
        
        return result
        
    except Exception as e:
        return handle_tool_error(e)

# Export all tools
__all__ = [
    "search_terms_conditions",
    "analyze_terms",
    "compare_terms",
    "summarize_terms",
    "extract_clauses",
    "answer_question",
]
