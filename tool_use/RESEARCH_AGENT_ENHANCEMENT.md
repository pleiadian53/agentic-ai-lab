# Enhanced Research Agent: Combining Reflection + Tool Use

## Overview

This document outlines how to enhance the existing reflection-based research agent (M2) with tool-calling capabilities (M3) to create a more sophisticated, fact-based essay writing system.

## Current State (M2 - Reflection Pattern)

**Location**: `/reflection/research_agent/`

**Workflow**:
```
1. Generate Draft (LLM generates essay from topic)
2. Reflect on Draft (LLM critiques the essay)
3. Revise Draft (LLM improves based on critique)
4. Repeat steps 2-3 until convergence or max iterations
```

**Limitations**:
- No access to external information sources
- Cannot verify facts or claims
- No citation generation or validation
- Relies solely on LLM's training data
- Cannot check for plagiarism or quality metrics

## Enhanced State (M3 - Reflection + Tool Use)

**Location**: `/tool_use/research_tools.py`, `/tool_use/examples/enhanced_research_agent.py`

**Enhanced Workflow**:
```
1. Research Phase (NEW)
   └─ Agent searches for information using tools
   
2. Generate Draft
   └─ Agent writes essay WITH access to research tools
   
3. Validate Phase (NEW)
   └─ Agent checks facts, citations, quality
   
4. Reflect on Draft
   └─ Agent critiques WITH validation results
   
5. Revise Draft
   └─ Agent improves using reflection + tool-verified data
   
6. Repeat steps 3-5 until convergence
```

## Tool Categories

### 1. Research Tools (`research_tools.py`)

**Purpose**: Gather information during draft generation

```python
def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web using Tavily API for current information.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        List of search results with title, url, snippet
    """

def search_arxiv(query: str, max_results: int = 5) -> list[dict]:
    """
    Search arXiv for academic papers.
    
    Args:
        query: Search query (topic, author, etc.)
        max_results: Maximum papers to return
        
    Returns:
        List of papers with title, authors, abstract, url
    """

def search_wikipedia(query: str) -> dict:
    """
    Get Wikipedia summary for a topic.
    
    Args:
        query: Topic to search
        
    Returns:
        Summary text and page URL
    """

def get_current_date() -> str:
    """
    Get current date for time-sensitive research.
    
    Returns:
        Current date in YYYY-MM-DD format
    """
```

### 2. Citation Tools (`citation_tools.py`)

**Purpose**: Generate and validate citations

```python
def generate_citation(
    title: str,
    authors: list[str],
    year: int,
    url: str,
    style: str = "apa"
) -> str:
    """
    Generate a formatted citation.
    
    Args:
        title: Publication title
        authors: List of author names
        year: Publication year
        url: Source URL
        style: Citation style (apa, mla, chicago)
        
    Returns:
        Formatted citation string
    """

def validate_url(url: str) -> dict:
    """
    Check if a URL is accessible and valid.
    
    Args:
        url: URL to validate
        
    Returns:
        Dict with status, accessible (bool), title
    """

def extract_citations_from_text(text: str) -> list[str]:
    """
    Extract citation references from essay text.
    
    Args:
        text: Essay text
        
    Returns:
        List of citation references found
    """
```

### 3. Quality Tools (`quality_tools.py`)

**Purpose**: Analyze and validate essay quality

```python
def analyze_readability(text: str) -> dict:
    """
    Calculate readability metrics.
    
    Args:
        text: Essay text
        
    Returns:
        Dict with flesch_score, grade_level, avg_sentence_length
    """

def check_grammar(text: str) -> list[dict]:
    """
    Check for grammar and spelling issues.
    
    Args:
        text: Text to check
        
    Returns:
        List of issues with type, message, suggestion
    """

def verify_facts(claims: list[str]) -> list[dict]:
    """
    Verify factual claims using fact-checking APIs.
    
    Args:
        claims: List of factual statements to verify
        
    Returns:
        List of verification results with claim, verdict, sources
    """

def count_words(text: str) -> dict:
    """
    Detailed word count analysis.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dict with total_words, unique_words, avg_word_length
    """
```

