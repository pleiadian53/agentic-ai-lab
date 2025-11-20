"""
Configuration and path management for Splice Agent API.

Centralizes all path resolution and configuration settings.
"""

from pathlib import Path
from typing import Optional

# Project structure
# agentic-ai-lab/
# ├── splice_agent/
# │   └── server/
# │       ├── config.py (this file)
# │       └── splice_service.py
# └── data/

# Resolve project root (3 levels up from this file)
SERVER_DIR = Path(__file__).parent  # splice_agent/server/
SPLICE_AGENT_DIR = SERVER_DIR.parent  # splice_agent/
PROJECT_ROOT = SPLICE_AGENT_DIR.parent  # agentic-ai-lab/

# Key directories
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output" / "splice_charts"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def resolve_dataset_path(dataset_path: str) -> Path:
    """
    Resolve dataset path to absolute path.
    
    If the path is relative, it's resolved from PROJECT_ROOT.
    If the path is absolute, it's used as-is.
    
    Args:
        dataset_path: Relative or absolute path to dataset
        
    Returns:
        Absolute Path object
        
    Examples:
        >>> resolve_dataset_path("data/splice_sites.tsv")
        PosixPath('/path/to/project/data/splice_sites.tsv')
        
        >>> resolve_dataset_path("/absolute/path/data.csv")
        PosixPath('/absolute/path/data.csv')
    """
    path = Path(dataset_path)
    
    if path.is_absolute():
        return path
    else:
        return PROJECT_ROOT / path


def get_available_datasets() -> list[dict]:
    """
    Scan DATA_DIR for available datasets.
    
    Returns:
        List of dataset metadata dictionaries with keys:
        - path: Relative path from project root
        - name: Dataset name (stem)
        - size_mb: File size in megabytes
        - format: File extension (.tsv, .csv)
    """
    datasets = []
    
    if not DATA_DIR.exists():
        return datasets
    
    # Scan for TSV files
    for file in DATA_DIR.glob("**/*.tsv"):
        datasets.append({
            "path": str(file.relative_to(PROJECT_ROOT)),
            "name": file.stem,
            "size_mb": file.stat().st_size / (1024 * 1024),
            "format": ".tsv"
        })
    
    # Scan for CSV files
    for file in DATA_DIR.glob("**/*.csv"):
        datasets.append({
            "path": str(file.relative_to(PROJECT_ROOT)),
            "name": file.stem,
            "size_mb": file.stat().st_size / (1024 * 1024),
            "format": ".csv"
        })
    
    return datasets


def get_output_path(filename: str) -> Path:
    """
    Get absolute path for output file.
    
    Args:
        filename: Output filename (e.g., "chart_1234.pdf")
        
    Returns:
        Absolute path in OUTPUT_DIR
    """
    return OUTPUT_DIR / filename


# API Configuration
DEFAULT_MODEL = "gpt-4o-mini"
SUPPORTED_FORMATS = [".tsv", ".csv"]
SUPPORTED_OUTPUT_FORMATS = ["pdf", "png"]

# CORS Configuration
CORS_ORIGINS = ["*"]  # Configure appropriately for production
CORS_ALLOW_CREDENTIALS = True

# Server Configuration
HOST = "0.0.0.0"
PORT = 8004  # Different from chart_agent (8003)
RELOAD = True  # Enable auto-reload in development


# Display configuration on import (for debugging)
if __name__ == "__main__":
    print("Splice Agent API Configuration")
    print("=" * 50)
    print(f"Project Root:     {PROJECT_ROOT}")
    print(f"Splice Agent Dir: {SPLICE_AGENT_DIR}")
    print(f"Server Dir:       {SERVER_DIR}")
    print(f"Data Dir:         {DATA_DIR}")
    print(f"Output Dir:       {OUTPUT_DIR}")
    print(f"\nAvailable Datasets: {len(get_available_datasets())}")
    for ds in get_available_datasets():
        print(f"  - {ds['name']} ({ds['size_mb']:.2f} MB)")
