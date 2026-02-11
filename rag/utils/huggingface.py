"""
HuggingFace Environment Configuration & Cache Monitor
======================================================

Utilities for configuring HuggingFace cache paths and inspecting
downloaded models/datasets (disk usage, revisions, staleness).

Usage — as a library:
    from rag.utils.huggingface import configure_cache, cache_summary, cache_report

    # Optionally redirect cache before any HF imports
    configure_cache("/my/custom/cache")

    # Quick overview
    print(cache_summary())

    # Detailed per-repo breakdown
    print(cache_report())

Usage — as a CLI:
    mamba run -n agentic-ai python rag/utils/huggingface.py
    mamba run -n agentic-ai python rag/utils/huggingface.py --detail
    mamba run -n agentic-ai python rag/utils/huggingface.py --cache-dir /custom/path
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------

def get_cache_dir() -> Path:
    """Return the current HuggingFace hub cache directory."""
    from huggingface_hub import constants
    return Path(constants.HF_HUB_CACHE)


def get_hf_home() -> Path:
    """Return the HuggingFace home directory (parent of hub cache)."""
    from huggingface_hub import constants
    return Path(constants.HF_HOME)


def configure_cache(cache_dir: Optional[str | Path] = None) -> Path:
    """
    Set the HuggingFace cache directory via environment variables.

    **Must be called before** importing ``transformers``, ``sentence_transformers``,
    or any library that reads HF env vars at import time.

    Args:
        cache_dir: Custom cache directory. If None, leaves the default
                   (``~/.cache/huggingface``).

    Returns:
        The resolved cache directory that will be used.
    """
    if cache_dir is not None:
        cache_dir = Path(cache_dir).expanduser().resolve()
        cache_dir.mkdir(parents=True, exist_ok=True)
        os.environ["HF_HOME"] = str(cache_dir)
        os.environ["HUGGINGFACE_HUB_CACHE"] = str(cache_dir / "hub")
    return get_cache_dir()


# ---------------------------------------------------------------------------
# Cache inspection
# ---------------------------------------------------------------------------

@dataclass
class RepoInfo:
    """Summary of a single cached repository."""
    repo_id: str
    repo_type: str
    size_bytes: int
    size_str: str
    nb_files: int
    last_modified: datetime
    revisions: int


def _scan(cache_dir: Optional[str | Path] = None):
    """Run huggingface_hub's cache scanner."""
    from huggingface_hub import scan_cache_dir
    if cache_dir:
        return scan_cache_dir(str(cache_dir))
    return scan_cache_dir()


def list_repos(cache_dir: Optional[str | Path] = None) -> list[RepoInfo]:
    """
    List all cached HuggingFace repos with metadata.

    Args:
        cache_dir: Override cache directory to scan. None = default.

    Returns:
        List of RepoInfo sorted by size (largest first).
    """
    cache_info = _scan(cache_dir)
    repos = []
    for r in cache_info.repos:
        last_mod = max(
            (rev.last_modified for rev in r.revisions),
            default=0.0,
        )
        repos.append(RepoInfo(
            repo_id=r.repo_id,
            repo_type=r.repo_type,
            size_bytes=r.size_on_disk,
            size_str=r.size_on_disk_str,
            nb_files=r.nb_files,
            last_modified=datetime.fromtimestamp(last_mod) if last_mod else datetime.min,
            revisions=len(r.revisions),
        ))
    repos.sort(key=lambda r: r.size_bytes, reverse=True)
    return repos


def total_size(cache_dir: Optional[str | Path] = None) -> tuple[int, str]:
    """
    Return total cache size as (bytes, human-readable string).

    Args:
        cache_dir: Override cache directory to scan. None = default.
    """
    cache_info = _scan(cache_dir)
    return cache_info.size_on_disk, cache_info.size_on_disk_str


def _format_size(size_bytes: int) -> str:
    """Format bytes into a human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


# ---------------------------------------------------------------------------
# Reports (formatted strings)
# ---------------------------------------------------------------------------

def cache_summary(cache_dir: Optional[str | Path] = None) -> str:
    """
    One-line summary of cache usage.

    Example:
        "HF cache: 4.8 GB across 13 repos in /Users/you/.cache/huggingface/hub"
    """
    total_bytes, total_str = total_size(cache_dir)
    repos = list_repos(cache_dir)
    resolved_dir = Path(cache_dir) if cache_dir else get_cache_dir()
    return f"HF cache: {total_str} across {len(repos)} repos in {resolved_dir}"


def cache_report(
    cache_dir: Optional[str | Path] = None,
    detail: bool = False,
) -> str:
    """
    Formatted multi-line report of cached repos.

    Args:
        cache_dir: Override cache directory to scan.
        detail: If True, include revision hashes and file counts.

    Returns:
        Formatted string suitable for printing.
    """
    repos = list_repos(cache_dir)
    total_bytes, total_str = total_size(cache_dir)
    resolved_dir = Path(cache_dir) if cache_dir else get_cache_dir()

    lines = [
        "=" * 70,
        "HuggingFace Cache Report",
        "=" * 70,
        f"  Cache directory : {resolved_dir}",
        f"  Total size      : {total_str}",
        f"  Repositories    : {len(repos)}",
        "-" * 70,
    ]

    if not repos:
        lines.append("  (empty — no models or datasets cached)")
    else:
        # Column headers
        lines.append(f"  {'Repo ID':<45} {'Type':<10} {'Size':>10}")
        lines.append(f"  {'-'*45} {'-'*10} {'-'*10}")

        for r in repos:
            lines.append(f"  {r.repo_id:<45} {r.repo_type:<10} {r.size_str:>10}")
            if detail:
                lines.append(f"    files: {r.nb_files}  |  revisions: {r.revisions}  |  last modified: {r.last_modified:%Y-%m-%d %H:%M}")

    lines.append("-" * 70)

    # Breakdown by type
    models = [r for r in repos if r.repo_type == "model"]
    datasets = [r for r in repos if r.repo_type == "dataset"]
    model_total = sum(r.size_bytes for r in models)
    dataset_total = sum(r.size_bytes for r in datasets)

    lines.append(f"  Models   : {len(models):>3} repos, {_format_size(model_total):>10}")
    lines.append(f"  Datasets : {len(datasets):>3} repos, {_format_size(dataset_total):>10}")
    lines.append("=" * 70)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Inspect the HuggingFace model/dataset cache.",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default=None,
        help="Custom cache directory to scan (default: HF default).",
    )
    parser.add_argument(
        "--detail",
        action="store_true",
        help="Show file counts, revisions, and last-modified dates.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a one-line summary only.",
    )
    args = parser.parse_args()

    if args.summary:
        print(cache_summary(args.cache_dir))
    else:
        print(cache_report(args.cache_dir, detail=args.detail))


if __name__ == "__main__":
    main()
