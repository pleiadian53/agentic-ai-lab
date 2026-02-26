# Visual Guide: Tool Calling Flow

## The Complete Picture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         YOUR CODE                                    │
│                                                                      │
│  ┌────────────────────┐  ┌────────────────────┐  ┌───────────────┐ │
│  │ Python Function    │  │ JSON Schema        │  │ Tool Mapping  │ │
│  │ (Implementation)   │  │ (Definition)       │  │ (Router)      │ │
│  ├────────────────────┤  ├────────────────────┤  ├───────────────┤ │
│  │ def arxiv_search(  │  │ {                  │  │ {             │ │
│  │   query: str       │  │   "name": "arxiv_  │  │   "arxiv_     │ │
│  │ ):                 │  │     search",       │  │     search":  │ │
│  │   # API call       │  │   "description":   │  │     arxiv_    │ │
│  │   # Parse results  │  │     "Searches...", │  │     search,   │ │
│  │   return data      │  │   "parameters": {} │  │   ...         │ │
│  │                    │  │ }                  │  │ }             │ │
│  └────────────────────┘  └────────────────────┘  └───────────────┘ │
│         ↑                        ↓                       ↑          │
│         │                        │                       │          │
│         │                        │                       │          │
└─────────┼────────────────────────┼───────────────────────┼──────────┘
          │                        │                       │
          │                        │                       │
          │                        ↓                       │
          │         ┌──────────────────────────┐          │
          │         │         LLM              │          │
          │         │                          │          │
          │         │  Reads schemas           │          │
          │         │  Decides which tool      │          │
          │         │  Generates tool call     │          │
          │         │                          │          │
          │         └──────────────────────────┘          │
          │                        │                       │
          │                        ↓                       │
          │         ┌──────────────────────────┐          │
          │         │  Tool Call Request       │          │
          │         │  {                       │          │
          │         │    "name": "arxiv_search"│          │
          │         │    "arguments": {        │          │
          │         │      "query": "quantum"  │          │
          │         │    }                     │          │
          │         │  }                       │          │
          │         └──────────────────────────┘          │
          │                        │                       │
          │                        ↓                       │
          │         ┌──────────────────────────┐          │
          │         │  Your Orchestration      │          │
          │         │                          │          │
          │         │  1. Parse tool call      │──────────┘
          │         │  2. Look up in mapping   
          │         │  3. Execute function     ──────────┐
          │         │  4. Return results       │         │
          │         │                          │         │
          │         └──────────────────────────┘         │
          │                        ↑                      │
          └────────────────────────┘                      │
                                                          │
                                                          ↓
                                             ┌────────────────────┐
                                             │ Function Execution │
                                             │                    │
                                             │ arxiv_search(      │
                                             │   query="quantum"  │
                                             │ )                  │
                                             │                    │
                                             │ Returns: [...]     │
                                             └────────────────────┘
```

## Step-by-Step Flow

### Step 1: Registration

```
YOU                                    LLM
│                                      │
│  Send schemas                        │
│  ─────────────────────────────────>  │
│  [arxiv_tool_def,                    │
│   tavily_tool_def,                   │
│   wikipedia_tool_def]                │
│                                      │
│                                      │  Stores available tools
│                                      │  in context
```

### Step 2: User Request

```
USER                                   LLM
│                                      │
│  "Research quantum computing"        │
│  ─────────────────────────────────>  │
│                                      │
│                                      │  Analyzes request
│                                      │  Checks available tools
│                                      │  Decides: need arxiv_search
```

### Step 3: Tool Call Generation

```
LLM                                    YOU
│                                      │
│  Tool call request                   │
│  ─────────────────────────────────>  │
│  {                                   │
│    "name": "arxiv_search_tool",      │
│    "arguments": {                    │
│      "query": "quantum computing",   │
│      "max_results": 5                │
│    }                                 │
│  }                                   │
│                                      │
│                                      │  Receives tool call
```

### Step 4: Execution

```
YOU (Orchestration)                    FUNCTION
│                                      │
│  1. Parse tool call                  │
│     name = "arxiv_search_tool"       │
│     args = {"query": "quantum..."}   │
│                                      │
│  2. Look up in mapping               │
│     func = tool_mapping[name]        │
│                                      │
│  3. Execute function                 │
│  ─────────────────────────────────>  │
│     func(**args)                     │
│                                      │
│                                      │  Makes API call
│                                      │  Parses response
│                                      │  Returns results
│  <─────────────────────────────────  │
│     results = [...]                  │
```

### Step 5: Return to LLM

```
YOU                                    LLM
│                                      │
│  Tool results                        │
│  ─────────────────────────────────>  │
│  [                                   │
│    {                                 │
│      "title": "Quantum Paper",       │
│      "url": "https://arxiv.org/...", │
│      ...                             │
│    }                                 │
│  ]                                   │
│                                      │
│                                      │  Processes results
│                                      │  Formulates response
│                                      │
│  <─────────────────────────────────  │
│  "Based on recent papers..."         │
```

## The Three Components

```
┌─────────────────────────────────────────────────────────────┐
│                    PYTHON FUNCTION                          │
│                                                             │
│  What:  Executable code                                    │
│  For:   Your application                                   │
│  When:  Execution time                                     │
│                                                             │
│  def arxiv_search_tool(query: str) -> list[dict]:          │
│      response = requests.get(f"arxiv.org/api?q={query}")   │
│      return parse_results(response)                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     JSON SCHEMA                             │
│                                                             │
│  What:  Metadata description                               │
│  For:   The LLM                                            │
│  When:  Planning/decision time                             │
│                                                             │
│  {                                                          │
│    "name": "arxiv_search_tool",                            │
│    "description": "Searches arXiv for research papers",    │
│    "parameters": {                                         │
│      "query": {"type": "string", "description": "..."}     │
│    }                                                        │
│  }                                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     TOOL MAPPING                            │
│                                                             │
│  What:  Name-to-function dictionary                        │
│  For:   Your orchestration code                            │
│  When:  Routing tool calls                                 │
│                                                             │
│  tool_mapping = {                                          │
│    "arxiv_search_tool": arxiv_search_tool,                 │
│    "tavily_search_tool": tavily_search_tool,               │
│  }                                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Information Flow

