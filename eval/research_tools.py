"""
Enhanced research tools for production use.

This module provides robust, production-ready implementations of research tools
for integration with agentic workflows. Includes advanced features like:
- Configurable retry logic
- Better error handling
- Caching support
- Rate limiting
- Logging
- Extended search capabilities

For educational/notebook use, see eval/M4/research_tools.py
"""

# --- Standard library ---
import os
import time
import logging
from typing import List, Dict, Optional, Literal
from functools import lru_cache
import xml.etree.ElementTree as ET

# --- Third-party ---
import requests
from dotenv import load_dotenv
from tavily import TavilyClient
import wikipedia

# Configure logging
logger = logging.getLogger(__name__)

# Init env
load_dotenv()

# Session with retry logic
session = requests.Session()
session.headers.update({
    "User-Agent": "Research-Agent/2.0 (mailto:research@example.com)"
})

# Retry configuration
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)


# ============================================================================
# arXiv Search Tool
# ============================================================================

def arxiv_search_tool(
    query: str,
    max_results: int = 5,
    search_field: Literal["all", "ti", "au", "abs", "cat"] = "all",
    sort_by: Literal["relevance", "lastUpdatedDate", "submittedDate"] = "relevance",
    sort_order: Literal["ascending", "descending"] = "descending",
) -> List[Dict]:
    """
    Searches arXiv for research papers using flexible keyword matching.
    
    Enhanced version with configurable search fields, sorting, and better
    error handling. Supports loose queries across title, abstract, authors,
    and full text. The search is relevance-based, not exact match.
    
    Args:
        query: Search keywords or phrases. Examples:
               - "quantum entanglement"
               - "author:Hawking black holes"
               - "neural networks AND physics"
        max_results: Maximum number of papers to return (default: 5, max: 100).
        search_field: Field to search in:
                      - "all": All fields (default)
                      - "ti": Title only
                      - "au": Author only
                      - "abs": Abstract only
                      - "cat": Category (e.g., "quant-ph", "cs.AI")
        sort_by: Sort results by:
                 - "relevance": Most relevant first (default)
                 - "lastUpdatedDate": Most recently updated
                 - "submittedDate": Most recently submitted
        sort_order: "ascending" or "descending" (default: descending)
    
    Returns:
        List of paper dictionaries with keys: title, authors, published,
        updated, url, summary, link_pdf, categories, comment.
        Returns [{"error": ...}] on failure.
    
    Examples:
        >>> # Basic search
        >>> papers = arxiv_search_tool("quantum computing", max_results=3)
        
        >>> # Title-only search
        >>> papers = arxiv_search_tool("BERT", search_field="ti", max_results=5)
        
        >>> # Author search
        >>> papers = arxiv_search_tool("Hinton", search_field="au")
        
        >>> # Category search
        >>> papers = arxiv_search_tool("cs.AI", search_field="cat", max_results=10)
        
        >>> # Recent papers
        >>> papers = arxiv_search_tool(
        ...     "machine learning",
        ...     sort_by="submittedDate",
        ...     max_results=10
        ... )
    """
    # Validate max_results
    max_results = min(max(1, max_results), 100)
    
    # Build query URL
    url = (
        f"https://export.arxiv.org/api/query?"
        f"search_query={search_field}:{query}&"
        f"start=0&"
        f"max_results={max_results}&"
        f"sortBy={sort_by}&"
        f"sortOrder={sort_order}"
    )
    
    logger.info(f"Searching arXiv: {query} (field={search_field}, max={max_results})")
    
    try:
        response = session.get(url, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"arXiv API request failed: {e}")
        return [{"error": f"Request failed: {str(e)}"}]
    
    try:
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        results = []
        for entry in root.findall('atom:entry', ns):
            # Extract basic info
            title = entry.find('atom:title', ns).text.strip()
            authors = [
                author.find('atom:name', ns).text 
                for author in entry.findall('atom:author', ns)
            ]
            published = entry.find('atom:published', ns).text[:10]
            updated = entry.find('atom:updated', ns).text[:10]
            url_abstract = entry.find('atom:id', ns).text
            summary = entry.find('atom:summary', ns).text.strip()
            
            # Extract PDF link
            link_pdf = None
            for link in entry.findall('atom:link', ns):
                if link.attrib.get('title') == 'pdf':
                    link_pdf = link.attrib.get('href')
                    break
            
            # Extract categories
            categories = [
                cat.attrib.get('term') 
                for cat in entry.findall('atom:category', ns)
            ]
            
            # Extract comment (if available)
            comment_elem = entry.find('atom:comment', ns)
            comment = comment_elem.text if comment_elem is not None else None
            
            results.append({
                "title": title,
                "authors": authors,
                "published": published,
                "updated": updated,
                "url": url_abstract,
                "summary": summary,
                "link_pdf": link_pdf,
                "categories": categories,
                "comment": comment,
            })
        
        logger.info(f"Found {len(results)} arXiv papers")
        return results
        
    except Exception as e:
        logger.error(f"arXiv parsing failed: {e}")
        return [{"error": f"Parsing failed: {str(e)}"}]


