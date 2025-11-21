"""Market research multi-agent package.

This package implements a linear/sequential multi-agent system for
automated marketing campaign generation. The system coordinates four
specialized agents in a fixed pipeline:

1. Market Research Agent - Scans trends and matches products
2. Graphic Designer Agent - Generates campaign visuals
3. Copywriter Agent - Creates marketing copy with multimodal analysis
4. Packaging Agent - Assembles executive-ready reports

The pipeline follows a linear communication pattern where each agent's
output becomes the input for the next agent in sequence.
"""

from .agents import (
    market_research_agent,
    graphic_designer_agent,
    copywriter_agent,
    packaging_agent,
)
from .pipeline import run_campaign_pipeline
from .tools import (
    tavily_search_tool,
    product_catalog_tool,
    get_available_tools,
    handle_tool_call,
    create_tool_response_message,
)
from .llm_client import (
    call_llm_text,
    call_llm_json,
)

__all__ = [
    # Agents
    "market_research_agent",
    "graphic_designer_agent",
    "copywriter_agent",
    "packaging_agent",
    # Pipeline
    "run_campaign_pipeline",
    # Tools
    "tavily_search_tool",
    "product_catalog_tool",
    "get_available_tools",
    "handle_tool_call",
    "create_tool_response_message",
    # LLM Client
    "call_llm_text",
    "call_llm_json",
]
