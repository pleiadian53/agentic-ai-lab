from dotenv import load_dotenv
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from typing import List, Optional
import asyncio
import nest_asyncio

nest_asyncio.apply()

load_dotenv()


# =============================================================================
# Available Claude Models (as of December 2025)
# =============================================================================
# Reference: https://docs.anthropic.com/en/docs/about-claude/models

CLAUDE_MODELS = {
    # Claude 4 family (Latest)
    "claude-sonnet-4": {
        "id": "claude-sonnet-4-20250514",
        "description": "Claude Sonnet 4 - Best balance of speed and intelligence",
        "context_window": 200000,
        "max_output": 64000,
    },
    "claude-opus-4": {
        "id": "claude-opus-4-20250514", 
        "description": "Claude Opus 4 - Most capable model for complex tasks",
        "context_window": 200000,
        "max_output": 32000,
    },
    # Claude 3.5 family
    "claude-3.5-sonnet": {
        "id": "claude-3-5-sonnet-20241022",
        "description": "Claude 3.5 Sonnet - Previous generation, still excellent",
        "context_window": 200000,
        "max_output": 8192,
    },
    "claude-3.5-haiku": {
        "id": "claude-3-5-haiku-20241022",
        "description": "Claude 3.5 Haiku - Fast and cost-effective",
        "context_window": 200000,
        "max_output": 8192,
    },
    # Claude 3 family (Legacy)
    "claude-3-opus": {
        "id": "claude-3-opus-20240229",
        "description": "Claude 3 Opus - Legacy, powerful but slower",
        "context_window": 200000,
        "max_output": 4096,
    },
    "claude-3-sonnet": {
        "id": "claude-3-sonnet-20240229",
        "description": "Claude 3 Sonnet - Legacy balanced model",
        "context_window": 200000,
        "max_output": 4096,
    },
    "claude-3-haiku": {
        "id": "claude-3-haiku-20240307",
        "description": "Claude 3 Haiku - Legacy fast model",
        "context_window": 200000,
        "max_output": 4096,
    },
}

# Default model
DEFAULT_MODEL = "claude-sonnet-4"


def list_available_models(verbose: bool = False) -> List[str]:
    """
    List all available Claude models.
    
    Args:
        verbose: If True, print detailed information about each model
        
    Returns:
        List of model short names (keys)
    """
    if verbose:
        print("\n" + "=" * 60)
        print("Available Claude Models")
        print("=" * 60)
        for name, info in CLAUDE_MODELS.items():
            print(f"\n  {name}")
            print(f"    ID: {info['id']}")
            print(f"    Description: {info['description']}")
            print(f"    Context: {info['context_window']:,} tokens")
            print(f"    Max Output: {info['max_output']:,} tokens")
        print("\n" + "=" * 60)
        print(f"Default: {DEFAULT_MODEL}")
        print("=" * 60 + "\n")
    
    return list(CLAUDE_MODELS.keys())


def get_model_id(model_name: str) -> str:
    """
    Get the full model ID from a short name.
    
    Args:
        model_name: Short name (e.g., "claude-sonnet-4") or full ID
        
    Returns:
        Full model ID for API calls
        
    Raises:
        ValueError: If model name is not recognized
    """
    # If it's already a full ID, return it
    if model_name.startswith("claude-") and "-202" in model_name:
        return model_name
    
    # Look up in our registry
    if model_name in CLAUDE_MODELS:
        return CLAUDE_MODELS[model_name]["id"]
    
    # Try case-insensitive match
    for name, info in CLAUDE_MODELS.items():
        if name.lower() == model_name.lower():
            return info["id"]
    
    raise ValueError(
        f"Unknown model: {model_name}. "
        f"Available models: {', '.join(CLAUDE_MODELS.keys())}"
    )


class ResearchClient:
    """
    MCP Client for the research server with configurable Claude model.
    
    Enhanced version of MCP_ChatBot with:
    - Configurable model selection
    - Model listing utilities
    - Better error handling
    """

    def __init__(self, model: Optional[str] = None):
        """
        Initialize the research client.
        
        Args:
            model: Model name (short or full ID). Defaults to claude-sonnet-4.
        """
        self.session: ClientSession = None
        self.anthropic = Anthropic()
        self.available_tools: List[dict] = []
        
        # Set model with validation
        model_name = model or DEFAULT_MODEL
        self.model_id = get_model_id(model_name)
        self.model_name = model_name

    async def process_query(self, query):
        """Process a user query with tool use support."""
        messages = [{'role': 'user', 'content': query}]

        # Send query to Claude using configured model
        response = self.anthropic.messages.create(
            max_tokens=8192,
            model=self.model_id,
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

            # Get next response using configured model
            response = self.anthropic.messages.create(
                max_tokens=8192,
                model=self.model_id,
                tools=self.available_tools,
                messages=messages
            )

        # Print final text response
        for content in response.content:
            if content.type == 'text':
                print(content.text)



    async def chat_loop(self):
        """Run an interactive chat loop."""
        print("\nResearch Client Started!")
        print(f"Using model: {self.model_name} ({self.model_id})")
        print("Type your queries, 'models' to list available models, or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break
                elif query.lower() == 'models':
                    list_available_models(verbose=True)
                    continue

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


async def main(model: Optional[str] = None):
    """
    Main entry point for the research client.
    
    Args:
        model: Optional model name to use (defaults to claude-sonnet-4)
    """
    client = ResearchClient(model=model)
    await client.connect_to_server_and_run()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Research Client")
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        help=f"Claude model to use (default: {DEFAULT_MODEL}). Use --list-models to see options."
    )
    parser.add_argument(
        "--list-models", "-l",
        action="store_true",
        help="List available models and exit"
    )
    
    args = parser.parse_args()
    
    if args.list_models:
        list_available_models(verbose=True)
    else:
        asyncio.run(main(model=args.model))
