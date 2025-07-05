"""Agent module for the Terms & Conditions Analyzer."""
from typing import List, Dict, Any, Optional, Union, Type
from langchain.agents import (
    AgentExecutor,
    create_openai_tools_agent,
    create_structured_chat_agent,
    create_react_agent,
    create_json_chat_agent,
    create_tool_calling_agent,
)
from langchain.agents.agent import BaseSingleActionAgent, BaseMultiActionAgent
from langchain.agents.agent_types import AgentType
from langchain.agents.tools import Tool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.tools import BaseTool

from ..config import settings, logger
from ..chains import ChainType, get_llm_chain
from ..retrievers import default_retriever

class AgentType(str, Enum):
    """Types of agents available in the application."""
    OPENAI_TOOLS = "openai_tools"
    STRUCTURED_CHAT = "structured_chat"
    REACT = "react"
    JSON_CHAT = "json_chat"
    TOOL_CALLING = "tool_calling"


def get_agent(
    agent_type: Union[AgentType, str],
    tools: Optional[List[Union[Tool, BaseTool]]] = None,
    llm: Optional[BaseChatModel] = None,
    **kwargs
) -> Union[AgentExecutor, BaseSingleActionAgent, BaseMultiActionAgent]:
    """Get a pre-configured agent for the specified type.
    
    Args:
        agent_type: Type of agent to create.
        tools: List of tools the agent can use.
        llm: Language model to use. If None, a default will be used.
        **kwargs: Additional keyword arguments for the agent.
        
    Returns:
        A configured agent instance.
    """
    from langchain_openai import ChatOpenAI
    
    # Convert string to enum if needed
    if isinstance(agent_type, str):
        agent_type = AgentType(agent_type.lower())
    
    # Use provided LLM or create a default one
    if llm is None:
        llm = ChatOpenAI(
            model_name=settings.openai.model,
            temperature=settings.openai.temperature,
            max_tokens=settings.openai.max_tokens,
            **kwargs.pop("llm_kwargs", {})
        )
    
    # Get default tools if none provided
    if tools is None:
        tools = get_default_tools()
    
    # Get the appropriate agent based on the type
    if agent_type == AgentType.OPENAI_TOOLS:
        return _create_openai_tools_agent(llm, tools, **kwargs)
    elif agent_type == AgentType.STRUCTURED_CHAT:
        return _create_structured_chat_agent(llm, tools, **kwargs)
    elif agent_type == AgentType.REACT:
        return _create_react_agent(llm, tools, **kwargs)
    elif agent_type == AgentType.JSON_CHAT:
        return _create_json_chat_agent(llm, tools, **kwargs)
    elif agent_type == AgentType.TOOL_CALLING:
        return _create_tool_calling_agent(llm, tools, **kwargs)
    else:
        raise ValueError(f"Unsupported agent type: {agent_type}")


def get_default_tools() -> List[Tool]:
    """Get the default set of tools for the agent."""
    from ..tools import (
        search_web,
        analyze_terms,
        compare_terms,
        summarize_terms,
        extract_clauses,
        answer_question,
    )
    
    tools = [
        Tool(
            name="search_web",
            func=search_terms_conditions,
            description="Search the web for terms and conditions of a service or product.",
        ),
        Tool(
            name="analyze_terms",
            func=analyze_terms,
            description="Analyze terms and conditions and provide a detailed analysis.",
        ),
        Tool(
            name="compare_terms",
            func=compare_terms,
            description="Compare two sets of terms and conditions and highlight differences.",
        ),
        Tool(
            name="summarize_terms",
            func=summarize_terms,
            description="Generate a concise summary of terms and conditions.",
        ),
        Tool(
            name="extract_clauses",
            func=extract_clauses,
            description="Extract specific legal clauses from terms and conditions.",
        ),
        Tool(
            name="answer_question",
            func=answer_question,
            description="Answer a specific question about terms and conditions.",
        ),
    ]
    
    return tools


