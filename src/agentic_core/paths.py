"""
Project Path Resolution & Environment Loading
===============================================

Centralized, robust path management for the agentic-ai-lab project.
Any sub-project (rag/, tool_use/, multiagent/, etc.) can import from here
instead of hand-coding fragile relative paths.

Usage:
    from agentic_core.paths import load_project_env, PROJECT_ROOT, DATA_DIR

    # Load .env from project root (call once at entry point)
    load_project_env()

    # Use resolved paths
    my_data = DATA_DIR / "my_dataset.csv"
"""

import os
from pathlib import Path
from typing import Optional


def find_project_root(marker_name: str = "agentic-ai-lab") -> Path:
    """
    Find the project root by walking up from this file's location.

    Strategy:
        1. Look for a parent directory whose name matches *marker_name*.
        2. Fallback: look for common project markers (.git, pyproject.toml).

    Args:
        marker_name: Expected name of the project root directory.

    Returns:
        Resolved Path to the project root.

    Raises:
        RuntimeError: If the root cannot be determined.
    """
    current = Path(__file__).resolve()

    # Primary: match by directory name
    for parent in [current] + list(current.parents):
        if parent.name == marker_name:
            return parent

    # Fallback: common project-root markers
    for parent in [current] + list(current.parents):
        if any((parent / m).exists() for m in (".git", "pyproject.toml", "setup.py")):
            return parent

    raise RuntimeError(
        f"Could not find project root. Expected directory named '{marker_name}' "
        f"or a directory containing .git, pyproject.toml, or setup.py"
    )


# ---------------------------------------------------------------------------
# Resolved constants — available immediately on import
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = find_project_root()

SRC_DIR:    Path = PROJECT_ROOT / "src"
DATA_DIR:   Path = PROJECT_ROOT / "data"
OUTPUT_DIR: Path = PROJECT_ROOT / "output"

ENV_FILE:   Path = PROJECT_ROOT / ".env"


# ---------------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------------

def load_project_env(override: bool = False) -> bool:
    """
    Load the project-level ``.env`` file into ``os.environ``.

    This is a thin wrapper around ``python-dotenv`` that always resolves
    the ``.env`` relative to the project root — no manual path math needed.

    Args:
        override: If True, .env values overwrite existing env vars.

    Returns:
        True if the .env file was found and loaded, False otherwise.
    """
    from dotenv import load_dotenv
    return load_dotenv(ENV_FILE, override=override)


def get_subproject_dir(name: str) -> Path:
    """
    Return the path to a top-level sub-project directory.

    Args:
        name: Sub-project name (e.g. "rag", "multiagent", "tool_use").

    Returns:
        Resolved Path (directory may not exist yet).
    """
    return PROJECT_ROOT / name
