"""
Tool Use Package - Agentic AI Tool Calling Patterns

This package provides reusable components for implementing tool-calling
design patterns with LLMs using AISuite.

Modules:
    - tools: Collection of tool functions for LLM use
    - client: AISuite client wrapper for tool orchestration
    - display_functions: Utilities for visualizing tool call sequences
    - utils: Helper functions for API interactions and display
"""

from tool_use.tools import (
    get_current_time,
    get_weather_from_ip,
    write_txt_file,
    generate_qr_code,
)

from tool_use.client import ToolClient

__version__ = "0.1.0"

__all__ = [
    "get_current_time",
    "get_weather_from_ip", 
    "write_txt_file",
    "generate_qr_code",
    "ToolClient",
]
