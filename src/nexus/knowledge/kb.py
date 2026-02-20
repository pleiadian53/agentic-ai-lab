"""
Knowledge Base for Nexus Research Agent
========================================

File-based personal knowledge base.  Items are stored as markdown files with
YAML frontmatter in an ``items/`` subdirectory.  The format is intentionally
compatible with the items that OpenClaw/Lyra writes when you send
``kb add <url>`` via Telegram, so both ingestion paths share the same substrate.

Default location: ``~/.openclaw/workspace/knowledge/agentic-ai-lab/kb/``
Override       : set ``NEXUS_KB_PATH`` env var to any directory.
"""

import os
import re
from datetime import date
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

_DEFAULT_KB_DIR = (
    Path.home()
    / ".openclaw"
    / "workspace"
    / "knowledge"
    / "agentic-ai-lab"
    / "kb"
)


def get_kb_dir() -> Path:
    """Return the active KB root directory (env override or default)."""
    env_path = os.getenv("NEXUS_KB_PATH")
    return Path(env_path) if env_path else _DEFAULT_KB_DIR


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slugify(text: str, max_len: int = 60) -> str:
    """Convert text to a filename-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text[:max_len]


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parse simple YAML-ish frontmatter delimited by ``---`` lines.

    Returns ``(meta_dict, body_text)``.  On parse failure returns
    ``({}, original_content)``.
    """
    if not content.startswith("---"):
        return {}, content

    end = content.find("---", 3)
    if end == -1:
        return {}, content

    fm_text = content[3:end].strip()
    body = content[end + 3:].strip()

    meta: dict = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        # Parse inline list  [tag1, tag2]
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1]
            value = [v.strip().strip("\"'") for v in inner.split(",") if v.strip()]
        meta[key] = value

    return meta, body


def _find_excerpt(text: str, query_terms: set[str], max_chars: int = 300) -> str:
    """Extract a short snippet of *text* around the first matching query term."""
    lower = text.lower()
    best_pos = len(text)

    for term in query_terms:
        pos = lower.find(term)
        if 0 <= pos < best_pos:
            best_pos = pos

    if best_pos == len(text):
        return text[:max_chars].strip()

    start = max(0, best_pos - 80)
    end = min(len(text), start + max_chars)
    snippet = text[start:end].strip()

    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."

    return snippet


# ---------------------------------------------------------------------------
# KnowledgeBase
# ---------------------------------------------------------------------------

