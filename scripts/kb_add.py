#!/usr/bin/env python3
"""
kb_add.py — Add a URL or local file to the Nexus knowledge base.

Usage
-----
  python scripts/kb_add.py <url_or_path> [--title TITLE] [--tags tag1,tag2]
  python scripts/kb_add.py --list
  python scripts/kb_add.py --search "agentic memory"

This writes a KB item to the same location that OpenClaw/Lyra uses
(``~/.openclaw/workspace/knowledge/agentic-ai-lab/kb/items/``), so both
ingestion paths share the same substrate and Nexus can query all of them.

Override the KB location via the NEXUS_KB_PATH environment variable.
"""

import argparse
import sys
import textwrap
from pathlib import Path

# ---------------------------------------------------------------------------
# Path bootstrap — make sure the project src is importable
# ---------------------------------------------------------------------------
_repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_repo_root / "src"))

from nexus.knowledge.kb import KnowledgeBase, get_kb_dir  # noqa: E402


# ---------------------------------------------------------------------------
# Content fetching
# ---------------------------------------------------------------------------

def _fetch_url(url: str) -> tuple[str, str]:
    """
    Fetch URL and return (title, cleaned_text).

    Uses requests + a lightweight HTML stripper.  Falls back gracefully.
    """
    import re
    import requests

    headers = {"User-Agent": "Nexus-KB/1.0"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()

    html = resp.text

    # Extract <title>
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    title = title_match.group(1).strip() if title_match else url

    # Strip scripts / style blocks
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
    # Strip all remaining tags
    text = re.sub(r"<[^>]+>", " ", html)
    # Collapse whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    # Truncate to a reasonable size for storage
    if len(text) > 8000:
        text = text[:8000] + "\n\n[... truncated at 8 000 chars ...]"

    return title, text


def _read_local_file(path: str) -> tuple[str, str]:
    """Read a local text/markdown file and return (filename_stem, content)."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    content = p.read_text(encoding="utf-8")
    return p.stem, content


def _build_summary(text: str, max_sentences: int = 4) -> str:
    """
    Build a naive extractive summary from the first few sentences.

    This is a placeholder — replace with an LLM call for better quality.
    """
    import re
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    selected = [s.strip() for s in sentences[:max_sentences] if len(s.strip()) > 20]
    return " ".join(selected) if selected else text[:300].strip()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_add(args: argparse.Namespace) -> None:
    source = args.source
    kb = KnowledgeBase()

    print(f"KB directory: {kb.kb_dir}")

    # Determine if source is a URL or a local file
    is_url = source.startswith("http://") or source.startswith("https://")

    if is_url:
        print(f"Fetching: {source}")
        try:
            fetched_title, content = _fetch_url(source)
        except Exception as exc:
            print(f"ERROR fetching URL: {exc}", file=sys.stderr)
            sys.exit(1)
        url = source
    else:
        print(f"Reading local file: {source}")
        try:
            fetched_title, content = _read_local_file(source)
        except Exception as exc:
            print(f"ERROR reading file: {exc}", file=sys.stderr)
            sys.exit(1)
        url = f"file://{Path(source).resolve()}"

    title = args.title or fetched_title
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
    summary = _build_summary(content)

    path = kb.add_item(
        url=url,
        title=title,
        content=content,
        summary=summary,
        tags=tags,
    )

    print(f"\n✓ Item saved: {path}")
    print(f"  Title   : {title}")
    print(f"  Tags    : {', '.join(tags) or '(none)'}")
    print(f"  Summary : {summary[:120]}{'...' if len(summary) > 120 else ''}")


def cmd_list(args: argparse.Namespace) -> None:
    kb = KnowledgeBase()
    items = kb.list_items()

    if not items:
        print(f"Knowledge base is empty.\nKB directory: {kb.items_dir}")
        return

    print(f"Knowledge base — {len(items)} item(s) in {kb.items_dir}\n")
    for item in items:
        tags_str = ", ".join(item["tags"]) if isinstance(item["tags"], list) else item["tags"]
        print(f"  [{item['date']}] {item['title']}")
        print(f"           {item['url']}")
        if tags_str:
            print(f"           tags: {tags_str}")
        print()


def cmd_search(args: argparse.Namespace) -> None:
    kb = KnowledgeBase()
    results = kb.search(args.query, top_k=args.top_k)

    if not results or (len(results) == 1 and "message" in results[0]):
        msg = results[0].get("message", "No results.") if results else "No results."
        print(msg)
        return

    print(f"Search: \"{args.query}\"  ({len(results)} result(s))\n")
    for i, r in enumerate(results, 1):
        tags_str = ", ".join(r["tags"]) if isinstance(r["tags"], list) else r["tags"]
        print(f"  {i}. {r['title']}  (score: {r['score']})")
        print(f"     {r['url']}")
        print(f"     {r['date']}  |  tags: {tags_str or '(none)'}")
        print()
        summary = r.get("summary", "")
        if summary:
            print(textwrap.indent(textwrap.fill(summary, 72), "     "))
        excerpt = r.get("excerpt", "")
        if excerpt:
            print()
            print(textwrap.indent(textwrap.fill(excerpt, 72), "     > "))
        print()


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kb_add",
        description="Add URLs/files to the Nexus knowledge base, list items, or search.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              # Ingest a URL
              python scripts/kb_add.py https://arxiv.org/abs/2310.06825 --tags llm,efficiency

              # Ingest with explicit title
              python scripts/kb_add.py https://example.com/blog --title "My Post" --tags agentic

              # Ingest a local markdown file
              python scripts/kb_add.py dev/notes/my_notes.md --tags notes

              # List all KB items
              python scripts/kb_add.py --list

              # Search the KB
              python scripts/kb_add.py --search "agentic memory" --top-k 3
        """),
    )

    subparsers = parser.add_subparsers(dest="command")

    # add (default when a positional source is provided)
    add_p = subparsers.add_parser("add", help="Add a URL or file to the KB.")
    add_p.add_argument("source", help="URL or local file path to ingest.")
    add_p.add_argument("--title", help="Override the extracted title.")
    add_p.add_argument("--tags", default="", help="Comma-separated tags (e.g. llm,efficiency).")

    # list
    subparsers.add_parser("list", help="List all KB items.")

    # search
    search_p = subparsers.add_parser("search", help="Search KB items.")
    search_p.add_argument("query", help="Natural-language query string.")
    search_p.add_argument("--top-k", type=int, default=5, dest="top_k",
                          help="Number of results to return (default: 5).")

    # Convenience: allow positional URL/path as implicit "add"
    parser.add_argument("source", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("--title", help=argparse.SUPPRESS)
    parser.add_argument("--tags", default="", help=argparse.SUPPRESS)
    parser.add_argument("--list", action="store_true", help="List all KB items.")
    parser.add_argument("--search", metavar="QUERY", help="Search KB items.")
    parser.add_argument("--top-k", type=int, default=5, dest="top_k",
                        help="Number of search results to return (default: 5).")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Route to sub-command
    if args.command == "add" or (not args.command and args.source):
        cmd_add(args)
    elif args.command == "list" or args.list:
        cmd_list(args)
    elif args.command == "search" or args.search:
        if args.command != "search":
            args.query = args.search
        cmd_search(args)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