## Enhanced Workflow Implementation

### Phase 1: Research-Augmented Draft Generation

**Before (M2)**:
```python
def generate_draft(topic: str, model: str, client: ai.Client) -> str:
    prompt = f"Write an essay about: {topic}"
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

**After (M3)**:
```python
from tool_use import ToolClient
from tool_use import research_tools

def generate_draft_with_research(
    topic: str,
    model: str,
    client: ToolClient
) -> tuple[str, list[dict]]:
    """Generate draft with access to research tools."""
    
    prompt = f"""Write a well-researched essay about: {topic}

You have access to research tools. Use them to:
1. Find current information and statistics
2. Locate academic sources
3. Verify facts and claims

Include proper citations for all sources used."""
    
    response = client.chat(
        prompt=prompt,
        tools=[
            research_tools.search_web,
            research_tools.search_arxiv,
            research_tools.search_wikipedia,
            research_tools.get_current_date,
        ],
        max_turns=15  # Allow multiple tool calls
    )
    
    # Extract essay and sources used
    essay = response.choices[0].message.content
    sources = extract_sources_from_response(response)
    
    return essay, sources
```

### Phase 2: Validation Before Reflection

**New Step**:
```python
from tool_use import quality_tools, citation_tools

def validate_draft(
    essay: str,
    sources: list[dict],
    client: ToolClient
) -> dict:
    """Validate essay quality and citations."""
    
    validation_prompt = f"""Analyze this essay and extract:
1. All factual claims that need verification
2. All citations that need validation

Essay:
{essay}"""
    
    response = client.chat(
        prompt=validation_prompt,
        tools=[
            quality_tools.analyze_readability,
            quality_tools.check_grammar,
            quality_tools.verify_facts,
            citation_tools.validate_url,
            citation_tools.extract_citations_from_text,
        ],
        max_turns=10
    )
    
    return {
        "readability": response.readability_score,
        "grammar_issues": response.grammar_issues,
        "fact_checks": response.fact_checks,
        "citation_validity": response.citation_validity,
    }
```

### Phase 3: Enhanced Reflection with Validation Data

**Before (M2)**:
```python
def reflect_on_draft(draft: str, model: str, client: ai.Client) -> str:
    prompt = f"Critique this essay:\n\n{draft}"
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

**After (M3)**:
```python
def reflect_with_validation(
    draft: str,
    validation_results: dict,
    model: str,
    client: ai.Client
) -> str:
    """Reflect on draft with validation data."""
    
    prompt = f"""Critique this essay considering the validation results:

Essay:
{draft}

Validation Results:
- Readability Score: {validation_results['readability']}
- Grammar Issues: {len(validation_results['grammar_issues'])}
- Fact Check Results: {validation_results['fact_checks']}
- Citation Validity: {validation_results['citation_validity']}

Provide specific feedback on:
1. Content accuracy and fact usage
2. Citation quality and completeness
3. Writing quality and readability
4. Areas needing improvement"""
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

### Phase 4: Tool-Assisted Revision

**After (M3)**:
```python
def revise_with_tools(
    draft: str,
    reflection: str,
    validation_results: dict,
    client: ToolClient
) -> str:
    """Revise essay with access to research and citation tools."""
    
    prompt = f"""Revise this essay based on the feedback and validation results.

Original Essay:
{draft}

Feedback:
{reflection}

Validation Issues:
{validation_results}

Use available tools to:
1. Find better sources for weak claims
2. Fix citation formatting
3. Verify and correct factual errors
4. Improve readability"""
    
    response = client.chat(
        prompt=prompt,
        tools=[
            research_tools.search_web,
            research_tools.search_arxiv,
            citation_tools.generate_citation,
            quality_tools.check_grammar,
        ],
        max_turns=15
    )
    
    return response.choices[0].message.content
