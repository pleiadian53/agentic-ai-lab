"""
agentic_core — Shared infrastructure for the agentic-ai-lab project.

This package provides project-wide utilities (path resolution, environment
loading, etc.) that any sub-project can depend on without coupling to a
specific product like Nexus.

Typical usage:
    from agentic_core.paths import load_project_env, PROJECT_ROOT, DATA_DIR
"""

from agentic_core.paths import (
    find_project_root,
    load_project_env,
    get_subproject_dir,
    PROJECT_ROOT,
    SRC_DIR,
    DATA_DIR,
    OUTPUT_DIR,
    ENV_FILE,
)

__all__ = [
    "find_project_root",
    "load_project_env",
    "get_subproject_dir",
    "PROJECT_ROOT",
    "SRC_DIR",
    "DATA_DIR",
    "OUTPUT_DIR",
    "ENV_FILE",
]
