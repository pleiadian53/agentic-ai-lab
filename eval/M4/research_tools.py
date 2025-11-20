# --- Standard library ---
import os
import xml.etree.ElementTree as ET

# --- Third-party ---
import requests
from dotenv import load_dotenv
from tavily import TavilyClient
import wikipedia

# Init env
load_dotenv()  # load variables 

# Set user-agent for requests to arXiv
session = requests.Session()
session.headers.update({
    "User-Agent": "LF-ADP-Agent/1.0 (mailto:your.email@example.com)"
})

def arxiv_search_tool(query: str, max_results: int = 5) -> list[dict]:
    """
    Searches arXiv for research papers using flexible keyword matching.
    
    Supports loose queries across title, abstract, authors, and full text.
    The search is relevance-based, not exact match, so general topics like
    "quantum computing" or "black holes" work well. Also supports advanced
    operators like "author:Einstein" or boolean "quantum AND computing".
    
    Args:
        query: Search keywords or phrases. Can be general topics, specific terms,
               or author names. Examples:
               - "quantum entanglement"
               - "author:Hawking black holes"
               - "neural networks AND physics"
        max_results: Maximum number of papers to return (default: 5).
    
    Returns:
        List of paper dictionaries with keys: title, authors, published,
        url, summary, link_pdf. Returns [{"error": ...}] on failure.
    """
    url = f"https://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"

    try:
        response = session.get(url, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return [{"error": str(e)}]

    try:
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        results = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text.strip()
            authors = [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)]
            published = entry.find('atom:published', ns).text[:10]
            url_abstract = entry.find('atom:id', ns).text
            summary = entry.find('atom:summary', ns).text.strip()

            link_pdf = None
            for link in entry.findall('atom:link', ns):
                if link.attrib.get('title') == 'pdf':
                    link_pdf = link.attrib.get('href')
                    break

            results.append({
                "title": title,
                "authors": authors,
                "published": published,
                "url": url_abstract,
                "summary": summary,
                "link_pdf": link_pdf
            })

        return results
    except Exception as e:
        return [{"error": f"Parsing failed: {str(e)}"}]


arxiv_tool_def = {
    "type": "function",
    "function": {
        "name": "arxiv_search_tool",
        "description": "Searches for research papers on arXiv by query string.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords for research papers."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return.",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}



def tavily_search_tool(query: str, max_results: int = 5, include_images: bool = False) -> list[dict]:
    """
    Performs a general-purpose web search using the Tavily API.
    
    Use this tool for current events, news, general information, and topics
    not covered by academic sources. Tavily provides high-quality, curated
    web results with content snippets. Ideal for recent developments,
    company information, product details, and real-world applications.

    Args:
        query: The search query. Can be questions ("What is quantum computing?")
               or keywords ("latest AI developments 2024").
        max_results: Number of web results to return (default: 5).
        include_images: Whether to include image URLs in results (default: False).

    Returns:
        List of result dictionaries with keys: title, content, url.
        If include_images=True, also includes {"image_url": ...} entries.
        Returns [{"error": ...}] on failure.
    """
    params = {}
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not found in environment variables.")
    params['api_key'] = api_key

    #client = TavilyClient(api_key)

    api_base_url = os.getenv("DLAI_TAVILY_BASE_URL")
    if api_base_url:
        params['api_base_url'] = api_base_url

    client = TavilyClient(api_key=api_key, api_base_url=api_base_url)

    try:
        response = client.search(
            query=query,
            max_results=max_results,
            include_images=include_images
        )

        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "content": r.get("content", ""),
                "url": r.get("url", "")
            })

        if include_images:
            for img_url in response.get("images", []):
                results.append({"image_url": img_url})

        return results

    except Exception as e:
        return [{"error": str(e)}]  # For LLM-friendly agents
    

tavily_tool_def = {
    "type": "function",
    "function": {
        "name": "tavily_search_tool",
        "description": "Performs a general-purpose web search using the Tavily API.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords for retrieving information from the web."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return.",
                    "default": 5
                },
                "include_images": {
                    "type": "boolean",
                    "description": "Whether to include image results.",
                    "default": False
                }
            },
            "required": ["query"]
        }
    }
}

## Wikipedia search tool

def wikipedia_search_tool(query: str, sentences: int = 5) -> list[dict]:
    """
    Searches Wikipedia for encyclopedic summaries and background information.
    
    Use this tool for well-established concepts, historical information,
    definitions, and general knowledge. Wikipedia provides reliable,
    comprehensive overviews of topics. Best for foundational understanding
    before diving into specialized sources.

    Args:
        query: Search query for Wikipedia. Works best with specific topics,
               people, places, or concepts. Examples:
               - "Quantum entanglement"
               - "Albert Einstein"
               - "CRISPR gene editing"
        sentences: Number of sentences to include in the summary (default: 5).
                   Use fewer (2-3) for brief overviews, more (7-10) for detail.

    Returns:
        List with a single dictionary containing keys: title, summary, url.
        Returns [{"error": ...}] if the topic is not found or ambiguous.
    """
    try:
        page_title = wikipedia.search(query)[0]
        page = wikipedia.page(page_title)
        summary = wikipedia.summary(page_title, sentences=sentences)

        return [{
            "title": page.title,
            "summary": summary,
            "url": page.url
        }]
    except Exception as e:
        return [{"error": str(e)}]

# Tool definition
wikipedia_tool_def = {
    "type": "function",
    "function": {
        "name": "wikipedia_search_tool",
        "description": "Searches for a Wikipedia article summary by query string.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords for the Wikipedia article."
                },
                "sentences": {
                    "type": "integer",
                    "description": "Number of sentences in the summary.",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}



# Tool mapping
tool_mapping = {
    "tavily_search_tool": tavily_search_tool,
    "arxiv_search_tool": arxiv_search_tool,
    "wikipedia_search_tool": wikipedia_search_tool
}