class KnowledgeBase:
    """
    File-based personal knowledge base for Nexus.

    Each KB item is a markdown file under ``<kb_dir>/items/`` with the naming
    convention ``YYYY-MM-DD__<slug>.md`` and YAML frontmatter containing url,
    date, title, tags, and summary.

    Example
    -------
    >>> kb = KnowledgeBase()
    >>> path = kb.add_item(
    ...     url="https://arxiv.org/abs/2310.06825",
    ...     title="Mistral 7B",
    ...     content="Full text ...",
    ...     summary="Efficient 7B LLM outperforming Llama 2 13B.",
    ...     tags=["llm", "efficiency", "mistral"],
    ... )
    >>> results = kb.search("efficient language model")
    >>> print(results[0]["title"])
    'Mistral 7B'
    """

    def __init__(self, kb_dir: Optional[Path | str] = None):
        self.kb_dir = Path(kb_dir) if kb_dir else get_kb_dir()
        self.items_dir = self.kb_dir / "items"
        self.indexes_dir = self.kb_dir / "indexes"

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def add_item(
        self,
        url: str,
        title: str,
        content: str,
        summary: str,
        tags: list[str],
        today: Optional[str] = None,
    ) -> str:
        """
        Write a new KB item as a markdown file and return its path.

        Parameters
        ----------
        url:
            Source URL of the item.
        title:
            Human-readable title (used to derive the filename slug).
        content:
            Main body text (cleaned, no HTML).
        summary:
            One-paragraph summary (2–5 sentences).
        tags:
            List of short keyword tags.
        today:
            Override the date string (``YYYY-MM-DD``); defaults to today.

        Returns
        -------
        str
            Absolute path of the created file.
        """
        self._ensure_dirs()

        today = today or str(date.today())
        slug = _slugify(title)
        filename = f"{today}__{slug}.md"
        filepath = self.items_dir / filename

        # Avoid collisions on same-day same-title entries
        counter = 1
        while filepath.exists():
            filepath = self.items_dir / f"{today}__{slug}_{counter}.md"
            counter += 1

        tags_str = ", ".join(tags) if tags else ""

        file_content = (
            f"---\n"
            f"url: {url}\n"
            f"date: {today}\n"
            f"title: {title}\n"
            f"tags: [{tags_str}]\n"
            f"summary: {summary}\n"
            f"---\n\n"
            f"# {title}\n\n"
            f"**URL**: {url}  \n"
            f"**Date**: {today}  \n"
            f"**Tags**: {tags_str}\n\n"
            f"## Summary\n\n"
            f"{summary}\n\n"
            f"## Content\n\n"
            f"{content}\n"
        )

        filepath.write_text(file_content, encoding="utf-8")
        return str(filepath)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def list_items(self) -> list[dict]:
        """Return metadata for all KB items, sorted newest first."""
        if not self.items_dir.exists():
            return []

        items = []
        for f in sorted(self.items_dir.glob("*.md"), reverse=True):
            raw = f.read_text(encoding="utf-8")
            meta, _ = _parse_frontmatter(raw)
            items.append({
                "file": f.name,
                "title": meta.get("title", f.stem),
                "url": meta.get("url", ""),
                "date": meta.get("date", ""),
                "tags": meta.get("tags", []),
                "summary": meta.get("summary", ""),
            })
        return items

    def get_item(self, filename: str) -> dict:
        """Return full content + metadata for a single item by filename."""
        filepath = self.items_dir / filename
        if not filepath.exists():
            return {"error": f"Item not found: {filename}"}

        raw = filepath.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(raw)
        return {
            "file": filename,
            "title": meta.get("title", filepath.stem),
            "url": meta.get("url", ""),
            "date": meta.get("date", ""),
            "tags": meta.get("tags", []),
            "summary": meta.get("summary", ""),
            "content": body,
        }

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Lexical search over all KB items.

        Scores each item by the number of query-term matches across its title,
        summary, tags, and body text.  Returns the top-*k* results with a
        short excerpt from the matching region of each item.

        Parameters
        ----------
        query:
            Natural-language question or keyword string.
        top_k:
            Maximum number of results to return.

        Returns
        -------
        list[dict]
            Each result contains: file, title, url, date, tags, summary,
            excerpt, score.  Empty list if the KB is empty or nothing matches.
        """
        if not self.items_dir.exists():
            return []

        query_terms = set(query.lower().split())
        scored: list[tuple[int, dict]] = []

        for f in self.items_dir.glob("*.md"):
            raw = f.read_text(encoding="utf-8")
            meta, body = _parse_frontmatter(raw)

            title = meta.get("title", "")
            summary = meta.get("summary", "")
            tags = meta.get("tags", [])
            tags_str = " ".join(tags) if isinstance(tags, list) else str(tags)

            searchable = f"{title} {summary} {tags_str} {body}".lower()
            score = sum(1 for term in query_terms if term in searchable)

            if score == 0:
                continue

            excerpt = _find_excerpt(body, query_terms)

            scored.append((score, {
                "file": f.name,
                "title": title,
                "url": meta.get("url", ""),
                "date": meta.get("date", ""),
                "tags": tags,
                "summary": summary,
                "excerpt": excerpt,
                "score": score,
            }))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:top_k]]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _ensure_dirs(self) -> None:
        self.items_dir.mkdir(parents=True, exist_ok=True)
        self.indexes_dir.mkdir(parents=True, exist_ok=True)
