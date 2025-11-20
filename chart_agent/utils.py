"""Utility functions for chart_agent package.

This module provides helper functions for:
- Model listing and selection
- HTML display and formatting
- Chart result presentation
- Code execution and visualization
"""

from __future__ import annotations

import base64
import json
import os
import re
from html import escape
from pathlib import Path
from textwrap import shorten
from typing import Any, Iterable, Optional

import pandas as pd

# Try to import IPython display functions (for notebook environments)
try:
    from IPython.display import display, HTML, Image
    IPYTHON_AVAILABLE = True
except ImportError:
    IPYTHON_AVAILABLE = False
    display = print  # Fallback
    HTML = str
    Image = None


# ================================
# HTML Display Utilities
# ================================

def print_html(content: Any, title: str | None = None, is_image: bool = False):
    """Pretty-print content inside a styled card.
    
    Args:
        content: Content to display (str, DataFrame, Series, image path)
        title: Optional title for the card
        is_image: If True and content is string, treat as image path
        
    Examples:
        >>> print_html("Generated code", title="Chart Code")
        >>> print_html(df, title="Query Results")
        >>> print_html("output/chart.png", title="Generated Chart", is_image=True)
    """
    if not IPYTHON_AVAILABLE:
        # Fallback for non-notebook environments
        if title:
            print(f"\n{'='*60}\n{title}\n{'='*60}")
        print(content)
        return
    
    def image_to_base64(image_path: str) -> str:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    
    # Render content
    if is_image and isinstance(content, str):
        if os.path.exists(content):
            b64 = image_to_base64(content)
            rendered = f'<img src="data:image/png;base64,{b64}" alt="Image" style="max-width:100%; height:auto; border-radius:8px;">'
        else:
            rendered = f"<p style='color:red;'>Image not found: {escape(content)}</p>"
    elif isinstance(content, pd.DataFrame):
        rendered = content.to_html(classes="pretty-table", index=False, border=0, escape=False)
    elif isinstance(content, pd.Series):
        rendered = content.to_frame().to_html(classes="pretty-table", border=0, escape=False)
    elif isinstance(content, str):
        rendered = f"<pre><code>{escape(content)}</code></pre>"
    else:
        rendered = f"<pre><code>{escape(str(content))}</code></pre>"
    
    css = """
    <style>
    .pretty-card{
      font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
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
# OpenAI Model Utilities
# ================================

def summarize_models_response(
    models_response: Any,
    *,
    max_description_width: int = 60,
    sort_key: str = "id",
) -> list[dict[str, Any]]:
    """Return a list of simplified model dicts from client.models.list().
    
    Args:
        models_response: Result from OpenAI client's models.list()
        max_description_width: Trim long descriptions to this many characters
        sort_key: Attribute name to sort results by (default: "id")
        
    Returns:
        List of dictionaries with keys: id, created, owner, status, description
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


def display_models_table(models_response: Any, *, title: str | None = "Available OpenAI Models") -> None:
    """High-level helper: summarize client.models.list() and render via print_html.
    
    Args:
        models_response: Result from OpenAI client.models.list()
        title: Title for the display card
        
    Example:
        >>> from openai import OpenAI
        >>> client = OpenAI()
        >>> display_models_table(client.models.list())
    """
    rows = summarize_models_response(models_response)
    table_text = format_models_table(rows)
    print_html(table_text, title=title)


def models_response_to_dataframe(
    models_response: Any,
    *,
    sort_key: str = "id",
    filters: Optional[dict[str, Any]] = None,
) -> pd.DataFrame:
    """Return a pandas DataFrame for easier ad-hoc analysis of models list.
    
    Args:
        models_response: Result from OpenAI client.models.list()
        sort_key: Column to sort by
        filters: Dict of {column: value} to filter results
        
    Returns:
        DataFrame with model information
        
    Example:
        >>> df = models_response_to_dataframe(
        ...     client.models.list(),
        ...     filters={"owner": "openai"}
        ... )
        >>> gpt4_models = df[df['id'].str.contains('gpt-4')]
    """
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


