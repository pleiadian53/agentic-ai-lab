"""
Domain evaluator for assessing source quality in research outputs.

This module provides tools to evaluate whether sources retrieved by
research agents come from preferred/trusted domains.
"""

import re
import json
import urllib.parse
from typing import Any
from dataclasses import dataclass

from .config import DEFAULT_PREFERRED_DOMAINS, DEFAULT_MIN_RATIO


@dataclass
class SourceInfo:
    """Information about a single source/URL."""
    url: str
    domain: str
    title: str | None = None
    is_preferred: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "domain": self.domain,
            "title": self.title,
            "is_preferred": self.is_preferred,
        }


def extract_domain(url: str) -> str:
    """
    Extract domain from URL, removing 'www.' prefix if present.
    
    Args:
        url: Full URL string
        
    Returns:
        Domain string (e.g., 'arxiv.org')
        
    Examples:
        >>> extract_domain('https://www.arxiv.org/abs/1234')
        'arxiv.org'
        >>> extract_domain('https://nature.com/articles/123')
        'nature.com'
    """
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.hostname or ""
        # Remove 'www.' prefix
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def extract_urls_from_text(text: str) -> list[str]:
    """
    Extract all URLs from plain text using regex.
    
    Args:
        text: Text content that may contain URLs
        
    Returns:
        List of URL strings
        
    Examples:
        >>> text = "Check https://arxiv.org and https://nature.com"
        >>> urls = extract_urls_from_text(text)
        >>> len(urls)
        2
    """
    url_pattern = re.compile(r'https?://[^\s\]\)>\}"\'\<]+', flags=re.IGNORECASE)
    return url_pattern.findall(text)


def is_domain_preferred(domain: str, preferred_domains: set[str]) -> bool:
    """
    Check if a domain matches any preferred domain.
    
    Supports exact matches and subdomain matches.
    
    Args:
        domain: Domain to check (e.g., 'arxiv.org')
        preferred_domains: Set of preferred domains
        
    Returns:
        True if domain is preferred
        
    Examples:
        >>> is_domain_preferred('arxiv.org', {'arxiv.org', 'nature.com'})
        True
        >>> is_domain_preferred('blog.example.com', {'example.com'})
        True
    """
    if not domain:
        return False
    
    # Check exact match
    if domain in preferred_domains:
        return True
    
    # Check if domain ends with any preferred domain (subdomain match)
    for preferred in preferred_domains:
        if domain.endswith(f".{preferred}") or domain == preferred:
            return True
    
    return False


