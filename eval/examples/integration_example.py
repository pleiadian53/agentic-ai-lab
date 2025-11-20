"""
Example: Integrating Production Research Tools with Research Agent

This example demonstrates how to use the production research tools
from eval/research_tools.py with the research agent workflow.
"""

# ============================================================================
# Example 1: Basic Integration with AISuite
# ============================================================================

def example_basic_integration():
    """Simple integration with AISuite."""
    from aisuite import Client
    from eval import arxiv_search_tool, tavily_search_tool, wikipedia_search_tool
    
    client = Client()
    
    # Define tools for AISuite
    tools = [
        arxiv_search_tool,
        tavily_search_tool,
        wikipedia_search_tool,
    ]
    
    # Create research query
    messages = [{
        "role": "user",
        "content": "Research recent developments in quantum computing"
    }]
    
    # Execute with tool calling
    response = client.chat.completions.create(
        model="openai:gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_turns=5,
    )
    
    print(response.choices[0].message.content)


# ============================================================================
# Example 2: Integration with Source Evaluation
# ============================================================================

def example_with_evaluation():
    """Combine research tools with domain evaluation."""
    from eval import (
        tavily_search_tool,
        DomainEvaluator,
        ACADEMIC_DOMAINS,
    )
    
    # Search for information
    query = "CRISPR gene editing recent advances"
    results = tavily_search_tool(query, max_results=10)
    
    # Evaluate source quality
    evaluator = DomainEvaluator(
        preferred_domains=ACADEMIC_DOMAINS,
        min_ratio=0.5
    )
    
    evaluation = evaluator.evaluate_json(results)
    
    # Display results
    print(f"Query: {query}")
    print(f"Found {evaluation.total_sources} sources")
    print(f"Preferred: {evaluation.preferred_count} ({evaluation.preferred_ratio:.1%})")
    print(f"Status: {evaluation.status}")
    print(f"\nPreferred sources:")
    for source in evaluation.preferred_sources:
        print(f"  - {source.domain}: {source.url}")


# ============================================================================
# Example 3: Multi-Source Research with Aggregation
# ============================================================================

def example_multi_source_research():
    """Research across multiple sources and aggregate results."""
    from eval import search_all
    
    topic = "RNA therapeutics"
    
    # Search all sources
    results = search_all(topic, max_results_per_tool=5)
    
    # Process results
    print(f"Research Topic: {topic}\n")
    
    # arXiv papers
    arxiv_papers = [p for p in results["arxiv"] if "error" not in p]
    print(f"📚 Found {len(arxiv_papers)} arXiv papers:")
    for paper in arxiv_papers[:3]:
        print(f"  - {paper['title']}")
        print(f"    Authors: {', '.join(paper['authors'][:2])}")
        print(f"    Published: {paper['published']}\n")
    
    # Web results
    web_results = [r for r in results["tavily"] if "error" not in r]
    print(f"🌐 Found {len(web_results)} web results:")
    for result in web_results[:3]:
        print(f"  - {result['title']}")
        print(f"    {result['url']}\n")
    
    # Wikipedia
    wiki = results["wikipedia"]
    if wiki and "error" not in wiki[0]:
        print(f"📖 Wikipedia summary:")
        print(f"  Title: {wiki[0]['title']}")
        print(f"  {wiki[0]['summary'][:200]}...")


# ============================================================================
# Example 4: Advanced arXiv Search
# ============================================================================

def example_advanced_arxiv():
    """Demonstrate advanced arXiv search features."""
    from eval import arxiv_search_tool
    from datetime import datetime, timedelta
    
    # Search recent papers
    print("🔬 Recent Machine Learning Papers\n")
    papers = arxiv_search_tool(
        "machine learning",
        search_field="all",
        sort_by="submittedDate",
        max_results=5
    )
    
    for paper in papers:
        if "error" in paper:
            continue
        print(f"Title: {paper['title']}")
        print(f"Authors: {', '.join(paper['authors'][:3])}")
        print(f"Published: {paper['published']}")
        print(f"Categories: {', '.join(paper['categories'])}")
        print(f"URL: {paper['url']}\n")
    
    # Search by specific author
    print("\n👤 Papers by Specific Author\n")
    author_papers = arxiv_search_tool(
        "Hinton",
        search_field="au",
        max_results=3
    )
    
    for paper in author_papers:
        if "error" in paper:
            continue
        print(f"- {paper['title']} ({paper['published']})")


# ============================================================================
# Example 5: News Monitoring
# ============================================================================