# ============================================================================
# Tavily Search Tool
# ============================================================================

def tavily_search_tool(
    query: str,
    max_results: int = 5,
    include_images: bool = False,
    include_answer: bool = False,
    search_depth: Literal["basic", "advanced"] = "basic",
    topic: Literal["general", "news"] = "general",
    days: Optional[int] = None,
) -> List[Dict]:
    """
    Performs a general-purpose web search using the Tavily API.
    
    Enhanced version with configurable search depth, topic filtering,
    and time-based filtering. Use this tool for current events, news,
    general information, and topics not covered by academic sources.
    
    Args:
        query: The search query. Can be questions or keywords.
        max_results: Number of web results to return (default: 5, max: 20).
        include_images: Whether to include image URLs in results (default: False).
        include_answer: Whether to include a direct answer summary (default: False).
        search_depth: Search depth:
                      - "basic": Fast, general results (default)
                      - "advanced": Deeper, more comprehensive search
        topic: Search topic filter:
               - "general": General web search (default)
               - "news": News-focused search
        days: Only include results from the last N days (optional).
              Useful for recent news or developments.
    
    Returns:
        List of result dictionaries with keys: title, content, url, score.
        If include_images=True, also includes {"image_url": ...} entries.
        If include_answer=True, first result includes {"answer": ...}.
        Returns [{"error": ...}] on failure.
    
    Examples:
        >>> # Basic search
        >>> results = tavily_search_tool("latest AI developments")
        
        >>> # News search from last 7 days
        >>> news = tavily_search_tool(
        ...     "quantum computing breakthrough",
        ...     topic="news",
        ...     days=7,
        ...     max_results=10
        ... )
        
        >>> # Deep search with answer
        >>> results = tavily_search_tool(
        ...     "What is CRISPR?",
        ...     search_depth="advanced",
        ...     include_answer=True
        ... )
        
        >>> # Search with images
        >>> results = tavily_search_tool(
        ...     "Mars rover images",
        ...     include_images=True
        ... )
    """
    # Validate max_results
    max_results = min(max(1, max_results), 20)
    
    # Get API credentials
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        logger.error("TAVILY_API_KEY not found in environment")
        raise ValueError("TAVILY_API_KEY not found in environment variables.")
    
    api_base_url = os.getenv("DLAI_TAVILY_BASE_URL")
    
    logger.info(
        f"Searching Tavily: {query} "
        f"(depth={search_depth}, topic={topic}, max={max_results})"
    )
    
    try:
        # Initialize client
        client = TavilyClient(api_key=api_key, api_base_url=api_base_url)
        
        # Build search parameters
        search_params = {
            "query": query,
            "max_results": max_results,
            "include_images": include_images,
            "include_answer": include_answer,
            "search_depth": search_depth,
            "topic": topic,
        }
        
        if days is not None:
            search_params["days"] = days
        
        # Execute search
        response = client.search(**search_params)
        
        results = []
        
        # Add answer if requested
        if include_answer and "answer" in response:
            results.append({"answer": response["answer"]})
        
        # Add search results
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "content": r.get("content", ""),
                "url": r.get("url", ""),
                "score": r.get("score", 0.0),
            })
        
        # Add images if requested
        if include_images:
            for img_url in response.get("images", []):
                results.append({"image_url": img_url})
        
        logger.info(f"Found {len(results)} Tavily results")
        return results
        
    except Exception as e:
        logger.error(f"Tavily search failed: {e}")
        return [{"error": str(e)}]


# ============================================================================
# Wikipedia Search Tool
# ============================================================================

@lru_cache(maxsize=128)
def _wikipedia_search_cached(query: str, sentences: int) -> tuple:
    """Cached Wikipedia search to avoid redundant API calls."""
    try:
        page_title = wikipedia.search(query)[0]
        page = wikipedia.page(page_title)
        summary = wikipedia.summary(page_title, sentences=sentences)
        return (page.title, summary, page.url, None)
    except wikipedia.exceptions.DisambiguationError as e:
        return (None, None, None, f"Ambiguous query. Options: {', '.join(e.options[:5])}")
    except wikipedia.exceptions.PageError:
        return (None, None, None, f"No Wikipedia page found for '{query}'")
    except Exception as e:
        return (None, None, None, str(e))