def save_models_list(
    models_response: Any,
    *,
    output_dir: str = "data/llm",
    filename: str = "available_models.json",
    include_metadata: bool = True
) -> Path:
    """Save list of available models to a JSON file.
    
    Args:
        models_response: Result from OpenAI client.models.list()
        output_dir: Directory to save the file (default: data/llm)
        filename: Output filename (default: available_models.json)
        include_metadata: Whether to include full metadata or just IDs
        
    Returns:
        Path to the saved file
        
    Example:
        >>> from openai import OpenAI
        >>> client = OpenAI()
        >>> filepath = save_models_list(client.models.list())
        >>> print(f"Models saved to: {filepath}")
    """
    import json
    from datetime import datetime
    
    # Create output directory
    output_path = ensure_output_dir(output_dir)
    filepath = output_path / filename
    
    # Get model data
    rows = summarize_models_response(models_response, max_description_width=200)
    
    # Prepare output data
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "total_models": len(rows),
        "models": rows if include_metadata else [row['id'] for row in rows]
    }
    
    # Add recommendations
    recommendations = get_recommended_models(models_response)
    output_data["recommendations"] = recommendations
    
    # Save to JSON
    with open(filepath, "w") as f:
        json.dump(output_data, f, indent=2)
    
    return filepath


def load_models_list(filepath: str = "data/llm/available_models.json") -> dict[str, Any]:
    """Load previously saved models list from JSON file.
    
    Args:
        filepath: Path to the saved models JSON file
        
    Returns:
        Dict with models data and metadata
        
    Example:
        >>> data = load_models_list()
        >>> print(f"Found {data['total_models']} models")
        >>> print(f"Saved on: {data['timestamp']}")
    """
    import json
    
    with open(filepath, "r") as f:
        return json.load(f)


def get_recommended_models(models_response: Any) -> dict[str, list[str]]:
    """Get recommended models by use case using dynamic detection.
    
    This function intelligently detects the best models based on naming patterns
    rather than hardcoding specific versions, making it future-proof.
    
    Args:
        models_response: Result from OpenAI client.models.list()
        
    Returns:
        Dict mapping use case to list of recommended model IDs
        
    Example:
        >>> recommendations = get_recommended_models(client.models.list())
        >>> print(recommendations['chart_generation'])
        ['gpt-5.1', 'gpt-5-codex', 'gpt-4o']
    """
    df = models_response_to_dataframe(models_response)
    
    recommendations = {
        "chart_generation": [],
        "fast_prototyping": [],
        "cost_effective": [],
        "vision": [],
        "code_generation": [],
    }
    
    if df.empty:
        return recommendations
    
    # Get all GPT models (owned by openai, system, or openai-internal)
    openai_owners = ['openai', 'system', 'openai-internal']
    openai_models = df[df['owner'].isin(openai_owners)]['id'].tolist()
    # Filter to only GPT models
    openai_models = [m for m in openai_models if m.startswith('gpt-')]
    
    import re
    
    # Chart generation: Most capable models (prioritize latest versions, exclude mini/nano)
    # Look for: gpt-5.1, gpt-5-pro, gpt-5, gpt-4o, gpt-4-turbo (but NOT mini/nano variants)
    chart_patterns = [
        r'^gpt-5\.1(?!.*mini)(?!.*nano)',  # gpt-5.1 but not mini/nano
        r'^gpt-5-pro',                      # gpt-5-pro variants
        r'^gpt-5(?!.*mini)(?!.*nano)(?!.*codex)',  # gpt-5 but not mini/nano/codex
        r'^gpt-4o(?!.*mini)',               # gpt-4o but not mini
        r'^gpt-4-turbo',                    # gpt-4-turbo
    ]
    for pattern in chart_patterns:
        matches = [m for m in openai_models if re.search(pattern, m)]
        recommendations["chart_generation"].extend(matches)
    recommendations["chart_generation"] = list(dict.fromkeys(recommendations["chart_generation"]))
    
    # Code generation: Specialized code models (including codex)
    # Look for: codex models, then fallback to best general models
    code_patterns = [
        r'codex(?!.*mini)',                 # Full codex models (not mini)
        r'^gpt-5\.1(?!.*mini)(?!.*nano)',  # gpt-5.1 (excellent for code)
        r'^gpt-5-pro',                      # gpt-5-pro
        r'^gpt-4o(?!.*mini)',               # gpt-4o
    ]
    for pattern in code_patterns:
        matches = [m for m in openai_models if re.search(pattern, m, re.IGNORECASE)]
        recommendations["code_generation"].extend(matches)
    recommendations["code_generation"] = list(dict.fromkeys(recommendations["code_generation"]))
    
    # Fast prototyping: Mini models (default for development/testing)
    # Prioritize latest mini models (gpt-5, gpt-4o) for best performance
    # Note: All models now support both Chat Completions and Responses API
    proto_patterns = [
        r'^gpt-5\.1-codex-mini',            # gpt-5.1-codex-mini (latest codex mini)
        r'^gpt-5-mini$',                    # gpt-5-mini (latest mini)
        r'^gpt-5-mini-\d',                  # Dated versions of gpt-5-mini
        r'^gpt-4o-mini$',                   # gpt-4o-mini (proven, cost-effective)
        r'^gpt-4o-mini-\d',                 # Dated versions of gpt-4o-mini
        r'^gpt-4\.1-mini',                  # gpt-4.1-mini
        r'^gpt-3\.5-turbo$',                # gpt-3.5-turbo (fallback)
    ]
    for pattern in proto_patterns:
        matches = [m for m in openai_models if re.search(pattern, m)]
        recommendations["fast_prototyping"].extend(matches)
    recommendations["fast_prototyping"] = list(dict.fromkeys(recommendations["fast_prototyping"]))
    
    # Cost effective: Nano and mini models (cheapest options)
    cost_patterns = [
        r'nano',                            # All nano variants (cheapest)
        r'^gpt-4o-mini$',                   # gpt-4o-mini (proven cost-effective)
        r'^gpt-3\.5-turbo',                 # gpt-3.5-turbo variants
    ]
    for pattern in cost_patterns:
        matches = [m for m in openai_models if re.search(pattern, m)]
        recommendations["cost_effective"].extend(matches)
    recommendations["cost_effective"] = list(dict.fromkeys(recommendations["cost_effective"]))
    
    # Vision: Models with vision/image capabilities
    # Look for: vision, image, gpt-5.1, gpt-5, gpt-4o (exclude audio/realtime/search)
    vision_patterns = [
        r'vision',                          # Explicit vision models
        r'image',                           # Image models
        r'^gpt-5\.1(?!.*audio)(?!.*realtime)(?!.*search)',  # gpt-5.1 (has vision)
        r'^gpt-5(?!.*audio)(?!.*realtime)(?!.*search)(?!.*codex)',  # gpt-5 (has vision)
        r'^gpt-4o(?!.*audio)(?!.*realtime)(?!.*search)',    # gpt-4o (has vision)
    ]
    for pattern in vision_patterns:
        matches = [m for m in openai_models if re.search(pattern, m)]
        recommendations["vision"].extend(matches)
    recommendations["vision"] = list(dict.fromkeys(recommendations["vision"]))
    
    return recommendations


