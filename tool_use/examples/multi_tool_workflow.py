"""
Multi-Tool Workflow Example

Demonstrates complex workflows where the LLM uses multiple tools
in sequence to accomplish a task. This shows the power of tool
orchestration for multi-step operations.
"""

from dotenv import load_dotenv
from tool_use import (
    ToolClient,
    get_current_time,
    get_weather_from_ip,
    write_txt_file,
    generate_qr_code
)

# Load environment variables
load_dotenv()


def main():
    """Run multi-tool workflow examples."""
    
    # Initialize the client
    client = ToolClient(model="openai:gpt-4o")
    
    print("=" * 60)
    print("EXAMPLE 1: Sequential Tool Usage")
    print("=" * 60)
    print("Task: Create a reminder note with current weather\n")
    
    response = client.chat(
        prompt="Can you write me a txt note called weather_reminder.txt with the current weather?",
        tools=[get_weather_from_ip, write_txt_file],
        max_turns=10
    )
    
    print(f"Response: {response.choices[0].message.content}\n")
    
    # Verify the file was created
    try:
        with open('weather_reminder.txt', 'r') as f:
            print(f"File contents:\n{f.read()}\n")
    except FileNotFoundError:
        print("Note: File not created (may need to run in correct directory)\n")
    
    print("=" * 60)
    print("EXAMPLE 2: Parallel Tool Usage")
    print("=" * 60)
    print("Task: Create QR code AND write a note\n")
    
    response = client.chat(
        prompt=(
            "Can you help me create a QR code that goes to www.deeplearning.ai "
            "and also write me a txt note called session_log.txt with the current time?"
        ),
        tools=[
            get_current_time,
            get_weather_from_ip,
            write_txt_file,
            generate_qr_code
        ],
        max_turns=10
    )
    
    print(f"Response: {response.choices[0].message.content}\n")
    
    print("=" * 60)
    print("EXAMPLE 3: Complex Multi-Step Workflow")
    print("=" * 60)
    print("Task: Weather note + branded QR code\n")
    
    response = client.chat(
        prompt=(
            "Please do two things: "
            "1) Write a file called current_weather.txt with today's weather forecast "
            "2) Create a QR code called weather_qr that goes to https://weather.com"
        ),
        tools=[
            get_current_time,
            get_weather_from_ip,
            write_txt_file,
            generate_qr_code
        ],
        max_turns=10
    )
    
    print(f"Response: {response.choices[0].message.content}\n")
    
    # Show intermediate steps if available
    if hasattr(response.choices[0], 'intermediate_messages'):
        print("\nTool Execution Sequence:")
        for i, msg in enumerate(response.choices[0].intermediate_messages, 1):
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for call in msg.tool_calls:
                    print(f"  {i}. Called: {call.function.name}")


if __name__ == "__main__":
    main()
