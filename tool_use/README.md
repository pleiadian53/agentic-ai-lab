# Tool Use Package

A reusable package for implementing tool-calling design patterns with LLMs using AISuite. Extracted from the M3_UGL_1 notebook to provide modular, testable, and production-ready components.

## 📦 Package Structure

```text
tool_use/
├── __init__.py              # Package initialization and exports
├── tools.py                 # Tool function definitions
├── client.py                # AISuite client wrapper
├── display_functions.py     # Visualization utilities
├── utils.py                 # Helper functions and API utilities
├── examples/                # Example scripts
│   ├── basic_tool_usage.py
│   ├── multi_tool_workflow.py
│   ├── manual_tool_execution.py
│   └── tool_registry_example.py
└── README.md               # This file
```

## 🎯 Design Philosophy

This package follows key design principles from the AGENTS.md guide:

### 1. **Modularity**
- Clear separation of concerns: tools, client logic, and display utilities
- Each module has a single, well-defined responsibility
- Easy to extend with new tools without modifying existing code

### 2. **Composability**
- Tools can be mixed and matched for different workflows
- Client wrapper supports both automatic and manual execution modes
- Registry pattern for organizing tools in larger applications

### 3. **Testability**
- Pure functions where possible (tools have minimal side effects)
- Clear interfaces for mocking and testing
- Explicit data flow makes debugging straightforward

### 4. **Reflective Practice**
- Comprehensive docstrings explain the "why" behind design decisions
- Examples demonstrate both simple and complex usage patterns
- Code comments highlight trade-offs and alternatives

## 🚀 Quick Start

### Installation

Ensure you have the required dependencies:

```bash
pip install aisuite requests qrcode pillow python-dotenv
```

### Basic Usage

```python
from dotenv import load_dotenv
from tool_use import ToolClient, get_current_time, get_weather_from_ip

load_dotenv()

# Initialize client
client = ToolClient(model="openai:gpt-4o")

# Use tools automatically
response = client.chat(
    prompt="What time is it?",
    tools=[get_current_time],
    max_turns=5
)

print(response.choices[0].message.content)
```

## 📚 Core Components

### Tools Module (`tools.py`)

Provides four core tool functions:

- **`get_current_time()`** - Returns current time in HH:MM:SS format
- **`get_weather_from_ip()`** - Fetches weather based on IP geolocation
- **`write_txt_file(file_path, content)`** - Writes text files
- **`generate_qr_code(data, filename, image_path=None)`** - Creates QR codes

Each tool includes:
- Comprehensive docstrings for LLM understanding
- Type hints for parameter validation
- Error handling with informative messages
- Usage examples in docstrings

**Design Decision**: Tools are stateless functions rather than classes. This makes them easier to test, compose, and pass to the LLM. The trade-off is that configuration must be passed as parameters rather than stored in instance variables.

### Client Module (`client.py`)

Provides two main classes:

#### `ToolClient`
Wrapper around AISuite client with simplified interfaces:

```python
# Automatic execution (recommended for most cases)
response = client.chat(
    prompt="What's the weather?",
    tools=[get_weather_from_ip],
    max_turns=5
)

# Manual execution (for debugging or custom logic)
response = client.chat_manual(
    prompt="What time is it?",
    tools=tool_schemas,
    tool_functions={"get_current_time": get_current_time}
)
```

**Design Decision**: Two execution modes provide flexibility. Automatic mode (`chat`) is simpler and handles the full workflow. Manual mode (`chat_manual`) gives control for debugging, logging, or custom execution logic.

#### `ToolRegistry`
Organizes tools by category for larger applications:

```python
registry = ToolRegistry()
registry.register("time", get_current_time, category="utility")
registry.register("weather", get_weather_from_ip, category="api")

# Get tools by category
api_tools = registry.get_by_category("api")
```

**Design Decision**: Registry pattern enables dynamic tool selection based on user intent, reducing token usage by only sending relevant tools to the LLM.

### Display Functions (`display_functions.py`)

Utilities for visualizing tool call sequences in Jupyter notebooks:

- **`pretty_print_chat_completion(response)`** - Displays tool execution flow
- **`pretty_print_chat_completion_html(response)`** - Returns HTML string

These are particularly useful for understanding multi-step tool orchestration.

## 📖 Examples

The `examples/` directory contains four comprehensive examples:

### 1. Basic Tool Usage
Demonstrates single-tool workflows and automatic tool selection.

```bash
python examples/basic_tool_usage.py
```

### 2. Multi-Tool Workflow
Shows complex workflows with sequential and parallel tool usage.

```bash
python examples/multi_tool_workflow.py
```

### 3. Manual Tool Execution
Demonstrates manual control over tool execution for debugging.

```bash
python examples/manual_tool_execution.py
```

### 4. Tool Registry
Shows how to organize and manage tools in larger applications.

```bash
python examples/tool_registry_example.py
```

## 🔧 Advanced Usage

### Creating Custom Tools

Tools should follow this pattern:

