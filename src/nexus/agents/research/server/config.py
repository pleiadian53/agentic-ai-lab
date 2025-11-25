"""
Configuration and path management for Research Agent API.

Centralizes all path resolution and configuration settings.
Uses NexusConfig for consistent path management across the platform.
"""

from pathlib import Path
from typing import Optional
import os

from nexus.core.config import NexusConfig

# Use Nexus centralized configuration
PROJECT_ROOT = NexusConfig.ROOT_DIR
SERVER_DIR = Path(__file__).parent
RESEARCH_AGENT_DIR = SERVER_DIR.parent

# Key directories - use standardized output structure
OUTPUT_DIR = NexusConfig.RESEARCH_REPORTS_DIR  # output/research_reports (standardized)
STATIC_DIR = SERVER_DIR / "static"
TEMPLATES_DIR = SERVER_DIR / "templates"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


def get_output_path(topic: str, filename: str) -> Path:
    """
    Get absolute path for output file under topic directory.
    
    Args:
        topic: Research topic (used as subdirectory name)
        filename: Output filename (e.g., "report.md", "references.json")
        
    Returns:
        Absolute path in OUTPUT_DIR/<topic>/
    """
    topic_dir = OUTPUT_DIR / topic
    topic_dir.mkdir(parents=True, exist_ok=True)
    return topic_dir / filename


def get_available_reports() -> list[dict]:
    """
    Scan OUTPUT_DIR for available research reports.
    
    Returns:
        List of report metadata dictionaries with keys:
        - topic: Research topic (directory name)
        - report_path: Path to the markdown report
        - pdf_path: Path to the PDF report (if exists)
        - created: Creation timestamp
        - size_kb: File size in kilobytes
    """
    reports = []
    
    if not OUTPUT_DIR.exists():
        return reports
    
    # Scan for markdown reports in topic directories
    for topic_dir in OUTPUT_DIR.iterdir():
        if not topic_dir.is_dir():
            continue
            
        # Look for markdown files
        for md_file in topic_dir.glob("*.md"):
            # Check if corresponding PDF exists
            pdf_file = md_file.with_suffix('.pdf')
            pdf_path = str(pdf_file.relative_to(OUTPUT_DIR)) if pdf_file.exists() else None
            
            reports.append({
                "topic": topic_dir.name,
                "report_path": str(md_file.relative_to(OUTPUT_DIR)),
                "pdf_path": pdf_path,
                "created": md_file.stat().st_mtime,
                "size_kb": md_file.stat().st_size / 1024
            })
    
    # Sort by creation time (newest first)
    reports.sort(key=lambda x: x["created"], reverse=True)
    
    return reports


# API Configuration
DEFAULT_MODEL = "openai:gpt-4o-mini"
SUPPORTED_MODELS = [
    "openai:gpt-4o-mini",
    "openai:gpt-4o",
    "openai:o4-mini",
    "openai:gpt-5.1-codex-mini"
]

# CORS Configuration
CORS_ORIGINS = ["*"]  # Configure appropriately for production
CORS_ALLOW_CREDENTIALS = True

# Server Configuration
HOST = "0.0.0.0"
PORT = 8004  # Different from chart_agent (8003)
RELOAD = True  # Enable auto-reload in development


# Display configuration on import (for debugging)
if __name__ == "__main__":
    print("Research Agent API Configuration")
    print("=" * 50)
    print(f"Project Root:        {PROJECT_ROOT}")
    print(f"Research Agent Dir:  {RESEARCH_AGENT_DIR}")
    print(f"Server Dir:          {SERVER_DIR}")
    print(f"Output Dir:          {OUTPUT_DIR}")
    print(f"Templates Dir:       {TEMPLATES_DIR}")
    print(f"\nAvailable Reports: {len(get_available_reports())}")
    for report in get_available_reports()[:5]:  # Show first 5
        print(f"  - {report['topic']} ({report['size_kb']:.2f} KB)")
