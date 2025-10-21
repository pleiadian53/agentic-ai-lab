# Agent & LLM Tools

Detailed documentation for agent and LLM-related libraries used in this project.

## Overview

These libraries enable the core agentic AI functionality, providing interfaces to multiple LLM providers and tools for building intelligent agents.

---

## LLM Provider Libraries

### aisuite (v0.1.11)

**Unified LLM Interface**

```python
from aisuite import Client

client = Client()

# Works with any provider
response = client.chat.completions.create(
    model="openai:gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Easy to switch providers
response = client.chat.completions.create(
    model="anthropic:claude-3-opus",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**Key Features:**
- Unified API across providers (OpenAI, Anthropic, Mistral, Google)
- Easy provider switching
- Consistent error handling
- Simplified configuration

**Use Cases in This Project:**
- Agent orchestration with multiple models
- A/B testing different LLMs
- Fallback to alternative providers
- Cost optimization by model selection

**Configuration:**
```python
# Set API keys in .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
MISTRAL_API_KEY=...
```

---

### openai

**Official OpenAI Python Client**

```python
from openai import OpenAI

client = OpenAI()

# Chat completions
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing"}
    ]
)

# Function calling for agents
tools = [{
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Search the web for information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            }
        }
    }
}]

response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=tools
)
```

**Key Features:**
- GPT-4, GPT-3.5 Turbo models
- Function/tool calling
- Streaming responses
- Embeddings for RAG
- Vision capabilities (GPT-4V)

**Use Cases:**
- Primary reasoning engine for agents
- Function calling for tool use
- Embeddings for semantic search
- Vision analysis for multimodal agents

---

### anthropic

**Official Anthropic Python Client (Claude)**

```python
from anthropic import Anthropic

client = Anthropic()

# Claude conversation
message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Analyze this research paper..."}
    ]
)

# Tool use with Claude
tools = [{
    "name": "search_arxiv",
    "description": "Search arXiv for papers",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        }
    }
}]

message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=4096,
    tools=tools,
    messages=messages
)
```

**Key Features:**
- Claude 3 models (Opus, Sonnet, Haiku)
- 200K context window
- Tool use (function calling)
- Strong reasoning capabilities
- Better at following instructions

**Use Cases:**
- Long document analysis
- Complex reasoning tasks
- Alternative to GPT-4
- Tasks requiring large context

**Model Comparison:**
- **Claude 3 Opus**: Most capable, best for complex tasks
- **Claude 3 Sonnet**: Balanced performance/cost
- **Claude 3 Haiku**: Fast, cost-effective

---

### mistralai

**Official Mistral AI Python Client**

```python
from mistralai.client import MistralClient

client = MistralClient(api_key="...")

# Chat completion
response = client.chat(
    model="mistral-large-latest",
    messages=[
        {"role": "user", "content": "Explain transformers"}
    ]
)

# Function calling
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather info",
        "parameters": {...}
    }
}]

response = client.chat(
    model="mistral-large-latest",
    messages=messages,
    tools=tools
)
```

**Key Features:**
- Mistral Large, Medium, Small models
- Function calling support
- Competitive pricing
- Open-source friendly
- European data residency option

**Use Cases:**
- Cost-effective alternative to GPT-4
- European compliance requirements
- Open-source model deployment
- Multilingual tasks

**Models:**
- **Mistral Large**: Most capable
- **Mistral Medium**: Balanced
- **Mistral Small**: Fast, efficient

---

### vertexai

**Google Cloud Vertex AI Client**

```python
from vertexai.preview.generative_models import GenerativeModel

model = GenerativeModel("gemini-pro")

# Generate content
response = model.generate_content("Explain AI agents")

# Multi-turn conversation
chat = model.start_chat()
response = chat.send_message("Hello!")
response = chat.send_message("Tell me more")

# Gemini Pro Vision
model_vision = GenerativeModel("gemini-pro-vision")
response = model_vision.generate_content([image, "Describe this"])
```

**Key Features:**
- Gemini Pro and Ultra models
- Multimodal (text, images, video)
- Enterprise features
- Google Cloud integration
- Grounding with Google Search

**Use Cases:**
- Multimodal analysis
- Enterprise deployments
- Google Cloud ecosystem
- Grounded generation

---

## Agent Tools

### tavily-python

**AI-Optimized Web Search**

```python
from tavily import TavilyClient

client = TavilyClient(api_key="...")

# Search the web
results = client.search(
    query="latest AI research 2024",
    search_depth="advanced",
    max_results=5
)

# Get context for LLM
context = client.get_search_context(
    query="quantum computing breakthroughs",
    max_tokens=4000
)

# Extract content from URL
content = client.extract(url="https://arxiv.org/abs/...")
```

**Key Features:**
- AI-optimized search results
- Source citations
- Content extraction
- Context generation for LLMs
- Advanced search options

**Use Cases:**
- Research agent web search
- Real-time information retrieval
- Source verification
- Content summarization

**Configuration:**
```python
# In .env
TAVILY_API_KEY=tvly-...