def example_news_monitoring():
    """Monitor news for specific topics."""
    from eval import tavily_search_tool
    
    topics = [
        "quantum computing breakthrough",
        "AI regulation",
        "gene therapy clinical trials"
    ]
    
    print("📰 Recent News Monitoring\n")
    
    for topic in topics:
        print(f"Topic: {topic}")
        news = tavily_search_tool(
            topic,
            topic="news",
            days=7,
            max_results=3
        )
        
        for item in news:
            if "error" in item:
                continue
            print(f"  - {item['title']}")
            print(f"    {item['url']}")
        print()


# ============================================================================
# Example 6: Research Agent Workflow
# ============================================================================

def example_research_workflow():
    """Complete research workflow with tools and evaluation."""
    from aisuite import Client
    from eval import (
        arxiv_search_tool,
        tavily_search_tool,
        wikipedia_search_tool,
        DomainEvaluator,
        BIOLOGY_FOCUSED_DOMAINS,
    )
    
    # Initialize
    client = Client()
    tools = [arxiv_search_tool, tavily_search_tool, wikipedia_search_tool]
    
    # Research task
    task = """
    Research the current state of mRNA vaccine technology.
    Focus on:
    1. Recent scientific papers
    2. Clinical trial results
    3. Manufacturing challenges
    
    Provide a comprehensive summary with sources.
    """
    
    # Execute research
    messages = [{"role": "user", "content": task}]
    
    response = client.chat.completions.create(
        model="openai:gpt-4o",
        messages=messages,
        tools=tools,
        max_turns=5,
    )
    
    # Get the research output
    research_output = response.choices[0].message.content
    
    # Evaluate sources
    evaluator = DomainEvaluator(
        preferred_domains=BIOLOGY_FOCUSED_DOMAINS,
        min_ratio=0.6
    )
    
    evaluation = evaluator.evaluate_text(research_output)
    
    # Display results
    print("=" * 80)
    print("RESEARCH OUTPUT")
    print("=" * 80)
    print(research_output)
    print("\n" + "=" * 80)
    print("SOURCE EVALUATION")
    print("=" * 80)
    print(f"Status: {evaluation.status}")
    print(f"Total sources: {evaluation.total_sources}")
    print(f"Preferred sources: {evaluation.preferred_count} ({evaluation.preferred_ratio:.1%})")
    print(f"\nPreferred domains used:")
    for source in evaluation.preferred_sources:
        print(f"  ✓ {source.domain}")


# ============================================================================
# Example 7: Caching and Performance
# ============================================================================

def example_caching():
    """Demonstrate caching benefits."""
    import time
    from eval import wikipedia_search_tool
    
    query = "Machine learning"
    
    # First call - hits API
    print("First call (API request)...")
    start = time.time()
    result1 = wikipedia_search_tool(query)
    time1 = time.time() - start
    print(f"Time: {time1:.3f}s")
    
    # Second call - cached
    print("\nSecond call (cached)...")
    start = time.time()
    result2 = wikipedia_search_tool(query)
    time2 = time.time() - start
    print(f"Time: {time2:.3f}s")
    
    print(f"\nSpeedup: {time1/time2:.1f}x faster")
    print(f"Same result: {result1 == result2}")


# ============================================================================
# Example 8: Error Handling
# ============================================================================

def example_error_handling():
    """Demonstrate robust error handling."""
    from eval import arxiv_search_tool, tavily_search_tool, wikipedia_search_tool
    
    # Test various error scenarios
    
    # 1. Wikipedia disambiguation
    print("1. Ambiguous Wikipedia query:")
    result = wikipedia_search_tool("Python")
    if result and "error" in result[0]:
        print(f"   Error: {result[0]['error']}")
    
    # 2. Wikipedia not found
    print("\n2. Non-existent Wikipedia page:")
    result = wikipedia_search_tool("asdfghjklqwertyuiop")
    if result and "error" in result[0]:
        print(f"   Error: {result[0]['error']}")
    
    # 3. Empty query
    print("\n3. Empty arXiv query:")
    result = arxiv_search_tool("")
    if result and "error" in result[0]:
        print(f"   Error: {result[0]['error']}")
    
    print("\n✓ All errors handled gracefully")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("Research Tools Integration Examples\n")
    print("=" * 80)
    
    # Run examples (uncomment to execute)
    
    # example_basic_integration()
    # example_with_evaluation()
    # example_multi_source_research()
    # example_advanced_arxiv()
    # example_news_monitoring()
    # example_research_workflow()
    # example_caching()
    # example_error_handling()
    
    print("\nTo run examples, uncomment the desired function calls in __main__")
