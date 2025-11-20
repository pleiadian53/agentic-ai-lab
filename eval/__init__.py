"""
Evaluation Package for Agentic AI Research Workflows

This package provides tools for evaluating the quality of sources
returned by research agents, with a focus on domain-based evaluation.

It also includes production-ready research tools (arXiv, Tavily, Wikipedia)
for integration with agentic workflows.
"""

from .domain_evaluator import (
    DomainEvaluator,
    evaluate_sources,
    extract_urls_from_text,
    SourceInfo,
)

from .metrics import (
    EvaluationResult,
    compute_domain_metrics,
)

from .config import (
    DEFAULT_PREFERRED_DOMAINS,
    ACADEMIC_DOMAINS,
    NEWS_DOMAINS,
    GOVERNMENT_DOMAINS,
    COMPUTATIONAL_BIOLOGY_DOMAINS,
    RNA_THERAPEUTICS_DOMAINS,
    GENOMICS_DOMAINS,
    BIOLOGY_FOCUSED_DOMAINS,
    get_domain_set,
    create_custom_domain_set,
)

# Research tools (production-ready)
from .research_tools import (
    arxiv_search_tool,
    tavily_search_tool,
    wikipedia_search_tool,
    search_all,
    get_tool,
    list_tools,
    get_tool_metadata,
    RESEARCH_TOOLS,
    TOOL_METADATA,
)

# Enhanced research agent with evaluation
from .research_agent import (
    EvaluatedResearchAgent,
    run_evaluated_workflow,
)

__version__ = "0.1.0"

__all__ = [
    # Core evaluation
    "DomainEvaluator",
    "evaluate_sources",
    "extract_urls_from_text",
    "SourceInfo",
    
    # Metrics
    "compute_domain_metrics",
    "EvaluationResult",
    
    # Configuration - General
    "DEFAULT_PREFERRED_DOMAINS",
    "ACADEMIC_DOMAINS",
    "NEWS_DOMAINS",
    "GOVERNMENT_DOMAINS",
    
    # Configuration - Biology/Life Sciences
    "COMPUTATIONAL_BIOLOGY_DOMAINS",
    "RNA_THERAPEUTICS_DOMAINS",
    "GENOMICS_DOMAINS",
    "BIOLOGY_FOCUSED_DOMAINS",
    
    # Configuration helpers
    "get_domain_set",
    "create_custom_domain_set",
    
    # Research tools
    "arxiv_search_tool",
    "tavily_search_tool",
    "wikipedia_search_tool",
    "search_all",
    "get_tool",
    "list_tools",
    "get_tool_metadata",
    "RESEARCH_TOOLS",
    "TOOL_METADATA",
    
    # Enhanced research agent
    "EvaluatedResearchAgent",
    "run_evaluated_workflow",
]
