"""Tool implementations for market research agents.

This module provides external tools that agents can call to gather
information and perform actions:
- tavily_search_tool: Web search for fashion trends
- product_catalog_tool: Access internal product inventory
"""

import json
import os
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv
from tavily import TavilyClient

from .inventory_utils import create_inventory_dataframe

# Session setup (optional)
session = requests.Session()
session.headers.update({
    "User-Agent": "LF-ADP-Agent/1.0 (mailto:your.email@example.com)"
})

load_dotenv()


# Tool Implementations

def tavily_search_tool(query: str, max_results: int = 5, include_images: bool = False) -> list[dict[str, str]]:
    """Perform web search using Tavily API.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        include_images: Whether to include image URLs in results
        
    Returns:
        List of search results with title, content, and URL
    """
    params = {}
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not found in environment variables.")
    params['api_key'] = api_key

    api_base_url = os.getenv("DLAI_TAVILY_BASE_URL")
    if api_base_url:
        params['api_base_url'] = api_base_url

    client = TavilyClient(api_key=api_key, api_base_url=api_base_url)

    try:
        response = client.search(
            query=query,
            max_results=max_results,
            include_images=include_images
        )

        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "content": r.get("content", ""),
                "url": r.get("url", "")
            })

        if include_images:
            for img_url in response.get("images", []):
                results.append({"image_url": img_url})

        return results

    except Exception as e:
        return [{"error": str(e)}]


def product_catalog_tool(max_items: int = 10) -> list[dict[str, Any]]:
    """Get products from internal inventory.
    
    Args:
        max_items: Maximum number of products to return
        
    Returns:
        List of product dictionaries with name, ID, description, stock, price
    """
    inventory_df = create_inventory_dataframe()
    return inventory_df.head(max_items).to_dict(orient="records")


# Tool Metadata for LLM

def get_available_tools() -> list[dict]:
    """Get tool definitions in OpenAI function calling format.
    
    Returns:
        List of tool definitions for LLM function calling
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "tavily_search_tool",
                "description": "Perform web search for sunglasses trends using Tavily.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "max_results": {"type": "integer", "default": 5},
                        "include_images": {"type": "boolean", "default": False}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "product_catalog_tool",
                "description": "Get sunglasses products from internal inventory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_items": {"type": "integer", "default": 10}
                    }
                }
            }
        }
    ]


# Tool Call Dispatcher

def handle_tool_call(tool_call) -> Any:
    """Execute a tool call and return the result.
    
    Args:
        tool_call: Tool call object from LLM response
        
    Returns:
        Result from the tool execution
    """
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    tools_map = {
        "tavily_search_tool": tavily_search_tool,
        "product_catalog_tool": product_catalog_tool,
    }

    return tools_map[function_name](**arguments)


def create_tool_response_message(tool_call, tool_result) -> dict:
    """Create a tool response message for the conversation.
    
    Args:
        tool_call: Original tool call object
        tool_result: Result from tool execution
        
    Returns:
        Message dict in OpenAI format
    """
    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "name": tool_call.function.name,
        "content": json.dumps(tool_result)
    }
