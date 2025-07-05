#!/usr/bin/env python3
"""
Test script for MCP and LangChain integration in the Terms & Conditions Analyzer.
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / "src"))

# Load environment variables
load_dotenv()

async def test_mcp_integration():
    """Test the MCP and LangChain integration."""
    print("Testing MCP and LangChain integration...")
    
    # Import the necessary modules
    from terms_analyzer.vector_store import default_vector_store
    from terms_analyzer.utils.document_loader import default_document_loader
    from terms_analyzer.utils.text_splitter import default_splitter
    from terms_analyzer.retrievers import default_retriever
    from terms_analyzer.chains import (
        ChainType,
        default_extraction_chain,
        default_analysis_chain,
        default_summarization_chain
    )
    from terms_analyzer.agents import default_agent
    from terms_analyzer.tools import (
        search_terms_conditions,
        analyze_terms,
        summarize_terms
    )
    
    # Test 1: Vector Store Initialization
    print("\n--- Testing Vector Store ---")
    try:
        print("Initializing vector store...")
        print(f"Vector store type: {type(default_vector_store).__name__}")
        print(f"Collection count: {default_vector_store.vector_store._collection.count()}")
        print("✅ Vector store initialized successfully!")
    except Exception as e:
        print(f"❌ Vector store initialization failed: {e}")
        return False
    
    # Test 2: Document Loading
    print("\n--- Testing Document Loading ---")
    try:
        test_text = """
        Terms of Service
        
        1. Introduction
        These terms and conditions govern your use of our service.
        
        2. User Responsibilities
        You agree not to misuse the service or help anyone else do so.
        
        3. Privacy
        We respect your privacy and are committed to protecting your personal data.
        """
        
        print("Splitting test document...")
        documents = default_splitter.split_text(test_text)
        print(f"Created {len(documents)} document chunks")
        print("✅ Document splitting successful!")
    except Exception as e:
        print(f"❌ Document loading failed: {e}")
        return False
    
    # Test 3: Document Processing with LLM
    print("\n--- Testing Document Processing ---")
    try:
        print("Running extraction chain...")
        extraction_result = await default_extraction_chain.ainvoke({"text": test_text})
        print(f"Extracted {len(extraction_result.get('text', {}).get('clauses', []))} clauses")
        
        print("\nRunning analysis chain...")
        analysis_result = await default_analysis_chain.ainvoke({"text": test_text})
        print(f"Analysis complete. Overall severity: {analysis_result.get('text', {}).get('overall_severity', 'N/A')}")
        
        print("\nRunning summarization chain...")
        summary_result = await default_summarization_chain.ainvoke({"text": test_text})
        print(f"Summary: {summary_result.get('text', {}).get('summary', 'No summary')[:200]}...")
        
        print("✅ Document processing successful!")
    except Exception as e:
        print(f"❌ Document processing failed: {e}")
        return False
    
    # Test 4: Tool Usage
    print("\n--- Testing Tools ---")
    try:
        print("Testing search_terms_conditions tool...")
        search_result = await search_terms_conditions("GitHub terms of service", max_results=1)
        print(f"Search result: {search_result[:200]}...")
        
        print("\nTesting analyze_terms tool...")
        analysis = await analyze_terms(test_text)
        print(f"Analysis result: {analysis[:200]}...")
        
        print("\nTesting summarize_terms tool...")
        summary = await summarize_terms(test_text)
        print(f"Summary: {summary[:200]}...")
        
        print("✅ Tools test successful!")
    except Exception as e:
        print(f"❌ Tools test failed: {e}")
        return False
    
    # Test 5: Agent Usage
    print("\n--- Testing Agent ---")
    try:
        print("Initializing agent...")
        
        # Test a simple query
        print("\nAsking agent a question...")
        agent_response = await default_agent.ainvoke({
            "input": "What are the key points in these terms? " + test_text
        })
        
        print(f"Agent response: {agent_response['output'][:300]}...")
        print("✅ Agent test successful!")
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False
    
    print("\n🎉 All tests completed successfully!")
    return True

if __name__ == "__main__":
    # Run the async test function
    asyncio.run(test_mcp_integration())
