#!/usr/bin/env python3
"""
Quick Demo: Production Research Tools

Run this script to see the enhanced research tools in action.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def demo_arxiv():
    """Demo arXiv search with enhanced features."""
    print("\n" + "=" * 80)
    print("DEMO 1: arXiv Search")
    print("=" * 80)
    
    from eval import arxiv_search_tool
    
    print("\n📚 Searching arXiv for 'quantum computing'...\n")
    
    papers = arxiv_search_tool("quantum computing", max_results=3)
    
    for i, paper in enumerate(papers, 1):
        if "error" in paper:
            print(f"Error: {paper['error']}")
            continue
            
        print(f"{i}. {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'][:3])}")
        if len(paper['authors']) > 3:
            print(f"            (+ {len(paper['authors']) - 3} more)")
        print(f"   Published: {paper['published']}")
        print(f"   Categories: {', '.join(paper['categories'][:3])}")
        print(f"   URL: {paper['url']}")
        print(f"   Summary: {paper['summary'][:150]}...")
        print()


def demo_tavily():
    """Demo Tavily web search."""
    print("\n" + "=" * 80)
    print("DEMO 2: Tavily Web Search")
    print("=" * 80)
    
    from eval import tavily_search_tool
    
    print("\n🌐 Searching web for 'latest AI developments'...\n")
    
    results = tavily_search_tool("latest AI developments", max_results=3)
    
    for i, result in enumerate(results, 1):
        if "error" in result:
            print(f"Error: {result['error']}")
            continue
            
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Content: {result['content'][:150]}...")
        if 'score' in result:
            print(f"   Relevance: {result['score']:.2f}")
        print()


def demo_wikipedia():
    """Demo Wikipedia search with caching."""
    print("\n" + "=" * 80)
    print("DEMO 3: Wikipedia Search (with Caching)")
    print("=" * 80)
    
    from eval import wikipedia_search_tool
    import time
    
    query = "Machine learning"
    
    print(f"\n📖 Searching Wikipedia for '{query}'...\n")
    
    # First call
    print("First call (hits API)...")
    start = time.time()
    result = wikipedia_search_tool(query, sentences=3)
    time1 = time.time() - start
    
    if result and "error" not in result[0]:
        print(f"Title: {result[0]['title']}")
        print(f"Summary: {result[0]['summary']}")
        print(f"URL: {result[0]['url']}")
        print(f"Time: {time1:.3f}s")
    
    # Second call (cached)
    print("\nSecond call (cached)...")
    start = time.time()
    result2 = wikipedia_search_tool(query, sentences=3)
    time2 = time.time() - start
    print(f"Time: {time2:.3f}s")
    print(f"Speedup: {time1/time2:.1f}x faster! ⚡")


def demo_search_all():
    """Demo searching all tools at once."""
    print("\n" + "=" * 80)
    print("DEMO 4: Multi-Source Search")
    print("=" * 80)
    
    from eval import search_all
    
    topic = "CRISPR gene editing"
    print(f"\n🔬 Searching all sources for '{topic}'...\n")
    
    results = search_all(topic, max_results_per_tool=2)
    
    # arXiv
    arxiv_papers = [p for p in results["arxiv"] if "error" not in p]
    print(f"📚 arXiv: Found {len(arxiv_papers)} papers")
    for paper in arxiv_papers:
        print(f"   - {paper['title'][:60]}...")
    
    # Tavily
    web_results = [r for r in results["tavily"] if "error" not in r]
    print(f"\n🌐 Web: Found {len(web_results)} results")
    for result in web_results:
        print(f"   - {result['title'][:60]}...")
    
    # Wikipedia
    wiki = results["wikipedia"]
    if wiki and "error" not in wiki[0]:
        print(f"\n📖 Wikipedia: {wiki[0]['title']}")
        print(f"   {wiki[0]['summary'][:100]}...")


def demo_with_evaluation():
    """Demo combining search with source evaluation."""
    print("\n" + "=" * 80)
    print("DEMO 5: Search + Source Evaluation")
    print("=" * 80)
    
    from eval import tavily_search_tool, DomainEvaluator, ACADEMIC_DOMAINS
    
    query = "quantum computing research"
    print(f"\n🔍 Searching and evaluating sources for '{query}'...\n")
    
    # Search
    results = tavily_search_tool(query, max_results=5)
    
    # Evaluate
    evaluator = DomainEvaluator(
        preferred_domains=ACADEMIC_DOMAINS,
        min_ratio=0.4
    )
    
    evaluation = evaluator.evaluate_json(results)
    
    # Display
    print(f"Status: {evaluation.status}")
    print(f"Total sources: {evaluation.total_sources}")
    print(f"Preferred sources: {evaluation.preferred_count} ({evaluation.preferred_ratio:.1%})")
    
    if evaluation.preferred_sources:
        print(f"\n✅ Preferred domains found:")
        for source in evaluation.preferred_sources[:3]:
            print(f"   - {source.domain}")
    
    if evaluation.other_sources:
        print(f"\n⚠️  Other domains:")
        for source in evaluation.other_sources[:3]:
            print(f"   - {source.domain}")


def demo_advanced_arxiv():
    """Demo advanced arXiv features."""
    print("\n" + "=" * 80)
    print("DEMO 6: Advanced arXiv Search")
    print("=" * 80)
    
    from eval import arxiv_search_tool
    
    # Recent papers
    print("\n📅 Recent machine learning papers (sorted by date)...\n")
    
    papers = arxiv_search_tool(
        "machine learning",
        search_field="all",
        sort_by="submittedDate",
        max_results=3
    )
    
    for paper in papers:
        if "error" in paper:
            continue
        print(f"- {paper['title'][:60]}...")
        print(f"  Published: {paper['published']}, Updated: {paper['updated']}")
        print(f"  Categories: {', '.join(paper['categories'][:2])}")
        print()


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("PRODUCTION RESEARCH TOOLS - QUICK DEMO")
    print("=" * 80)
    print("\nThis demo showcases the enhanced research tools from eval/research_tools.py")
    print("These tools are ready for integration with tool_use/research_agent")
    
    try:
        # Run demos
        demo_arxiv()
        demo_tavily()
        demo_wikipedia()
        demo_search_all()
        demo_with_evaluation()
        demo_advanced_arxiv()
        
        print("\n" + "=" * 80)
        print("DEMO COMPLETE ✅")
        print("=" * 80)
        print("\nKey Features Demonstrated:")
        print("  ✓ Enhanced arXiv search with advanced options")
        print("  ✓ Tavily web search with relevance scoring")
        print("  ✓ Wikipedia search with automatic caching")
        print("  ✓ Multi-source search aggregation")
        print("  ✓ Integration with domain evaluation")
        print("  ✓ Advanced search features (sorting, filtering)")
        print("\nNext Steps:")
        print("  1. Review eval/RESEARCH_TOOLS_GUIDE.md for full documentation")
        print("  2. Check eval/examples/integration_example.py for more examples")
        print("  3. Integrate with tool_use/research_agent")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  - Set TAVILY_API_KEY environment variable")
        print("  - Installed required packages: requests, tavily, wikipedia")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
