"""
Basic Tool Usage Example

Demonstrates the fundamental pattern of using tools with the ToolClient.
This example shows automatic tool execution where AISuite handles the
tool calling workflow.
"""

from dotenv import load_dotenv
from tool_use import ToolClient, get_current_time, get_weather_from_ip

# Load environment variables
load_dotenv()


def main():
    """Run basic tool usage examples."""
    
    # Initialize the client
    client = ToolClient(model="openai:gpt-4o")
    
    print("=" * 60)
    print("EXAMPLE 1: Single Tool - Get Current Time")
    print("=" * 60)
    
    response = client.chat(
        prompt="What time is it?",
        tools=[get_current_time],
        max_turns=5
    )
    
    print(f"\nResponse: {response.choices[0].message.content}\n")
    
    print("=" * 60)
    print("EXAMPLE 2: Single Tool - Get Weather")
    print("=" * 60)
    
    response = client.chat(
        prompt="Can you get the weather for my location?",
        tools=[get_weather_from_ip],
        max_turns=5
    )
    
    print(f"\nResponse: {response.choices[0].message.content}\n")
    
    print("=" * 60)
    print("EXAMPLE 3: Multiple Tools - LLM Chooses Appropriate Tool")
    print("=" * 60)
    
    response = client.chat(
        prompt="What's the current temperature where I am?",
        tools=[get_current_time, get_weather_from_ip],
        max_turns=5
    )
    
    print(f"\nResponse: {response.choices[0].message.content}\n")
    print("Note: The LLM chose the weather tool, not the time tool!")


if __name__ == "__main__":
    main()
