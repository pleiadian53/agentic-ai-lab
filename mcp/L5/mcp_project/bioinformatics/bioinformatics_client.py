"""
Bioinformatics MCP Client

A Python client that connects to bioinformatics MCP servers (UniProt, AlphaFold)
and uses Claude to orchestrate protein analysis queries.

Usage:
    python bioinformatics_client.py                    # Connect to all servers
    python bioinformatics_client.py --server uniprot   # Connect to UniProt only
    python bioinformatics_client.py --server alphafold # Connect to AlphaFold only
    python bioinformatics_client.py --list-models      # List available Claude models
"""

from dotenv import load_dotenv
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import List, Dict, Optional
import asyncio
import nest_asyncio
import os

nest_asyncio.apply()
load_dotenv()


# =============================================================================
# Server Configuration
# =============================================================================

# Base path for bioinformatics servers
BIOINFORMATICS_DIR = os.path.dirname(os.path.abspath(__file__))

# Available MCP servers
MCP_SERVERS = {
    "uniprot": {
        "name": "UniProt MCP Server",
        "description": "Protein database queries, sequences, features, pathways",
        "command": "node",
        "args": [os.path.join(BIOINFORMATICS_DIR, "uniprot-server/build/index.js")],
    },
    "alphafold": {
        "name": "AlphaFold MCP Server", 
        "description": "Protein structure predictions, confidence scores",
        "command": "node",
        "args": [os.path.join(BIOINFORMATICS_DIR, "alphafold-server/build/index.js")],
    },
}


# =============================================================================
# Claude Models
# =============================================================================

CLAUDE_MODELS = {
    "claude-sonnet-4": {
        "id": "claude-sonnet-4-20250514",
        "description": "Claude Sonnet 4 - Best balance of speed and intelligence",
    },
    "claude-opus-4": {
        "id": "claude-opus-4-20250514",
        "description": "Claude Opus 4 - Most capable for complex analysis",
    },
    "claude-3.5-sonnet": {
        "id": "claude-3-5-sonnet-20241022",
        "description": "Claude 3.5 Sonnet - Previous generation, still excellent",
    },
    "claude-3.5-haiku": {
        "id": "claude-3-5-haiku-20241022",
        "description": "Claude 3.5 Haiku - Fast and cost-effective",
    },
}

DEFAULT_MODEL = "claude-sonnet-4"


def get_model_id(model_name: str) -> str:
    """Get full model ID from short name."""
    if model_name in CLAUDE_MODELS:
        return CLAUDE_MODELS[model_name]["id"]
    # If already a full ID, return as-is
    if "-202" in model_name:
        return model_name
    raise ValueError(f"Unknown model: {model_name}")


def list_available_models(verbose: bool = False) -> List[str]:
    """List available Claude models."""
    if verbose:
        print("\n" + "=" * 50)
        print("Available Claude Models")
        print("=" * 50)
        for name, info in CLAUDE_MODELS.items():
            print(f"\n  {name}")
            print(f"    {info['description']}")
        print("\n" + "=" * 50)
    return list(CLAUDE_MODELS.keys())


def list_available_servers(verbose: bool = False) -> List[str]:
    """List available MCP servers."""
    if verbose:
        print("\n" + "=" * 50)
        print("Available Bioinformatics MCP Servers")
        print("=" * 50)
        for name, info in MCP_SERVERS.items():
            print(f"\n  {name}")
            print(f"    {info['description']}")
            exists = os.path.exists(info['args'][0])
            status = "✓ Installed" if exists else "✗ Not installed"
            print(f"    Status: {status}")
        print("\n" + "=" * 50)
    return list(MCP_SERVERS.keys())


# =============================================================================
# Bioinformatics Client
# =============================================================================

