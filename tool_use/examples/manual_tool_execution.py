"""
Manual Tool Execution Example

Demonstrates manual control over tool execution using tool schemas.
This gives you full control over the tool calling workflow, useful
for debugging, logging, or custom execution logic.
"""

import json
from dotenv import load_dotenv
from tool_use import ToolClient
from tool_use.tools import get_current_time, get_tool_schemas

# Load environment variables
load_dotenv()


def main():
    """Run manual tool execution examples."""
    
    # Initialize the client
    client = ToolClient(model="openai:gpt-4o")
    
    print("=" * 60)
    print("EXAMPLE: Manual Tool Execution with Full Control")
    print("=" * 60)
    
    # Get tool schemas for manual definition
    schemas = get_tool_schemas()
    
    # Create mapping of tool names to functions
    tool_functions = {
        "get_current_time": get_current_time,
    }
    
    # Use manual execution mode
    response = client.chat_manual(
        prompt="What time is it?",
        tools=schemas,
        tool_functions=tool_functions
    )
    
    print(f"\nFinal Response: {response.choices[0].message.content}\n")
    
    print("=" * 60)
    print("EXAMPLE: Inspecting the Full Response Object")
    print("=" * 60)
    
    # Create a new message list for manual handling
    messages = [{"role": "user", "content": "What time is it?"}]
    
    # First LLM call
    response1 = client.client.chat.completions.create(
        model="openai:gpt-4o",
        messages=messages,
        tools=[schema for schema in schemas if schema["function"]["name"] == "get_current_time"],
    )
    
    print("\nStep 1: Initial LLM Response")
    print(json.dumps(response1.model_dump(), indent=2, default=str))
    
    # Check if tool was called
    if response1.choices[0].message.tool_calls:
        tool_call = response1.choices[0].message.tool_calls[0]
        print(f"\n\nStep 2: LLM Requested Tool: {tool_call.function.name}")
        
        # Execute tool locally
        tool_result = get_current_time()
        print(f"Step 3: Tool Result: {tool_result}")
        
        # Append to messages
        messages.append(response1.choices[0].message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(tool_result)
        })
        
        # Get final response
        response2 = client.client.chat.completions.create(
            model="openai:gpt-4o",
            messages=messages,
            tools=[schema for schema in schemas if schema["function"]["name"] == "get_current_time"],
        )
        
        print(f"\nStep 4: Final LLM Response: {response2.choices[0].message.content}")
    
    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("=" * 60)
    print("""
1. Manual mode gives you full control over tool execution
2. You can inspect and log each step of the workflow
3. Useful for debugging, custom execution logic, or integration with other systems
4. The chat_manual() method simplifies this pattern while maintaining control
    """)


if __name__ == "__main__":
    main()