```python
def my_custom_tool(param1: str, param2: int = 10) -> str:
    """
    Brief description for the LLM.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 (default: 10)
        
    Returns:
        Description of return value
        
    Example:
        >>> my_custom_tool("test", 5)
        "result"
    """
    try:
        # Implementation
        result = f"Processed {param1} with {param2}"
        return result
    except Exception as e:
        return f"Error: {str(e)}"
```

**Key Points**:
- Comprehensive docstring (LLM uses this to understand the tool)
- Type hints for parameters and return value
- Error handling with informative messages
- Example usage in docstring

### Manual Tool Schema Definition

For fine-grained control, define tool schemas manually:

```python
from tool_use.tools import get_tool_schemas

schemas = get_tool_schemas()
# Returns list of properly formatted tool schemas

# Or create custom schema
custom_schema = {
    "type": "function",
    "function": {
        "name": "my_tool",
        "description": "What the tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Parameter description"
                }
            },
            "required": ["param1"]
        }
    }
}
```

### Multi-Turn Conversations

Build conversational workflows with tool support:

```python
client = ToolClient()

# Create message history
messages = client.create_messages(
    prompt="What's the weather?",
    system_message="You are a helpful weather assistant."
)

# First turn
response1 = client.chat(
    prompt="",  # Empty since we're using messages
    messages=messages,
    tools=[get_weather_from_ip],
    max_turns=5
)

# Continue conversation
messages.append({
    "role": "assistant",
    "content": response1.choices[0].message.content
})
messages.append({
    "role": "user",
    "content": "Can you write that to a file?"
})

response2 = client.chat(
    prompt="",
    messages=messages,
    tools=[write_txt_file],
    max_turns=5
)
```

## 🧪 Testing

The modular design makes testing straightforward:

```python
# Test individual tools
def test_get_current_time():
    result = get_current_time()
    assert isinstance(result, str)
    assert len(result) == 8  # HH:MM:SS format

# Test client with mock tools
def test_client_with_mock():
    def mock_tool():
        """Mock tool for testing."""
        return "mock result"
    
    client = ToolClient()
    response = client.chat(
        prompt="Test",
        tools=[mock_tool],
        max_turns=1
    )
    assert response is not None
```

## 🔍 Missing Components Analysis

Based on the notebook analysis, all components are now properly modularized:

✅ **Tool Functions** - Extracted to `tools.py`  
✅ **Client Wrapper** - Created in `client.py`  
✅ **Display Utilities** - Already existed in `display_functions.py`  
✅ **Helper Functions** - Already existed in `utils.py`  
✅ **Package Structure** - Created `__init__.py` with proper exports  
✅ **Examples** - Created comprehensive example scripts  
✅ **Documentation** - This README

**No missing components identified.** The package is complete and ready for use.

## 🎓 Learning Path

For those new to tool-calling patterns:

1. **Start with** `examples/basic_tool_usage.py` - Understand single-tool workflows
2. **Move to** `examples/multi_tool_workflow.py` - Learn multi-step orchestration
3. **Explore** `examples/manual_tool_execution.py` - Understand the internals
4. **Apply** `examples/tool_registry_example.py` - Organize tools at scale

## 🔄 Migration from Notebook

To migrate existing notebook code:

**Before (Notebook)**:
```python
import aisuite as ai
from datetime import datetime

def get_current_time():
    """Returns the current time as a string."""
    return datetime.now().strftime("%H:%M:%S")

client = ai.Client()
response = client.chat.completions.create(
    model="openai:gpt-4o",
    messages=[{"role": "user", "content": "What time is it?"}],
    tools=[get_current_time],
    max_turns=5
)
```

**After (Package)**:
```python
from tool_use import ToolClient, get_current_time

client = ToolClient(model="openai:gpt-4o")
response = client.chat(
    prompt="What time is it?",
    tools=[get_current_time],
    max_turns=5
)
```

## 🚦 Best Practices

1. **Tool Design**
   - Keep tools focused on a single responsibility
   - Include comprehensive docstrings (LLM reads these!)
   - Handle errors gracefully with informative messages
   - Use type hints for clarity

2. **Client Usage**
   - Use automatic mode (`chat`) for most workflows
   - Use manual mode (`chat_manual`) for debugging or custom logic
   - Set appropriate `max_turns` to prevent infinite loops
   - Consider token usage when selecting tools

3. **Organization**
   - Use `ToolRegistry` for applications with many tools
   - Group related tools by category
   - Only expose relevant tools to reduce token usage

4. **Testing**
   - Test tools independently before LLM integration
   - Use mock tools for client testing
   - Verify error handling paths

## 🤝 Contributing

When adding new tools:

1. Follow the tool function pattern (see "Creating Custom Tools")
2. Add comprehensive docstrings
3. Include error handling
4. Add type hints
5. Create an example in `examples/`
6. Update this README

## 📝 License

Part of the agentic-ai-lab repository. See repository LICENSE for details.

## 🙏 Acknowledgments

This package was refactored from the M3_UGL_1 notebook, which demonstrates tool-calling patterns with AISuite. The refactoring follows principles from the AGENTS.md guide, emphasizing modularity, composability, and reflective practice.