class BioinformaticsClient:
    """
    MCP Client for bioinformatics servers.
    
    Connects to one or more MCP servers (UniProt, AlphaFold) and uses
    Claude to orchestrate protein analysis queries.
    """

    def __init__(self, server: str = "uniprot", model: Optional[str] = None):
        """
        Initialize the bioinformatics client.
        
        Args:
            server: Which server to connect to ("uniprot", "alphafold")
            model: Claude model to use (default: claude-sonnet-4)
        """
        if server not in MCP_SERVERS:
            raise ValueError(f"Unknown server: {server}. Available: {list(MCP_SERVERS.keys())}")
        
        self.server_name = server
        self.server_config = MCP_SERVERS[server]
        self.session: ClientSession = None
        self.anthropic = Anthropic()
        self.available_tools: List[dict] = []
        
        # Set model
        model_name = model or DEFAULT_MODEL
        self.model_id = get_model_id(model_name)
        self.model_name = model_name

    async def process_query(self, query: str) -> None:
        """Process a user query with tool use support."""
        messages = [{'role': 'user', 'content': query}]

        response = self.anthropic.messages.create(
            max_tokens=8192,
            model=self.model_id,
            tools=self.available_tools,
            messages=messages
        )

        # Agentic loop: process until final response
        while response.stop_reason == "tool_use":
            tool_results = []

            for content in response.content:
                if content.type == 'text' and content.text:
                    print(content.text)
                elif content.type == 'tool_use':
                    tool_name = content.name
                    tool_args = content.input
                    tool_id = content.id

                    print(f"🔧 Calling {tool_name} with {tool_args}")
                    result = await self.session.call_tool(tool_name, arguments=tool_args)

                    result_content = result.content
                    if isinstance(result_content, list):
                        result_content = str(result_content)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": result_content
                    })

            messages.append({'role': 'assistant', 'content': response.content})
            messages.append({'role': 'user', 'content': tool_results})

            response = self.anthropic.messages.create(
                max_tokens=8192,
                model=self.model_id,
                tools=self.available_tools,
                messages=messages
            )

        # Print final response
        for content in response.content:
            if content.type == 'text':
                print(content.text)

    async def chat_loop(self) -> None:
        """Run an interactive chat loop."""
        print(f"\n🧬 Bioinformatics Client Started!")
        print(f"   Server: {self.server_config['name']}")
        print(f"   Model: {self.model_name}")
        print(f"   Tools: {len(self.available_tools)} available")
        print("\nCommands: 'tools' (list tools), 'quit' (exit)")
        print("-" * 50)

        while True:
            try:
                query = input("\n🔬 Query: ").strip()

                if query.lower() == 'quit':
                    break
                elif query.lower() == 'tools':
                    print("\nAvailable tools:")
                    for tool in self.available_tools:
                        print(f"  • {tool['name']}: {tool.get('description', '')[:60]}...")
                    continue
                elif not query:
                    continue

                await self.process_query(query)

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")

    async def connect_and_run(self) -> None:
        """Connect to the MCP server and run the chat loop."""
        # Check if server is installed
        server_path = self.server_config['args'][0]
        if not os.path.exists(server_path):
            print(f"\n❌ Server not installed: {server_path}")
            print(f"\nTo install, run:")
            print(f"  cd {BIOINFORMATICS_DIR}")
            print(f"  git clone https://github.com/Augmented-Nature/{'Augmented-Nature-UniProt-MCP-Server' if self.server_name == 'uniprot' else 'AlphaFold-MCP-Server'}.git {self.server_name}-server")
            print(f"  cd {self.server_name}-server")
            print(f"  npm install && npm run build")
            return

        server_params = StdioServerParameters(
            command=self.server_config['command'],
            args=self.server_config['args'],
            env=None,
        )

        print(f"\n🔌 Connecting to {self.server_config['name']}...")

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                await session.initialize()

                # Discover tools
                response = await session.list_tools()
                self.available_tools = [{
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                } for tool in response.tools]

                print(f"✓ Connected! Found {len(self.available_tools)} tools.")

                await self.chat_loop()


# =============================================================================
# Main
# =============================================================================

async def main(server: str = "uniprot", model: Optional[str] = None):
    """Main entry point."""
    client = BioinformaticsClient(server=server, model=model)
    await client.connect_and_run()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Bioinformatics MCP Client - Query protein databases with Claude"
    )
    parser.add_argument(
        "--server", "-s",
        type=str,
        default="uniprot",
        choices=list(MCP_SERVERS.keys()),
        help="MCP server to connect to (default: uniprot)"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        help=f"Claude model to use (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--list-servers",
        action="store_true",
        help="List available MCP servers and exit"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available Claude models and exit"
    )

    args = parser.parse_args()

    if args.list_servers:
        list_available_servers(verbose=True)
    elif args.list_models:
        list_available_models(verbose=True)
    else:
        asyncio.run(main(server=args.server, model=args.model))