def _create_openai_tools_agent(
    llm: BaseChatModel,
    tools: List[Union[Tool, BaseTool]],
    **kwargs
) -> AgentExecutor:
    """Create an agent that uses OpenAI's function calling API."""
    from langchain.agents import AgentExecutor
    
    # Define the system message
    system_message = """You are a helpful assistant that helps users understand terms and conditions. 
    You have access to various tools to help analyze, compare, and explain legal documents.
    Always be thorough in your analysis and provide clear, concise explanations.
    """
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    # Create the agent executor
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=settings.langchain.verbose,
        max_iterations=10,
        handle_parsing_errors=True,
        **kwargs
    )


def _create_structured_chat_agent(
    llm: BaseChatModel,
    tools: List[Union[Tool, BaseTool]],
    **kwargs
) -> AgentExecutor:
    """Create a structured chat agent."""
    from langchain.agents import AgentExecutor
    
    # Define the system message
    system_message = """You are a helpful assistant that helps users understand terms and conditions. 
    You have access to various tools to help analyze, compare, and explain legal documents.
    Always be thorough in your analysis and provide clear, concise explanations.
    
    You have access to the following tools:
    {tools}
    
    Use the following format:
    
    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question
    
    Begin!
    
    Question: {input}
    {agent_scratchpad}
    """
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = create_structured_chat_agent(llm, tools, prompt)
    
    # Create the agent executor
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=settings.langchain.verbose,
        max_iterations=10,
        handle_parsing_errors=True,
        **kwargs
    )


def _create_react_agent(
    llm: BaseChatModel,
    tools: List[Union[Tool, BaseTool]],
    **kwargs
) -> AgentExecutor:
    """Create a ReAct agent."""
    from langchain.agents import AgentExecutor
    
    # Define the system message
    system_message = """You are a helpful assistant that helps users understand terms and conditions. 
    You have access to various tools to help analyze, compare, and explain legal documents.
    Always be thorough in your analysis and provide clear, concise explanations.
    
    You have access to the following tools:
    {tools}
    
    Use the following format:
    
    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question
    
    Begin!
    
    Question: {input}
    {agent_scratchpad}
    """
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create the agent executor
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=settings.langchain.verbose,
        max_iterations=10,
        handle_parsing_errors=True,
        **kwargs
    )


def _create_json_chat_agent(
    llm: BaseChatModel,
    tools: List[Union[Tool, BaseTool]],
    **kwargs
) -> AgentExecutor:
    """Create a JSON chat agent."""
    from langchain.agents import AgentExecutor
    
    # Define the system message
    system_message = """You are a helpful assistant that helps users understand terms and conditions. 
    You have access to various tools to help analyze, compare, and explain legal documents.
    Always be thorough in your analysis and provide clear, concise explanations.
    
    Respond with a JSON object containing your thoughts and actions.
    """
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = create_json_chat_agent(llm, tools, prompt)
    
    # Create the agent executor
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=settings.langchain.verbose,
        max_iterations=10,
        handle_parsing_errors=True,
        **kwargs
    )


def _create_tool_calling_agent(
    llm: BaseChatModel,
    tools: List[Union[Tool, BaseTool]],
    **kwargs
) -> AgentExecutor:
    """Create a tool calling agent."""
    from langchain.agents import AgentExecutor
    
    # Define the system message
    system_message = """You are a helpful assistant that helps users understand terms and conditions. 
    You have access to various tools to help analyze, compare, and explain legal documents.
    Always be thorough in your analysis and provide clear, concise explanations.
    """
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # Create the agent executor
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=settings.langchain.verbose,
        max_iterations=10,
        handle_parsing_errors=True,
        **kwargs
    )


# Create default agents for easy import
default_agent = get_agent(AgentType.OPENAI_TOOLS)
structured_chat_agent = get_agent(AgentType.STRUCTURED_CHAT)
react_agent = get_agent(AgentType.REACT)
json_chat_agent = get_agent(AgentType.JSON_CHAT)
tool_calling_agent = get_agent(AgentType.TOOL_CALLING)

# Export public API
__all__ = [
    "AgentType",
    "get_agent",
    "get_default_tools",
    "default_agent",
    "structured_chat_agent",
    "react_agent",
    "json_chat_agent",
    "tool_calling_agent",
]
