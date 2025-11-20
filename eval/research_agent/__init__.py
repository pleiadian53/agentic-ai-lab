"""
Enhanced Research Agent with Integrated Evaluation

This package combines the research agent from tool_use/research_agent with
component-wise evaluation from the eval package to improve research quality.

Key Features:
- Research report generation with tool use
- Component-wise source evaluation
- Reflection and rewriting with quality checks
- HTML/PDF conversion
- Comprehensive evaluation metrics

Usage:
    from eval.research_agent import EvaluatedResearchAgent
    
    agent = EvaluatedResearchAgent(
        preferred_domains=ACADEMIC_DOMAINS,
        min_source_ratio=0.5
    )
    
    results = agent.run_workflow("quantum computing research")
"""

from .agent import EvaluatedResearchAgent
from .workflow import run_evaluated_workflow

__all__ = [
    "EvaluatedResearchAgent",
    "run_evaluated_workflow",
]