class DomainEvaluator:
    """
    Evaluator for assessing source quality based on domain preferences.
    
    This class provides methods to evaluate research outputs by checking
    whether retrieved sources come from a predefined list of preferred domains.
    
    Attributes:
        preferred_domains: Set of preferred domain strings
        min_ratio: Minimum ratio of preferred sources required to pass
    
    Examples:
        >>> evaluator = DomainEvaluator()
        >>> result = evaluator.evaluate_text("Check https://arxiv.org/abs/1234")
        >>> result.passed
        True
    """
    
    def __init__(
        self,
        preferred_domains: set[str] | None = None,
        min_ratio: float = DEFAULT_MIN_RATIO
    ):
        """
        Initialize domain evaluator.
        
        Args:
            preferred_domains: Set of preferred domains (uses default if None)
            min_ratio: Minimum ratio of preferred sources (0.0-1.0)
        """
        self.preferred_domains = preferred_domains or DEFAULT_PREFERRED_DOMAINS.copy()
        self.min_ratio = min_ratio
    
    def evaluate_url(self, url: str, title: str | None = None) -> SourceInfo:
        """
        Evaluate a single URL.
        
        Args:
            url: URL to evaluate
            title: Optional title for the source
            
        Returns:
            SourceInfo object with evaluation results
        """
        domain = extract_domain(url)
        is_preferred = is_domain_preferred(domain, self.preferred_domains)
        
        return SourceInfo(
            url=url,
            domain=domain,
            title=title,
            is_preferred=is_preferred
        )
    
    def evaluate_urls(self, urls: list[str]) -> tuple[bool, dict]:
        """
        Evaluate a list of URLs.
        
        Args:
            urls: List of URL strings
            
        Returns:
            Tuple of (passed, results_dict) where:
                - passed: True if ratio >= min_ratio
                - results_dict: Dictionary with evaluation details
        """
        if not urls:
            return False, {
                "total": 0,
                "preferred": 0,
                "ratio": 0.0,
                "sources": [],
                "passed": False,
                "min_ratio": self.min_ratio,
            }
        
        sources = [self.evaluate_url(url) for url in urls]
        preferred_count = sum(1 for s in sources if s.is_preferred)
        ratio = preferred_count / len(sources)
        passed = ratio >= self.min_ratio
        
        return passed, {
            "total": len(sources),
            "preferred": preferred_count,
            "ratio": ratio,
            "sources": [s.to_dict() for s in sources],
            "passed": passed,
            "min_ratio": self.min_ratio,
        }
    
    def evaluate_text(self, text: str) -> "EvaluationResult":
        """
        Evaluate text by extracting and checking URLs.
        
        Args:
            text: Text content containing URLs
            
        Returns:
            EvaluationResult object
        """
        from .metrics import EvaluationResult
        
        urls = extract_urls_from_text(text)
        passed, results = self.evaluate_urls(urls)
        
        return EvaluationResult(
            passed=passed,
            total=results["total"],
            preferred=results["preferred"],
            ratio=results["ratio"],
            min_ratio=self.min_ratio,
            sources=results["sources"],
        )
    
    def evaluate_json(self, data: str | list | dict) -> "EvaluationResult":
        """
        Evaluate JSON data (e.g., from Tavily API).
        
        Handles multiple formats:
        - JSON string
        - List of dicts with 'url' key
        - Dict with 'results' key containing list
        
        Args:
            data: JSON data in various formats
            
        Returns:
            EvaluationResult object
        """
        from .metrics import EvaluationResult
        
        # Parse JSON string if needed
        if isinstance(data, str):
            data = data.strip()
            # Remove markdown code fences
            if data.startswith("```"):
                data = re.sub(r"^```(?:json|text)?\s*", "", data)
                data = re.sub(r"\s*```$", "", data)
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                # Fall back to text extraction
                return self.evaluate_text(data)
        
        # Extract URLs from structured data
        urls = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "url" in item:
                    urls.append(item["url"])
        elif isinstance(data, dict):
            if "results" in data and isinstance(data["results"], list):
                for item in data["results"]:
                    if isinstance(item, dict) and "url" in item:
                        urls.append(item["url"])
            elif "url" in data:
                urls.append(data["url"])
        
        if not urls:
            # Fall back to text extraction
            return self.evaluate_text(str(data))
        
        passed, results = self.evaluate_urls(urls)
        
        return EvaluationResult(
            passed=passed,
            total=results["total"],
            preferred=results["preferred"],
            ratio=results["ratio"],
            min_ratio=self.min_ratio,
            sources=results["sources"],
        )
    
    def evaluate(self, data: Any) -> "EvaluationResult":
        """
        Evaluate any type of input (auto-detect format).
        
        Args:
            data: Text, JSON string, list, or dict
            
        Returns:
            EvaluationResult object
        """
        if isinstance(data, str):
            # Try JSON first, fall back to text
            try:
                parsed = json.loads(data)
                return self.evaluate_json(parsed)
            except json.JSONDecodeError:
                return self.evaluate_text(data)
        elif isinstance(data, (list, dict)):
            return self.evaluate_json(data)
        else:
            return self.evaluate_text(str(data))


def evaluate_sources(
    data: Any,
    preferred_domains: set[str] | None = None,
    min_ratio: float = DEFAULT_MIN_RATIO
) -> "EvaluationResult":
    """
    Convenience function to evaluate sources.
    
    Args:
        data: Text, JSON, or structured data containing URLs
        preferred_domains: Set of preferred domains (uses default if None)
        min_ratio: Minimum ratio of preferred sources
        
    Returns:
        EvaluationResult object
        
    Examples:
        >>> result = evaluate_sources("Check https://arxiv.org/abs/1234")
        >>> result.passed
        True
    """
    evaluator = DomainEvaluator(preferred_domains, min_ratio)
    return evaluator.evaluate(data)
