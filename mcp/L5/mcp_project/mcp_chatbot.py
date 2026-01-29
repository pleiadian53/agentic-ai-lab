from dotenv import load_dotenv
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from typing import List
import asyncio
import nest_asyncio

nest_asyncio.apply()

load_dotenv()

class MCP_ChatBot:

    def __init__(self):
        # Initialize session and client objects
        self.session: ClientSession = None
        self.anthropic = Anthropic()
        self.available_tools: List[dict] = []

    async def process_query(self, query):
        """Process a user query with tool use support."""
        messages = [{'role': 'user', 'content': query}]

        # Send my query to Claude
        response = self.anthropic.messages.create(
            max_tokens=2024,
            model='claude-sonnet-4-20250514',
            tools=self.available_tools,
            messages=messages
        )

        # Process until we get a final text response
        while response.stop_reason == "tool_use":
            # Collect all tool uses from the response
            tool_results = []

            for content in response.content:
                if content.type == 'text' and content.text:
                    print(content.text)
                elif content.type == 'tool_use':
                    tool_name = content.name
                    tool_args = content.input
                    tool_id = content.id

                    print(f"Calling tool {tool_name} with args {tool_args}")
                    result = await self.session.call_tool(tool_name, arguments=tool_args)

                    # Convert result content to string if needed
                    result_content = result.content
                    if isinstance(result_content, list):
                        result_content = str(result_content)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": result_content
                    })

            # Add assistant message with all tool uses
            messages.append({'role': 'assistant', 'content': response.content})

            # Add user message with ALL tool results together
            messages.append({'role': 'user', 'content': tool_results})

            # Get next response
            response = self.anthropic.messages.create(
                max_tokens=2024,
                model='claude-sonnet-4-20250514',
                tools=self.available_tools,
                messages=messages
            )

        # Print final text response
        for content in response.content:
            if content.type == 'text':
                print(content.text)



    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                await self.process_query(query)
                print("\n")

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def connect_to_server_and_run(self):
        # Create server parameters for stdio connection
        server_params = StdioServerParameters(
            command="python",  # Executable (use "uv" with args=["run", "research_server.py"] if using uv)
            args=["research_server.py"],  # Command line arguments
            env=None,  # Optional environment variables
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                # Initialize the connection
                await session.initialize()

                # List available tools
                response = await session.list_tools()

                tools = response.tools
                print("\nConnected to server with tools:", [tool.name for tool in tools])

                self.available_tools = [{
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                } for tool in response.tools]

                await self.chat_loop()


async def main():
    chatbot = MCP_ChatBot()
    await chatbot.connect_to_server_and_run()


if __name__ == "__main__":
    asyncio.run(main())