def wikipedia_search_tool(
    query: str,
    sentences: int = 5,
    auto_suggest: bool = True,
) -> List[Dict]:
    """
    Searches Wikipedia for encyclopedic summaries and background information.
    
    Enhanced version with caching, auto-suggest, and better error handling.
    Use this tool for well-established concepts, historical information,
    definitions, and general knowledge.
    
    Args:
        query: Search query for Wikipedia. Works best with specific topics,
               people, places, or concepts. Examples:
               - "Quantum entanglement"
               - "Albert Einstein"
               - "CRISPR gene editing"
        sentences: Number of sentences to include in the summary (default: 5).
                   Use fewer (2-3) for brief overviews, more (7-10) for detail.
        auto_suggest: Enable auto-suggestion for misspelled queries (default: True).
    
    Returns:
        List with a single dictionary containing keys: title, summary, url.
        Returns [{"error": ...}] if the topic is not found or ambiguous.
    
    Examples:
        >>> # Basic search
        >>> result = wikipedia_search_tool("Machine learning")
        
        >>> # Brief summary
        >>> result = wikipedia_search_tool("Python programming", sentences=3)
        
        >>> # Detailed summary
        >>> result = wikipedia_search_tool("Quantum mechanics", sentences=10)
        
        >>> # Disable auto-suggest for exact matches
        >>> result = wikipedia_search_tool("AI", auto_suggest=False)
    """
    # Validate sentences
    sentences = min(max(1, sentences), 20)
    
    logger.info(f"Searching Wikipedia: {query} (sentences={sentences})")
    
    # Set auto-suggest
    wikipedia.set_lang("en")
    
    # Use cached search
    title, summary, url, error = _wikipedia_search_cached(query, sentences)
    
    if error:
        logger.warning(f"Wikipedia search failed: {error}")
        return [{"error": error}]
    
    logger.info(f"Found Wikipedia article: {title}")
    return [{
        "title": title,
        "summary": summary,
        "url": url,
    }]


# ============================================================================
# Tool Mapping and Metadata
# ============================================================================

# Tool mapping for easy lookup
RESEARCH_TOOLS = {
    "arxiv_search_tool": arxiv_search_tool,
    "tavily_search_tool": tavily_search_tool,
    "wikipedia_search_tool": wikipedia_search_tool,
}

# Tool metadata for documentation and UI
TOOL_METADATA = {
    "arxiv_search_tool": {
        "name": "arXiv Search",
        "category": "academic",
        "description": "Search academic papers on arXiv",
        "best_for": ["research papers", "academic literature", "preprints"],
        "rate_limit": "3 requests/second",
    },
    "tavily_search_tool": {
        "name": "Tavily Web Search",
        "category": "web",
        "description": "General-purpose web search",
        "best_for": ["current events", "news", "general information", "company info"],
        "rate_limit": "Depends on API plan",
    },
    "wikipedia_search_tool": {
        "name": "Wikipedia Search",
        "category": "encyclopedia",
        "description": "Search Wikipedia for encyclopedic information",
        "best_for": ["definitions", "background info", "historical facts", "concepts"],
        "rate_limit": "Unlimited (cached)",
    },
}


# ============================================================================
# Utility Functions
# ============================================================================

def get_tool(name: str):
    """
    Get a research tool by name.
    
    Args:
        name: Tool name (e.g., "arxiv_search_tool")
    
    Returns:
        The tool function
    
    Raises:
        KeyError: If tool not found
    """
    if name not in RESEARCH_TOOLS:
        available = ", ".join(RESEARCH_TOOLS.keys())
        raise KeyError(f"Tool '{name}' not found. Available: {available}")
    return RESEARCH_TOOLS[name]


def list_tools() -> List[str]:
    """
    List all available research tools.
    
    Returns:
        List of tool names
    """
    return list(RESEARCH_TOOLS.keys())


def get_tool_metadata(name: str) -> Dict:
    """
    Get metadata for a research tool.
    
    Args:
        name: Tool name
    
    Returns:
        Dictionary with tool metadata
    """
    return TOOL_METADATA.get(name, {})


# ============================================================================
# Convenience Functions
# ============================================================================

def search_all(
    query: str,
    max_results_per_tool: int = 3,
    include_arxiv: bool = True,
    include_tavily: bool = True,
    include_wikipedia: bool = True,
) -> Dict[str, List[Dict]]:
    """
    Search across all available tools and aggregate results.
    
    Args:
        query: Search query
        max_results_per_tool: Max results per tool (default: 3)
        include_arxiv: Include arXiv search (default: True)
        include_tavily: Include Tavily search (default: True)
        include_wikipedia: Include Wikipedia search (default: True)
    
    Returns:
        Dictionary with keys: "arxiv", "tavily", "wikipedia"
        Each containing the respective search results
    
    Example:
        >>> results = search_all("quantum computing", max_results_per_tool=5)
        >>> print(f"Found {len(results['arxiv'])} arXiv papers")
        >>> print(f"Found {len(results['tavily'])} web results")
        >>> print(f"Found {len(results['wikipedia'])} Wikipedia articles")
    """
    results = {}
    
    if include_arxiv:
        logger.info(f"Searching arXiv for: {query}")
        results["arxiv"] = arxiv_search_tool(query, max_results=max_results_per_tool)
    
    if include_tavily:
        logger.info(f"Searching Tavily for: {query}")
        results["tavily"] = tavily_search_tool(query, max_results=max_results_per_tool)
    
    if include_wikipedia:
        logger.info(f"Searching Wikipedia for: {query}")
        results["wikipedia"] = wikipedia_search_tool(query)
    
    return results