```
┌──────────────┐
│ User Request │
└──────┬───────┘
       │
       ↓
┌──────────────────────────────────────────┐
│ LLM reads JSON schemas                   │
│ - What tools are available?              │
│ - What do they do?                       │
│ - What parameters do they need?          │
└──────┬───────────────────────────────────┘
       │
       ↓
┌──────────────────────────────────────────┐
│ LLM decides and generates tool call      │
│ {                                        │
│   "name": "arxiv_search_tool",           │
│   "arguments": {"query": "quantum"}      │
│ }                                        │
└──────┬───────────────────────────────────┘
       │
       ↓
┌──────────────────────────────────────────┐
│ Your code receives tool call             │
│ - Extracts name and arguments            │
│ - Looks up function in mapping           │
└──────┬───────────────────────────────────┘
       │
       ↓
┌──────────────────────────────────────────┐
│ Python function executes                 │
│ - Makes API calls                        │
│ - Processes data                         │
│ - Returns structured results             │
└──────┬───────────────────────────────────┘
       │
       ↓
┌──────────────────────────────────────────┐
│ Results sent back to LLM                 │
│ - LLM reads results                      │
│ - Formulates final response              │
└──────┬───────────────────────────────────┘
       │
       ↓
┌──────────────┐
│ User Response│
└──────────────┘
```

## Why the LLM Can't See Your Code

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR PYTHON CODE                         │
│                                                             │
│  def arxiv_search_tool(query: str, max_results: int = 5):  │
│      """Searches arXiv for papers."""                      │
│      url = f"https://arxiv.org/api?q={query}"              │
│      response = requests.get(url)                          │
│      return parse_response(response)                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                           ↑
                           │
                           │  LLM CANNOT ACCESS THIS
                           │  - Can't read function signature
                           │  - Can't parse docstrings
                           │  - Can't inspect parameters
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                    WHAT LLM SEES                            │
│                                                             │
│  {                                                          │
│    "name": "arxiv_search_tool",                            │
│    "description": "Searches arXiv for research papers",    │
│    "parameters": {                                         │
│      "type": "object",                                     │
│      "properties": {                                       │
│        "query": {                                          │
│          "type": "string",                                 │
│          "description": "Search keywords"                  │
│        },                                                  │
│        "max_results": {                                    │
│          "type": "integer",                                │
│          "description": "Max results",                     │
│          "default": 5                                      │
│        }                                                   │
│      },                                                    │
│      "required": ["query"]                                 │
│    }                                                        │
│  }                                                          │
│                                                             │
│  THIS IS THE ONLY INFORMATION AVAILABLE TO THE LLM         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Common Mistake: Thinking LLM Can See Code

```
❌ WRONG ASSUMPTION:

"I have a well-documented function with type hints,
 so the LLM will know how to use it."

def search_papers(query: str, year: int = 2024) -> list[dict]:
    """
    Searches for academic papers.
    
    Args:
        query: Search keywords
        year: Publication year filter
    """
    # ... implementation ...


✅ REALITY:

The LLM sees NOTHING from the function above.
You MUST provide a JSON schema:

search_papers_def = {
    "type": "function",
    "function": {
        "name": "search_papers",
        "description": "Searches for academic papers",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords"
                },
                "year": {
                    "type": "integer",
                    "description": "Publication year filter",
                    "default": 2024
                }
            },
            "required": ["query"]
        }
    }
}
```

## Summary Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    TOOL CALLING SYSTEM                      │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐ │
│  │   Function   │      │    Schema    │      │  Mapping │ │
│  │ (executes)   │      │ (describes)  │      │ (routes) │ │
│  └──────┬───────┘      └──────┬───────┘      └────┬─────┘ │
│         │                     │                    │       │
│         │                     │                    │       │
└─────────┼─────────────────────┼────────────────────┼───────┘
          │                     │                    │
          │                     ↓                    │
          │              ┌─────────────┐             │
          │              │     LLM     │             │
          │              │  (decides)  │             │
          │              └──────┬──────┘             │
          │                     │                    │
          │                     ↓                    │
          │              ┌─────────────┐             │
          │              │  Tool Call  │             │
          │              └──────┬──────┘             │
          │                     │                    │
          │                     ↓                    │
          │              ┌─────────────┐             │
          │              │Orchestration│─────────────┘
          │              └──────┬──────┘
          │                     │
          └─────────────────────┘
                                │
                                ↓
                          ┌──────────┐
                          │  Result  │
                          └──────────┘
```

## Key Takeaway

**The LLM is blind to your code.**

It only knows what you explicitly tell it through the JSON schema.

That's why you need both:
- **Function**: Does the work
- **Schema**: Tells LLM about it
- **Mapping**: Connects them
