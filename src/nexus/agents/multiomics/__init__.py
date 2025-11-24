"""
Multiomics Agent
================

Comprehensive analysis of genomic, transcriptomic, and proteomic data.

Sub-Agents:
    - Splice Agent: RNA splicing prediction using OpenSpliceAI and other models
    - Variant Agent: Genetic variant analysis and interpretation
    - Expression Agent: Gene expression analysis and differential expression

This agent coordinates specialized sub-agents for different aspects of
multiomics analysis, enabling comprehensive biological insights.

Example:
    >>> from nexus.agents.multiomics import MultiomicsAgent
    >>> agent = MultiomicsAgent()
    >>> result = agent.analyze(
    ...     data_type="rna_seq",
    ...     task="splice_prediction",
    ...     sequence="ATCG..."
    ... )
"""

__all__ = ["MultiomicsAgent"]
