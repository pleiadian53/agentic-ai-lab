# ================================
# Standard library imports
# ================================
import base64
import json
import re
from html import escape
from textwrap import shorten
from typing import Any, Iterable, Optional

# ================================
# Third-party imports
# ================================
import pandas as pd
from IPython.display import display, HTML

# ================================
# Personal / local imports
# ================================
# 

# ================================
# Utility function
# ================================
def print_html(content: Any, title: str | None = None, is_image: bool = False):
    """
    Pretty-print inside a styled card.
    - If is_image=True and content is a string: treat as image path/URL and render <img>.
    - If content is a pandas DataFrame/Series: render as an HTML table.
    - Otherwise (strings/otros): show as code/text in <pre><code>.
    """
    try:
        from html import escape as _escape
    except ImportError:
        _escape = lambda x: x

    def image_to_base64(image_path: str) -> str:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    # Render content
    if is_image and isinstance(content, str):
        b64 = image_to_base64(content)
        rendered = f'<img src="data:image/png;base64,{b64}" alt="Image" style="max-width:100%; height:auto; border-radius:8px;">'
    elif isinstance(content, pd.DataFrame):
        rendered = content.to_html(classes="pretty-table", index=False, border=0, escape=False)
    elif isinstance(content, pd.Series):
        rendered = content.to_frame().to_html(classes="pretty-table", border=0, escape=False)
    elif isinstance(content, str):
        rendered = f"<pre><code>{_escape(content)}</code></pre>"
    else:
        rendered = f"<pre><code>{_escape(str(content))}</code></pre>"

    css = """
    <style>
    .pretty-card{
      font-family: ui-sans-serif, system-ui;
      border: 2px solid transparent;
      border-radius: 14px;
      padding: 14px 16px;
      margin: 10px 0;
      background: linear-gradient(#fff, #fff) padding-box,
                  linear-gradient(135deg, #3b82f6, #9333ea) border-box;
      color: #111;
      box-shadow: 0 4px 12px rgba(0,0,0,.08);
    }
    .pretty-title{
      font-weight:700;
      margin-bottom:8px;
      font-size:14px;
      color:#111;
    }
    /* 🔒 Solo afecta lo DENTRO de la tarjeta */
    .pretty-card pre, 
    .pretty-card code {
      background: #f3f4f6;
      color: #111;
      padding: 8px;
      border-radius: 8px;
      display: block;
      overflow-x: auto;
      font-size: 13px;
      white-space: pre-wrap;
    }
    .pretty-card img { max-width: 100%; height: auto; border-radius: 8px; }
    .pretty-card table.pretty-table {
      border-collapse: collapse;
      width: 100%;
      font-size: 13px;
      color: #111;
    }
    .pretty-card table.pretty-table th, 
    .pretty-card table.pretty-table td {
      border: 1px solid #e5e7eb;
      padding: 6px 8px;
      text-align: left;
    }
    .pretty-card table.pretty-table th { background: #f9fafb; font-weight: 600; }
    </style>
    """

    title_html = f'<div class="pretty-title">{title}</div>' if title else ""
    card = f'<div class="pretty-card">{title_html}{rendered}</div>'
    display(HTML(css + card))


# ================================
# OpenAI helper utilities
# ================================
def summarize_models_response(
    models_response: Any,
    *,
    max_description_width: int = 60,
    sort_key: str = "id",
) -> list[dict[str, Any]]:
    """Return a list of simplified model dicts from client.models.list().

    Args:
        models_response: Result from OpenAI client's ``models.list()``.
        max_description_width: Trim long descriptions to this many characters.
        sort_key: Attribute name to sort results by (default: ``"id"``).

    Returns:
        List of dictionaries with keys: ``id``, ``created``, ``owner``, ``status``, ``description``.
    """

    data = getattr(models_response, "data", []) or []
    sorted_models = sorted(data, key=lambda m: getattr(m, sort_key, ""))
    rows: list[dict[str, Any]] = []

    for model in sorted_models:
        description = getattr(model, "description", "") or ""
        rows.append(
            {
                "id": getattr(model, "id", "unknown"),
                "created": getattr(model, "created", ""),
                "owner": getattr(model, "owned_by", "unknown"),
                "status": getattr(model, "status", "active"),
                "description": shorten(description.strip(), max_description_width, placeholder="…"),
            }
        )

    return rows


def format_models_table(rows: Iterable[dict[str, Any]]) -> str:
    """Return a plain-text table for model metadata rows."""

    rows = list(rows)
    if not rows:
        return "(no models found)"

    headers = ["id", "created", "owner", "status", "description"]
    widths = {
        header: max(len(header), max((len(str(row.get(header, ""))) for row in rows), default=0))
        for header in headers[:-1]
    }
    widths["description"] = len("description")

    header_line = "  ".join(
        f"{header:<{widths.get(header, len(header))}}" if header != "description" else header for header in headers
    )
    sep_line = "-" * len(header_line)

    lines = [header_line, sep_line]
    for row in rows:
        line_parts = []
        for header in headers[:-1]:
            line_parts.append(f"{str(row.get(header, '')):<{widths[header]}}")
        line_parts.append(str(row.get("description", "")))
        lines.append("  ".join(line_parts))

    return "\n".join(lines)


def display_models_table(models_response: Any, *, title: str | None = "Model Catalog") -> None:
    """High-level helper: summarize client.models.list() and render via print_html."""

    rows = summarize_models_response(models_response)
    table_text = format_models_table(rows)
    print_html(table_text, title=title)


def models_response_to_dataframe(
    models_response: Any,
    *,
    sort_key: str = "id",
    filters: Optional[dict[str, Any]] = None,
) -> pd.DataFrame:
    """Return a pandas DataFrame for easier ad-hoc analysis of models list."""

    rows = summarize_models_response(models_response, sort_key=sort_key)
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    if sort_key in df.columns:
        df = df.sort_values(sort_key)

    if filters:
        mask = pd.Series([True] * len(df))
        for field, expected in filters.items():
            if field in df.columns:
                mask &= df[field] == expected
        df = df[mask]

    return df.reset_index(drop=True)