# ================================
# Chart Result Display Utilities
# ================================

def display_chart_result(
    result: dict[str, Any],
    *,
    show_code: bool = True,
    show_metadata: bool = True,
    execute: bool = False,
) -> None:
    """Display chart generation results in a formatted way.
    
    Args:
        result: Result dict from chart_agent or generate_chart_code
        show_code: Whether to display the generated code
        show_metadata: Whether to display metadata (library, chart_type, etc.)
        execute: Whether to execute the code (requires data in scope)
        
    Example:
        >>> result = generate_chart_code(dataset, "Create a bar chart...")
        >>> display_chart_result(result, show_code=True, show_metadata=True)
    """
    if show_metadata:
        metadata = {
            "Chart Type": result.get("chart_type", "Unknown"),
            "Library": result.get("library", "Unknown"),
            "Reasoning": result.get("reasoning", "N/A"),
        }
        df_meta = pd.DataFrame([metadata])
        print_html(df_meta, title="Chart Generation Metadata")
    
    if show_code and "code" in result:
        print_html(result["code"], title="Generated Chart Code")
    
    if execute and "code" in result:
        print_html("Executing generated code...", title="Execution")
        try:
            # Note: This requires 'df' to be in the calling scope
            exec(result["code"], {"df": None, "pd": pd})
            print_html("✓ Code executed successfully", title="Status")
        except Exception as e:
            print_html(f"✗ Execution failed: {e}", title="Error")


