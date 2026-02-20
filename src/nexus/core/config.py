"""
Nexus Configuration Management
===============================

Centralized configuration for all Nexus components.
"""

import os
from pathlib import Path
from typing import Optional

from agentic_core.paths import find_project_root, PROJECT_ROOT, DATA_DIR, OUTPUT_DIR


class NexusConfig:
    """Global configuration for Nexus platform."""
    
    # Base paths (from agentic_core.paths)
    ROOT_DIR = PROJECT_ROOT
    SRC_DIR = ROOT_DIR / "src"
    NEXUS_DIR = SRC_DIR / "nexus"
    OUTPUT_DIR = OUTPUT_DIR
    DATA_DIR = DATA_DIR
    
    # Research outputs (standardized path)
    RESEARCH_REPORTS_DIR = OUTPUT_DIR / "research_reports"
    
    # Template paths
    TEMPLATE_DIR = NEXUS_DIR / "templates"
    TEMPLATE_PAPERS_DIR = TEMPLATE_DIR / "papers"
    TEMPLATE_METADATA_DIR = TEMPLATE_DIR / "metadata"
    
    # Knowledge paths
    KNOWLEDGE_DIR = OUTPUT_DIR / "knowledge"
    KNOWLEDGE_GRAPH_PATH = KNOWLEDGE_DIR / "graph.db"

    # OpenClaw workspace root.
    # Override with OPENCLAW_WORKSPACE to point at a different installation prefix
    # (e.g. a shared network mount or a non-default install path) while keeping the
    # sub-directory structure identical across all users.
    OPENCLAW_WORKSPACE: Path = Path(
        os.getenv("OPENCLAW_WORKSPACE", str(Path.home() / ".openclaw" / "workspace"))
    )

    # Personal knowledge base (shared with OpenClaw/Lyra when available).
    # Resolution order (highest to lowest priority):
    #   1. NEXUS_KB_PATH  — full path override (power users / CI)
    #   2. OPENCLAW_WORKSPACE — prefix override; appends the standard sub-path
    #   3. Default: ~/.openclaw/workspace/knowledge/agentic-ai-lab/kb
    KB_DIR: Path = Path(
        os.getenv(
            "NEXUS_KB_PATH",
            str(
                Path(os.getenv("OPENCLAW_WORKSPACE", str(Path.home() / ".openclaw" / "workspace")))
                / "knowledge"
                / "agentic-ai-lab"
                / "kb"
            ),
        )
    )
    
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
