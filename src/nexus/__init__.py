"""
Nexus: Superintelligent Research Platform
==========================================

A unified platform for orchestrating multiple AI agents to conduct
scientific research, data analysis, and knowledge synthesis.

Agents:
    - Research Agent: Literature review and report generation
    - Chart Agent: Data visualization and analysis
    - SQL Agent: Database querying and data retrieval
    - Multiomics Agent: Genomic, transcriptomic, and proteomic analysis
        - Splice Agent: RNA splicing prediction (OpenSpliceAI, etc.)
        - Variant Agent: Genetic variant analysis
        - Expression Agent: Gene expression analysis
    - ML Agent: Machine learning and predictions
        - Splice Predictor: Per-nucleotide splice site scoring
        - Cancer Classifier: Cancer type classification
        - Drug Response: Drug response prediction
        - Custom Models: User-defined ML workflows
    - Email Agent: Communication and collaboration

Features:
    - Multi-agent orchestration
    - Paper-based style transfer
    - Knowledge graph integration
    - Experimental results aggregation
    - Unified CLI and Web UI

Example:
    >>> from nexus.agents.research import ResearchAgent
    >>> agent = ResearchAgent()
    >>> report = agent.generate("AI in drug discovery")
    
    >>> from nexus.workflows import DiscoveryPipeline
    >>> pipeline = DiscoveryPipeline()
    >>> result = pipeline.run(topic="Protein folding", agents=["research", "chart"])
"""

__version__ = "0.1.0"
__author__ = "Agentic AI Lab"

# Core imports
from nexus.core import config

# Version info
VERSION = __version__

__all__ = [
    "__version__",
    "VERSION",
    "config",
]