# Search options
search_depth: "basic" | "advanced"
include_domains: ["arxiv.org", "nature.com"]
exclude_domains: ["spam.com"]
```

---

### docstring-parser

**Extract Function Documentation**

```python
from docstring_parser import parse

def search_arxiv(query: str, max_results: int = 10):
    """
    Search arXiv for research papers.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of paper metadata dictionaries
    """
    pass

# Parse docstring
docstring = parse(search_arxiv.__doc__)
print(docstring.short_description)  # "Search arXiv for research papers."
print(docstring.params[0].arg_name)  # "query"
print(docstring.params[0].description)  # "Search query string"
```

**Key Features:**
- Parse Google, NumPy, Sphinx docstrings
- Extract parameters, returns, raises
- Type information extraction
- Multiple format support

**Use Cases:**
- Auto-generate tool descriptions for LLMs
- Function calling schema generation
- API documentation
- Agent tool registration

**Example for Agent Tools:**
```python
def create_tool_schema(func):
    """Generate OpenAI function schema from docstring"""
    doc = parse(func.__doc__)
    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": doc.short_description,
            "parameters": {
                "type": "object",
                "properties": {
                    param.arg_name: {
                        "type": "string",  # infer from type hints
                        "description": param.description
                    }
                    for param in doc.params
                }
            }
        }
    }
```

---

### textstat

**Text Readability Analysis**

```python
import textstat

text = """
Artificial intelligence agents are autonomous systems
that perceive their environment and take actions to
achieve specific goals.
"""

# Readability scores
flesch = textstat.flesch_reading_ease(text)  # 0-100, higher = easier
grade = textstat.flesch_kincaid_grade(text)  # US grade level
smog = textstat.smog_index(text)  # Simple Measure of Gobbledygook

# Text statistics
sentences = textstat.sentence_count(text)
words = textstat.lexicon_count(text)
syllables = textstat.syllable_count(text)

print(f"Reading ease: {flesch}")  # 60-70 = standard
print(f"Grade level: {grade}")    # 8-10 = high school
```

**Key Features:**
- Multiple readability formulas
- Text complexity metrics
- Language statistics
- Multi-language support

**Use Cases:**
- Evaluate agent-generated text quality
- Ensure appropriate reading level
- Content optimization
- Report quality assessment

**Readability Scales:**
- **Flesch Reading Ease**: 90-100 (very easy) to 0-30 (very difficult)
- **Flesch-Kincaid Grade**: US grade level (8 = 8th grade)
- **SMOG Index**: Years of education needed

---

## Integration Patterns

### Multi-Provider Agent

```python
from aisuite import Client

class MultiProviderAgent:
    def __init__(self):
        self.client = Client()
        self.providers = [
            "openai:gpt-4",
            "anthropic:claude-3-opus",
            "mistralai:mistral-large"
        ]
    
    def query_with_fallback(self, prompt):
        for model in self.providers:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response
            except Exception as e:
                print(f"Failed with {model}: {e}")
                continue
        raise Exception("All providers failed")
```

### Research Agent with Tools

```python
from tavily import TavilyClient
from openai import OpenAI

class ResearchAgent:
    def __init__(self):
        self.llm = OpenAI()
        self.search = TavilyClient()
    
    def research(self, topic):
        # Search the web
        results = self.search.search(topic, max_results=5)
        
        # Get context for LLM
        context = "\n\n".join([
            f"Source: {r['url']}\n{r['content']}"
            for r in results['results']
        ])
        
        # Generate report
        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a research assistant."},
                {"role": "user", "content": f"Summarize this research:\n\n{context}"}
            ]
        )
        
        return response.choices[0].message.content
```

---

## Best Practices

### API Key Management

```python
# Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
```

### Error Handling

```python
from openai import OpenAI, APIError, RateLimitError
import time

def call_with_retry(client, **kwargs):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(**kwargs)
        except RateLimitError:
            wait = 2 ** attempt  # Exponential backoff
            time.sleep(wait)
        except APIError as e:
            print(f"API error: {e}")
            raise
    raise Exception("Max retries exceeded")
```

### Cost Optimization

```python
# Use cheaper models for simple tasks
def choose_model(task_complexity):
    if task_complexity == "simple":
        return "openai:gpt-3.5-turbo"  # Cheaper
    elif task_complexity == "medium":
        return "anthropic:claude-3-sonnet"  # Balanced
    else:
        return "openai:gpt-4"  # Most capable
```

---

## See Also

- [Complete Dependencies](DEPENDENCIES.md)
- [Web Framework Tools](WEB_FRAMEWORK.md)
- [Environment Setup](../ENVIRONMENT_SETUP.md)
- [Agentic Roadmap](../AGENTIC_ROADMAP.md)
