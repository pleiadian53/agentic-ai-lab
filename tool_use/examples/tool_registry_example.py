"""
Tool Registry Example

Demonstrates how to use the ToolRegistry for organizing and managing
tools in larger applications. This is useful when you have many tools
and want to organize them by category or functionality.
"""

from dotenv import load_dotenv
from tool_use import ToolClient
from tool_use.client import ToolRegistry
from tool_use.tools import (
    get_current_time,
    get_weather_from_ip,
    write_txt_file,
    generate_qr_code
)

# Load environment variables
load_dotenv()


def main():
    """Run tool registry examples."""
    
    # Initialize registry
    registry = ToolRegistry()
    
    print("=" * 60)
    print("EXAMPLE 1: Organizing Tools by Category")
    print("=" * 60)
    
    # Register tools with categories
    registry.register(
        "get_time",
        get_current_time,
        category="utility",
        description="Returns current time"
    )
    
    registry.register(
        "get_weather",
        get_weather_from_ip,
        category="api",
        description="Fetches weather from IP location"
    )
    
    registry.register(
        "write_file",
        write_txt_file,
        category="file_ops",
        description="Writes text files"
    )
    
    registry.register(
        "create_qr",
        generate_qr_code,
        category="file_ops",
        description="Generates QR codes"
    )
    
    print("\nRegistered Categories:")
    for category in registry.list_categories():
        tools = registry.get_by_category(category)
        print(f"  - {category}: {len(tools)} tool(s)")
    
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Using Category-Specific Tools")
    print("=" * 60)
    
    # Initialize client
    client = ToolClient(model="openai:gpt-4o")
    
    # Use only utility tools
    print("\nUsing only 'utility' category tools:")
    utility_tools = registry.get_by_category("utility")
    
    response = client.chat(
        prompt="What time is it?",
        tools=utility_tools,
        max_turns=5
    )
    
    print(f"Response: {response.choices[0].message.content}")
    
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Using All File Operation Tools")
    print("=" * 60)
    
    file_tools = registry.get_by_category("file_ops")
    
    response = client.chat(
        prompt="Create a file called test_note.txt with the message 'Hello from tool registry!'",
        tools=file_tools,
        max_turns=5
    )
    
    print(f"Response: {response.choices[0].message.content}")
    
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Dynamic Tool Selection")
    print("=" * 60)
    
    # Simulate selecting tools based on user intent
    user_intent = "weather"  # Could come from intent classification
    
    if "weather" in user_intent:
        selected_tools = registry.get_by_category("api")
        print(f"\nDetected weather intent, using API tools")
    elif "file" in user_intent:
        selected_tools = registry.get_by_category("file_ops")
        print(f"\nDetected file intent, using file operation tools")
    else:
        selected_tools = registry.get_all()
        print(f"\nNo specific intent, using all tools")
    
    response = client.chat(
        prompt="What's the weather like?",
        tools=selected_tools,
        max_turns=5
    )
    
    print(f"Response: {response.choices[0].message.content}")
    
    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("=" * 60)
    print("""
1. ToolRegistry helps organize tools in larger applications
2. Category-based organization enables selective tool exposure
3. Reduces token usage by only sending relevant tools to LLM
4. Enables dynamic tool selection based on user intent
5. Metadata can be used for additional tool information
    """)


if __name__ == "__main__":
    main()
