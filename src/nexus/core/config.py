"""
Nexus Configuration Management
===============================

Centralized configuration for all Nexus components.
"""

import os
from pathlib import Path
from typing import Optional

def _find_project_root(marker_name: str = "agentic-ai-lab") -> Path:
    """
    Find project root by searching for a directory with the given name.
    
    This is more robust than counting parent directories, as it works
    regardless of where the code is located in the project structure.
    
    Args:
        marker_name: Name of the project root directory
        
    Returns:
        Path to project root
        
    Raises:
        RuntimeError: If project root cannot be found
    """
    current = Path(__file__).resolve()
    
    # Traverse up the directory tree
    for parent in [current] + list(current.parents):
        if parent.name == marker_name:
            return parent
    
    # Fallback: look for common project markers
    for parent in [current] + list(current.parents):
        # Check for common project root indicators
        if any((parent / marker).exists() for marker in ['.git', 'pyproject.toml', 'setup.py']):
            return parent
    
    raise RuntimeError(
        f"Could not find project root. Expected directory named '{marker_name}' "
        f"or a directory containing .git, pyproject.toml, or setup.py"
    )


class NexusConfig:
    """Global configuration for Nexus platform."""
    
    # Base paths
    ROOT_DIR = _find_project_root("agentic-ai-lab")
    SRC_DIR = ROOT_DIR / "src"
    NEXUS_DIR = SRC_DIR / "nexus"
    OUTPUT_DIR = ROOT_DIR / "output"  # Standardized output directory
    DATA_DIR = ROOT_DIR / "data"
    
    # Research outputs (standardized path)
    RESEARCH_REPORTS_DIR = OUTPUT_DIR / "research_reports"
    
    # Template paths
    TEMPLATE_DIR = NEXUS_DIR / "templates"
    TEMPLATE_PAPERS_DIR = TEMPLATE_DIR / "papers"
    TEMPLATE_METADATA_DIR = TEMPLATE_DIR / "metadata"
    
    # Knowledge paths
    KNOWLEDGE_DIR = OUTPUT_DIR / "knowledge"
    KNOWLEDGE_GRAPH_PATH = KNOWLEDGE_DIR / "graph.db"
    
    # API Keys (from environment)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    
    # Default model settings
    DEFAULT_MODEL = "openai:gpt-4o"
    DEFAULT_REPORT_LENGTH = "standard"
    MAX_TOKENS = 16000
    TEMPERATURE = 0.7
    
    # Orchestration settings
    MAX_PARALLEL_AGENTS = 3
    TIMEOUT_SECONDS = 600
    RETRY_ATTEMPTS = 3
    
    # Server settings
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 8000
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = OUTPUT_DIR / "logs"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        directories = [
            cls.OUTPUT_DIR,
            cls.RESEARCH_REPORTS_DIR,
            cls.KNOWLEDGE_DIR,
            cls.LOG_DIR,
            cls.TEMPLATE_PAPERS_DIR,
            cls.TEMPLATE_METADATA_DIR,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_output_path(cls, agent_name: str, filename: str) -> Path:
        """Get output path for an agent's file."""
        agent_dir = cls.OUTPUT_DIR / agent_name
        agent_dir.mkdir(parents=True, exist_ok=True)
        return agent_dir / filename


# Initialize directories on import
NexusConfig.ensure_directories()
