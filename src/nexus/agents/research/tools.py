import os
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from tavily import TavilyClient
import wikipedia
import json
from typing import Optional

# Load environment variables
load_dotenv()

# --- Tool Implementations ---

def arxiv_search_tool(query: str, max_results: int = 5) -> list[dict]:
    """
    Searches arXiv for research papers matching the given query.
    
    This tool searches the arXiv repository for academic papers in physics,
    mathematics, computer science, quantitative biology, quantitative finance,
    statistics, electrical engineering, systems science, and economics.
    
    Args:
        query: Search keywords or phrases for research papers. Can include
            author names, paper titles, or topic keywords. Examples:
            - "quantum entanglement"
            - "author:Einstein"
            - "neural networks deep learning"
        max_results: Maximum number of papers to return. Default is 5.
            Valid range: 1-100.
    
    Returns:
        List of dictionaries, each containing:
            - title (str): Paper title
            - authors (list[str]): List of author names
            - published (str): Publication date in YYYY-MM-DD format
            - url (str): URL to the paper's abstract page
            - summary (str): Paper abstract/summary
            - link_pdf (str | None): Direct link to PDF, if available
        
        Returns list with single error dict on failure:
            - error (str): Error message describing what went wrong
    
    Example:
        >>> results = arxiv_search_tool("quantum computing", max_results=3)
        >>> print(results[0]["title"])
        'Quantum Computing: A Gentle Introduction'
        >>> print(results[0]["authors"])
        ['Eleanor Rieffel', 'Wolfgang Polak']
    
    Note:
        - Results are ordered by relevance (arXiv's default ranking)
        - Abstracts are returned in full (not truncated)
        - Use specific keywords for better results
    """
    url = f"https://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    
    # Set user-agent for requests to arXiv
    headers = {
        "User-Agent": "Agentic-AI-Lab/1.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=60)
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


def tavily_search_tool(query: str, max_results: int = 5, include_images: bool = False) -> list[dict]:
    """
    Perform a general-purpose web search using the Tavily API.
    
    This tool searches the web for current information, news, articles, and
    general knowledge. It's ideal for finding recent events, product information,
    company details, or any information not available in academic databases.
    
    Args:
        query: Search keywords or natural language query. Examples:
            - "latest developments in AI regulation"
            - "SpaceX Starship launch schedule 2024"
            - "best practices for Python async programming"
        max_results: Maximum number of search results to return. Default is 5.
            Valid range: 1-20.
        include_images: If True, also returns image URLs related to the query.
            Default is False.
    
    Returns:
        List of dictionaries containing search results:
            - title (str): Title of the web page or article
            - content (str): Relevant excerpt or snippet from the page
            - url (str): URL to the source page
        
        If include_images=True, also includes:
            - image_url (str): URL to relevant images
        
        Returns list with single error dict on failure:
            - error (str): Error message (e.g., missing API key, network error)
    
    Example:
        >>> results = tavily_search_tool("climate change solutions", max_results=3)
        >>> print(results[0]["title"])
        'Top 10 Solutions to Climate Change'
        >>> print(results[0]["url"])
        'https://example.com/climate-solutions'
    
    Note:
        - Requires TAVILY_API_KEY environment variable
        - Optionally uses DLAI_TAVILY_BASE_URL for custom API endpoint
        - Results are optimized for relevance and recency
        - Content snippets are typically 200-500 characters
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return [{"error": "TAVILY_API_KEY not found in environment variables."}]

    api_base_url = os.getenv("DLAI_TAVILY_BASE_URL")
    
    try:
        client = TavilyClient(api_key=api_key, api_base_url=api_base_url)
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
        return [{"error": str(e)}]


def wikipedia_search_tool(query: str, sentences: int = 5) -> list[dict]:
    """
    Searches Wikipedia for a summary of the given query.
    
    This tool retrieves concise summaries from Wikipedia articles, ideal for
    getting background information, definitions, historical context, or general
    knowledge about people, places, concepts, or events.
    
    Args:
        query: Search term for the Wikipedia article. Can be:
            - A specific article title: "Albert Einstein"
            - A general topic: "machine learning"
            - A concept: "photosynthesis"
            - A place: "Tokyo"
        sentences: Number of sentences to include in the summary. Default is 5.
            Valid range: 1-10. Longer summaries provide more context but may
            be less focused.
    
    Returns:
        List with a single dictionary containing:
            - title (str): The actual Wikipedia article title (may differ from query)
            - summary (str): Article summary with the requested number of sentences
            - url (str): Full URL to the Wikipedia article
        
        Returns list with single error dict on failure:
            - error (str): Error message (e.g., "No results found", "Page not found")
    
    Example:
        >>> results = wikipedia_search_tool("Python programming", sentences=3)
        >>> print(results[0]["title"])
        'Python (programming language)'
        >>> print(results[0]["summary"][:100])
        'Python is a high-level, general-purpose programming language...'
    
    Note:
        - Automatically handles disambiguation pages by selecting the first option
        - Returns the most relevant article if multiple matches exist
        - Summaries are extracted from the article's introduction
        - For ambiguous queries, consider being more specific
    """
    try:
        results = wikipedia.search(query)
        if not results:
            return [{"error": "No results found on Wikipedia."}]
            
        page_title = results[0]
        # Handle potential disambiguation or page load errors
        try:
            page = wikipedia.page(page_title, auto_suggest=False)
        except wikipedia.DisambiguationError as e:
            page = wikipedia.page(e.options[0], auto_suggest=False)
        except wikipedia.PageError:
            return [{"error": f"Page '{page_title}' not found."}]
            
        summary = wikipedia.summary(page_title, sentences=sentences)

        return [{
            "title": page.title,
            "summary": summary,
            "url": page.url
        }]
    except Exception as e:
        return [{"error": str(e)}]


def europe_pmc_search_tool(query: str, max_results: int = 5) -> list[dict]:
    """
    Searches Europe PMC for life science and biomedical research literature.
    
    This tool searches Europe PMC, which aggregates content from multiple sources
    including PubMed, PubMed Central, bioRxiv, medRxiv, and other preprint servers.
    It's ideal for finding medical research, clinical studies, biological research,
    pharmaceutical studies, and health-related publications.
    
    Args:
        query: Search keywords for biomedical literature. Can include:
            - Disease names: "Alzheimer's disease"
            - Drug names: "aspirin cardiovascular"
            - Biological processes: "CRISPR gene editing"
            - Author names: "author:Smith"
            - MeSH terms: "diabetes mellitus type 2"
        max_results: Maximum number of papers to return. Default is 5.
            Valid range: 1-100.
    
    Returns:
        List of dictionaries, each containing:
            - title (str): Paper or article title
            - authors (str): Comma-separated list of author names
            - journal (str): Journal name where published
            - pub_year (str): Publication year
            - source (str): Source database code:
                * 'MED' = PubMed
                * 'PMC' = PubMed Central
                * 'PPR' = Preprint (bioRxiv, medRxiv, etc.)
                * 'AGR' = Agricultural research
                * 'CBA' = Chinese Biological Abstracts
            - url (str): Direct link to the article on Europe PMC
            - abstract (str): Paper abstract (truncated to ~500 characters)
        
        Returns list with single error dict on failure:
            - error (str): Error message describing what went wrong
    
    Example:
        >>> results = europe_pmc_search_tool("mRNA vaccine COVID-19", max_results=3)
        >>> print(results[0]["title"])
        'Efficacy of mRNA vaccines against SARS-CoV-2'
        >>> print(results[0]["source"])
        'MED'
        >>> print(results[0]["journal"])
        'Nature Medicine'
    
    Note:
        - Covers both peer-reviewed publications and preprints
        - Results include papers from the last several decades
        - Abstracts are truncated; use the URL for full text
        - No API key required (public API)
        - Particularly strong for recent biomedical research
    """
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": query,
        "format": "json",
        "pageSize": max_results,
        "resultType": "core"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("resultList", {}).get("result", []):
            results.append({
                "title": item.get("title", ""),
                "authors": item.get("authorString", ""),
                "journal": item.get("journalTitle", ""),
                "pub_year": item.get("pubYear", ""),
                "source": item.get("source", ""),  # e.g. MED (PubMed), PPR (Preprint)
                "url": f"https://europepmc.org/article/{item.get('source', '')}/{item.get('id', '')}",
                "abstract": item.get("abstractText", "No abstract available.")[:500] + "..."
            })
            
        return results
    
    except requests.exceptions.RequestException as e:
        return [{"error": f"Europe PMC API request failed: {str(e)}"}]
    except Exception as e:
        return [{"error": f"Europe PMC search failed: {str(e)}"}]


def reddit_search_tool(query: str, subreddit: str | None = None, max_results: int = 10, sort: str = "relevance") -> list[dict]:
    """
    Searches Reddit for discussions, insights, and community perspectives.
    
    This tool searches Reddit, which is excellent for finding:
    - Cutting-edge technology discussions (AGI, AI safety, emerging tech)
    - Community insights and real-world experiences
    - Speculative and experimental topics
    - Technical deep-dives and explanations
    - Niche and non-mainstream subjects
    
    Particularly useful for topics like:
    - AGI and superintelligence (/r/singularity, /r/artificial)
    - AI safety and alignment (/r/ControlProblem)
    - Machine learning discussions (/r/MachineLearning)
    - Futurism and emerging tech (/r/Futurology)
    - Fringe science and speculation (/r/HighStrangeness)
    
    Args:
        query: Search keywords. Examples:
            - "AGI consciousness debate"
            - "fractal neural networks"
            - "sentient AI ethics"
        subreddit: Optional subreddit to restrict search to (e.g., "singularity")
        max_results: Maximum number of posts to return. Default is 10.
        sort: Sort order - "relevance", "hot", "top", "new". Default is "relevance".
    
    Returns:
        List of dictionaries, each containing:
            - title (str): Post title
            - author (str): Reddit username
            - subreddit (str): Subreddit name
            - score (int): Upvote score
            - num_comments (int): Number of comments
            - url (str): URL to the Reddit post
            - selftext (str): Post body text (if text post)
            - created_utc (float): Unix timestamp of creation
        
        Returns list with single error dict on failure.
    
    Example:
        >>> results = reddit_search_tool("AGI safety", subreddit="singularity")
        >>> print(results[0]["title"])
        'New developments in AGI alignment research'
    
    Note:
        - Uses Reddit's JSON API (no authentication required for read-only)
        - Results include both posts and their metadata
        - Useful for gauging community sentiment and finding discussions
    """
    try:
        # Build URL
        if subreddit:
            url = f"https://www.reddit.com/r/{subreddit}/search.json"
        else:
            url = "https://www.reddit.com/search.json"
        
        # Parameters
        params = {
            "q": query,
            "limit": max_results,
            "sort": sort,
            "raw_json": 1  # Prevent HTML encoding
        }
        
        if subreddit:
            params["restrict_sr"] = "on"
        
        # Make request
        headers = {"User-Agent": "Nexus Research Agent/1.0"}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse results
        results = []
        for post in data.get("data", {}).get("children", []):
            post_data = post.get("data", {})
            results.append({
                "title": post_data.get("title", ""),
                "author": post_data.get("author", ""),
                "subreddit": post_data.get("subreddit", ""),
                "score": post_data.get("score", 0),
                "num_comments": post_data.get("num_comments", 0),
                "url": f"https://www.reddit.com{post_data.get('permalink', '')}",
                "selftext": post_data.get("selftext", "")[:500],  # Limit text length
                "created_utc": post_data.get("created_utc", 0)
            })
        
        if not results:
            return [{"message": "No Reddit posts found for the given query."}]
        
        return results
    
    except requests.exceptions.RequestException as e:
        return [{"error": f"Reddit API request failed: {str(e)}"}]
    except Exception as e:
        return [{"error": f"Reddit search failed: {str(e)}"}]


def semantic_scholar_search_tool(query: str, max_results: int = 10, fields: Optional[list[str]] = None) -> list[dict]:
    """
    Searches Semantic Scholar for academic papers using AI-powered relevance.
    
    Semantic Scholar is an AI-powered research tool that:
    - Finds papers across all scientific disciplines
    - Uses machine learning to rank by relevance
    - Provides citation context and influence metrics
    - Covers papers that might not be in arXiv
    - Includes preprints, conference papers, and journals
    
    Particularly strong for:
    - Computer science and AI research
    - Cross-disciplinary connections
    - Finding influential papers
    - Recent preprints and working papers
    - Papers with high citation counts
    
    Args:
        query: Search keywords. Examples:
            - "transformer architecture attention mechanism"
            - "fractal dimension machine learning"
            - "consciousness artificial intelligence"
        max_results: Maximum number of papers to return. Default is 10.
        fields: Optional list of fields to include. If None, uses default set.
            Available: title, authors, year, abstract, citationCount, 
            influentialCitationCount, url, venue, publicationTypes
    
    Returns:
        List of dictionaries, each containing:
            - paperId (str): Semantic Scholar paper ID
            - title (str): Paper title
            - authors (list[dict]): Author information with names and IDs
            - year (int): Publication year
            - abstract (str): Paper abstract
            - citationCount (int): Number of citations
            - influentialCitationCount (int): Number of influential citations
            - url (str): URL to Semantic Scholar page
            - venue (str): Publication venue (journal/conference)
            - publicationTypes (list[str]): Types (e.g., JournalArticle, Conference)
        
        Returns list with single error dict on failure.
    
    Example:
        >>> results = semantic_scholar_search_tool("neural architecture search")
        >>> print(results[0]["title"])
        >>> print(f"Citations: {results[0]['citationCount']}")
    
    Note:
        - Free API with generous rate limits
        - Results ranked by AI-powered relevance
        - Includes citation metrics for assessing impact
    """
    try:
        # Default fields if not specified
        if fields is None:
            fields = [
                "paperId", "title", "authors", "year", "abstract",
                "citationCount", "influentialCitationCount", 
                "url", "venue", "publicationTypes"
            ]
        
        # API endpoint
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        
        # Parameters
        params = {
            "query": query,
            "limit": max_results,
            "fields": ",".join(fields)
        }
        
        # Make request
        headers = {"User-Agent": "Nexus Research Agent/1.0"}
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse results
        papers = data.get("data", [])
        
        if not papers:
            return [{"message": "No papers found for the given query."}]
        
        # Format results
        results = []
        for paper in papers:
            # Extract author names
            authors = [
                {"name": author.get("name", "Unknown"), "authorId": author.get("authorId")}
                for author in paper.get("authors", [])
            ]
            
            results.append({
                "paperId": paper.get("paperId", ""),
                "title": paper.get("title", ""),
                "authors": authors,
                "year": paper.get("year"),
                "abstract": paper.get("abstract", "")[:1000] if paper.get("abstract") else None,  # Limit length
                "citationCount": paper.get("citationCount", 0),
                "influentialCitationCount": paper.get("influentialCitationCount", 0),
                "url": paper.get("url", ""),
                "venue": paper.get("venue", ""),
                "publicationTypes": paper.get("publicationTypes", [])
            })
        
        return results
    
    except requests.exceptions.RequestException as e:
        return [{"error": f"Semantic Scholar API request failed: {str(e)}"}]
    except Exception as e:
        return [{"error": f"Semantic Scholar search failed: {str(e)}"}]


# --- Tool Definitions (Schemas) ---

arxiv_tool_def = {
    "type": "function",
    "function": {
        "name": "arxiv_search_tool",
        "description": "Searches arXiv for research papers in physics, math, CS, and related fields.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords for research papers."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of papers to return.",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}

reddit_tool_def = {
    "type": "function",
    "function": {
        "name": "reddit_search_tool",
        "description": "Searches Reddit for discussions, community insights, and cutting-edge topics (AGI, AI safety, experimental tech, fringe science).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords for Reddit discussions."
                },
                "subreddit": {
                    "type": ["string", "null"],
                    "description": "Optional subreddit to search within (e.g., 'singularity', 'MachineLearning'). Leave null to search all subreddits."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of posts to return.",
                    "default": 10
                },
                "sort": {
                    "type": "string",
                    "description": "Sort order: 'relevance', 'hot', 'top', 'new'.",
                    "default": "relevance"
                }
            },
            "required": ["query"]
        }
    }
}

semantic_scholar_tool_def = {
    "type": "function",
    "function": {
        "name": "semantic_scholar_search_tool",
        "description": "Searches Semantic Scholar for academic papers using AI-powered relevance ranking. Covers all disciplines with citation metrics.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords for academic papers."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of papers to return.",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    }
}

europe_pmc_tool_def = {
    "type": "function",
    "function": {
        "name": "europe_pmc_search_tool",
        "description": "Searches biomedical literature (PubMed, bioRxiv, medRxiv) via Europe PMC.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords for biomedical papers."
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

# Tool mapping for execution
tool_mapping = {
    "tavily_search_tool": tavily_search_tool,
    "arxiv_search_tool": arxiv_search_tool,
    "wikipedia_search_tool": wikipedia_search_tool,
    "europe_pmc_search_tool": europe_pmc_search_tool,
    "reddit_search_tool": reddit_search_tool,
    "semantic_scholar_search_tool": semantic_scholar_search_tool
}

# List of callables for aisuite
aisuite_tools = [
    arxiv_search_tool, 
    tavily_search_tool, 
    wikipedia_search_tool, 
    europe_pmc_search_tool,
    reddit_search_tool,
    semantic_scholar_search_tool
]

# List of definitions for Responses API (GPT-5)
responses_tool_defs = [
    arxiv_tool_def, 
    tavily_tool_def, 
    wikipedia_tool_def, 
    europe_pmc_tool_def,
    reddit_tool_def,
    semantic_scholar_tool_def
]