def display_analysis_summary(
    analysis_type: str,
    query_result: pd.DataFrame,
    *,
    show_sample: bool = True,
    sample_rows: int = 5,
) -> None:
    """Display summary of analysis query results.
    
    Args:
        analysis_type: Name of the analysis
        query_result: DataFrame with query results
        show_sample: Whether to show sample rows
        sample_rows: Number of sample rows to display
        
    Example:
        >>> display_analysis_summary(
        ...     "high_alternative_splicing",
        ...     query_result,
        ...     show_sample=True
        ... )
    """
    summary = {
        "Analysis": analysis_type,
        "Rows": len(query_result),
        "Columns": len(query_result.columns),
        "Column Names": ", ".join(query_result.columns.tolist()),
    }
    df_summary = pd.DataFrame([summary])
    print_html(df_summary, title="Analysis Summary")
    
    if show_sample and not query_result.empty:
        sample = query_result.head(sample_rows)
        print_html(sample, title=f"Sample Data (first {sample_rows} rows)")


# ================================
# Code Execution Utilities
# ================================

def execute_chart_code(
    code: str,
    data: pd.DataFrame,
    *,
    save_path: Optional[str] = None,
    show_plot: bool = True,
) -> dict[str, Any]:
    """Execute generated chart code with provided data.
    
    Args:
        code: Python code to execute
        data: DataFrame to use as 'df' in the code
        save_path: Optional path to save the generated plot
        show_plot: Whether to display the plot
        
    Returns:
        Dict with execution status and any errors
        
    Example:
        >>> result = execute_chart_code(
        ...     generated_code,
        ...     query_result,
        ...     save_path="output/chart.png"
        ... )
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Prepare execution environment
    exec_globals = {
        "df": data,
        "pd": pd,
        "plt": plt,
        "np": np,
    }
    
    # Try to import common libraries
    try:
        import seaborn as sns
        exec_globals["sns"] = sns
    except ImportError:
        pass
    
    result = {
        "success": False,
        "error": None,
        "plot_path": save_path,
    }
    
    try:
        # Execute the code
        exec(code, exec_globals)
        
        # Save if requested
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            result["plot_path"] = save_path
        
        # Show if requested
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
        plt.close()
    
    return result


# ================================
# File and Path Utilities
# ================================

def ensure_output_dir(base_dir: str = "output") -> Path:
    """Ensure output directory exists and return Path object.
    
    Args:
        base_dir: Base directory name
        
    Returns:
        Path object for the output directory
    """
    output_path = Path(base_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def save_code_to_file(
    code: str,
    filename: str,
    *,
    output_dir: str = "output",
    add_header: bool = True,
    metadata: Optional[dict[str, Any]] = None,
) -> Path:
    """Save generated code to a Python file.
    
    Args:
        code: Python code to save
        filename: Output filename (without .py extension)
        output_dir: Output directory
        add_header: Whether to add a header comment
        metadata: Optional metadata to include in header
        
    Returns:
        Path to the saved file
        
    Example:
        >>> path = save_code_to_file(
        ...     generated_code,
        ...     "my_chart",
        ...     metadata={"analysis": "splice_sites", "date": "2025-11-18"}
        ... )
    """
    output_path = ensure_output_dir(output_dir)
    filepath = output_path / f"{filename}.py"
    
    with open(filepath, "w") as f:
        if add_header:
            f.write("# Generated by chart_agent\n")
            if metadata:
                for key, value in metadata.items():
                    f.write(f"# {key}: {value}\n")
                f.write("\n")
        f.write(code)
    
    return filepath


# ================================
# Validation Utilities
# ================================

def validate_chart_code(code: str) -> dict[str, Any]:
    """Validate generated chart code for common issues.
    
    Args:
        code: Python code to validate
        
    Returns:
        Dict with validation results
        
    Example:
        >>> validation = validate_chart_code(generated_code)
        >>> if not validation['valid']:
        ...     print(validation['issues'])
    """
    issues = []
    warnings = []
    
    # Check for required imports
    if "matplotlib" not in code and "plt" not in code:
        issues.append("No matplotlib import found")
    
    # Check for data reference
    if "df" not in code and "data" not in code:
        warnings.append("No DataFrame reference found (df or data)")
    
    # Check for plot display/save
    if "plt.show()" not in code and "plt.savefig" not in code:
        warnings.append("No plt.show() or plt.savefig() found")
    
    # Check for syntax errors
    try:
        compile(code, "<string>", "exec")
    except SyntaxError as e:
        issues.append(f"Syntax error: {e}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "code_length": len(code),
        "line_count": len(code.split("\n")),
    }
