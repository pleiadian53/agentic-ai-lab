"""
AISuite Client Wrapper for Tool Orchestration

This module provides a high-level wrapper around the AISuite client
for managing tool-calling workflows. It simplifies common patterns
like automatic vs. manual tool execution and provides utilities for
handling multi-turn conversations.

Design Principles:
    - Encapsulate AISuite complexity
    - Support both automatic and manual tool execution modes
    - Provide clear abstractions for common workflows
    - Enable easy testing and debugging
"""

import json
from typing import Any, Callable, Optional
import aisuite as ai


class ToolClient:
    """
    Wrapper around AISuite client for tool-calling workflows.
    
    This class simplifies the process of creating LLM completions with
    tool support, handling both automatic execution (via max_turns) and
    manual execution patterns.
    
    Attributes:
        client: The underlying AISuite client instance
        default_model: Default model to use for completions
        
    Example:
        >>> from tool_use import ToolClient, get_current_time
        >>> 
        >>> tool_client = ToolClient(model="openai:gpt-4o")
        >>> response = tool_client.chat(
        ...     prompt="What time is it?",
        ...     tools=[get_current_time]
        ... )
        >>> print(response.choices[0].message.content)
    """
    
    def __init__(self, model: str = "openai:gpt-4o"):
        """
        Initialize the ToolClient.
        
        Args:
            model: Default model identifier (e.g., "openai:gpt-4o")
        """
        self.client = ai.Client()
        self.default_model = model
        
    def chat(
        self,
        prompt: str,
        tools: Optional[list[Callable]] = None,
        model: Optional[str] = None,
        max_turns: int = 5,
        messages: Optional[list[dict]] = None,
    ) -> Any:
        """
        Create a chat completion with automatic tool execution.
        
        This method handles the full tool-calling workflow automatically,
        executing tools locally and passing results back to the LLM until
        a final response is generated or max_turns is reached.
        
        Args:
            prompt: User's prompt/question
            tools: List of callable functions to expose as tools
            model: Model to use (defaults to self.default_model)
            max_turns: Maximum number of LLM turns to prevent infinite loops
            messages: Optional pre-existing message history. If None, creates
                new conversation with the prompt.
                
        Returns:
            AISuite response object with completion and intermediate messages
            
        Example:
            >>> response = tool_client.chat(
            ...     prompt="What's the weather?",
            ...     tools=[get_weather_from_ip],
            ...     max_turns=3
            ... )
        """
        # Build message list
        if messages is None:
            messages = [{"role": "user", "content": prompt}]
        elif prompt:
            messages.append({"role": "user", "content": prompt})
            
        # Use default model if not specified
        model = model or self.default_model
        
        # Create completion with automatic tool execution
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools or [],
            max_turns=max_turns
        )
        
        return response
    
    def chat_manual(
        self,
        prompt: str,
        tools: list[dict],
        tool_functions: dict[str, Callable],
        model: Optional[str] = None,
        messages: Optional[list[dict]] = None,
    ) -> Any:
        """
        Create a chat completion with manual tool execution.
        
        This method gives you full control over tool execution. You provide
        tool schemas and a mapping of tool names to functions. The method
        handles one round of tool calling - if the LLM requests a tool, it
        executes it and returns the final response.
        
        Args:
            prompt: User's prompt/question
            tools: List of tool schema dictionaries
            tool_functions: Mapping of tool names to callable functions
            model: Model to use (defaults to self.default_model)
            messages: Optional pre-existing message history
            
        Returns:
            AISuite response object (may contain tool_calls if LLM wants to use tools)
            
        Example:
            >>> from tool_use.tools import get_tool_schemas, get_current_time
            >>> 
            >>> schemas = get_tool_schemas()
            >>> functions = {"get_current_time": get_current_time}
            >>> 
            >>> response = tool_client.chat_manual(
            ...     prompt="What time is it?",
            ...     tools=schemas,
            ...     tool_functions=functions
            ... )
        """
        # Build message list
        if messages is None:
            messages = [{"role": "user", "content": prompt}]
        elif prompt:
            messages.append({"role": "user", "content": prompt})
            
        # Use default model if not specified
        model = model or self.default_model
        
        # Initial LLM call
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
        )
        
        # Check if LLM wants to use a tool
        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            tool_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Execute the tool locally
            if tool_name in tool_functions:
                tool_result = tool_functions[tool_name](**args)
            else:
                tool_result = f"Error: Tool '{tool_name}' not found"
            
            # Append results to message history
            messages.append(response.choices[0].message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_result)
            })
            
            # Get final response from LLM
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
            )
        
        return response
    
    def create_messages(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        history: Optional[list[dict]] = None
    ) -> list[dict]:
        """
        Helper to create a properly formatted message list.
        
        Args:
            prompt: User's current prompt
            system_message: Optional system message to set context
            history: Optional conversation history
            
        Returns:
            List of message dictionaries ready for AISuite
            
        Example:
            >>> messages = tool_client.create_messages(
            ...     prompt="What time is it?",
            ...     system_message="You are a helpful assistant."
            ... )
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
            
        if history:
            messages.extend(history)
            
        messages.append({"role": "user", "content": prompt})
        
        return messages


class ToolRegistry:
    """
    Registry for managing and organizing tool functions.
    
    This class helps organize tools into categories and provides
    utilities for selecting subsets of tools for specific tasks.
    
    Example:
        >>> registry = ToolRegistry()
        >>> registry.register("time", get_current_time, category="utility")
        >>> registry.register("weather", get_weather_from_ip, category="api")
        >>> 
        >>> # Get all tools in a category
        >>> api_tools = registry.get_by_category("api")
    """
    
    def __init__(self):
        """Initialize an empty tool registry."""
        self.tools: dict[str, Callable] = {}
        self.categories: dict[str, list[str]] = {}
        self.metadata: dict[str, dict] = {}
        
    def register(
        self,
        name: str,
        func: Callable,
        category: Optional[str] = None,
        **metadata
    ) -> None:
        """
        Register a tool function.
        
        Args:
            name: Unique identifier for the tool
            func: The callable function
            category: Optional category for organization
            **metadata: Additional metadata about the tool
        """
        self.tools[name] = func
        self.metadata[name] = metadata
        
        if category:
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(name)
            
    def get(self, name: str) -> Optional[Callable]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def get_by_category(self, category: str) -> list[Callable]:
        """Get all tools in a category."""
        tool_names = self.categories.get(category, [])
        return [self.tools[name] for name in tool_names]
    
    def get_all(self) -> list[Callable]:
        """Get all registered tools."""
        return list(self.tools.values())
    
    def list_categories(self) -> list[str]:
        """List all available categories."""
        return list(self.categories.keys())