```

## Complete Enhanced Workflow

```python
from tool_use import ToolClient
from tool_use import research_tools, citation_tools, quality_tools

def run_enhanced_research_workflow(
    topic: str,
    max_iterations: int = 3,
    model: str = "openai:gpt-4o"
) -> dict:
    """
    Run the complete enhanced research workflow.
    
    Combines reflection pattern (M2) with tool use (M3).
    """
    client = ToolClient(model=model)
    iterations = []
    
    # Phase 1: Research-augmented draft generation
    draft, sources = generate_draft_with_research(topic, model, client)
    
    iterations.append({
        "iteration": 1,
        "essay": draft,
        "sources": sources,
        "validation": None,
        "reflection": None,
    })
    
    # Phases 2-4: Validate → Reflect → Revise loop
    for i in range(2, max_iterations + 1):
        # Validate current draft
        validation = validate_draft(draft, sources, client)
        
        # Reflect with validation data
        reflection = reflect_with_validation(draft, validation, model, client)
        
        # Check if essay is good enough
        if is_satisfactory(validation, reflection):
            break
        
        # Revise with tools
        draft = revise_with_tools(draft, reflection, validation, client)
        
        iterations.append({
            "iteration": i,
            "essay": draft,
            "sources": extract_sources_from_text(draft),
            "validation": validation,
            "reflection": reflection,
        })
    
    return {
        "topic": topic,
        "iterations": iterations,
        "final_essay": draft,
        "total_iterations": len(iterations),
    }
```

## Implementation Checklist

### Core Infrastructure (Reuse from M3 refactoring)
- [x] `ToolClient` class
- [x] `ToolRegistry` class
- [x] `display_functions` for visualization
- [x] Package structure

### New Tool Modules
- [ ] `research_tools.py` - Web search, academic search, Wikipedia
- [ ] `citation_tools.py` - Citation generation and validation
- [ ] `quality_tools.py` - Readability, grammar, fact-checking

### Integration with Reflection Pattern
- [ ] Enhanced draft generation with research tools
- [ ] Validation phase before reflection
- [ ] Enhanced reflection with validation data
- [ ] Tool-assisted revision

### Examples and Documentation
- [ ] `examples/enhanced_research_agent.py` - Complete workflow
- [ ] `examples/research_tools_demo.py` - Individual tool demos
- [ ] Update README with research agent section
- [ ] Create comparison notebook (M2 vs M3 approach)

### Testing and Validation
- [ ] Test each tool independently
- [ ] Test integrated workflow
- [ ] Compare output quality (M2 vs M3)
- [ ] Measure improvement metrics

## Key Benefits of Enhancement

1. **Factual Accuracy**: Essays backed by real sources, not just LLM knowledge
2. **Current Information**: Access to recent data and research
3. **Proper Citations**: Automatic citation generation and validation
4. **Quality Assurance**: Objective metrics for readability and grammar
5. **Verifiable Claims**: Fact-checking integration
6. **Reproducibility**: Clear source tracking and validation logs

## Example Output Comparison

**M2 (Reflection Only)**:
- Essay based on LLM training data
- No external sources
- Self-critique without validation
- May contain outdated or incorrect information

**M3 (Reflection + Tools)**:
- Essay with cited sources
- Current information from web/academic sources
- Critique backed by validation metrics
- Fact-checked claims
- Proper bibliography

## Next Steps

1. Implement `research_tools.py` with Tavily and arXiv APIs
2. Implement `citation_tools.py` with citation formatting
3. Implement `quality_tools.py` with readability metrics
4. Create `enhanced_research_agent.py` example
5. Test and compare with M2 baseline
6. Document improvements and best practices

This enhancement demonstrates how **tool use (M3) amplifies the reflection pattern (M2)** to create more sophisticated, reliable, and verifiable agentic workflows.
