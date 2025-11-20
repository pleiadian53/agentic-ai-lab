"""
Visualization utilities for evaluation results.

Provides functions to display evaluation results in Jupyter notebooks
with rich HTML formatting.
"""

from typing import Any
from IPython.display import display, HTML

from .metrics import EvaluationResult, compute_domain_metrics


def display_evaluation(result: EvaluationResult, format: str = "html") -> None:
    """
    Display evaluation result in notebook.
    
    Args:
        result: EvaluationResult object
        format: Display format ('html' or 'markdown')
    """
    if format == "html":
        display(HTML(result.to_html()))
    else:
        print(result.to_markdown())


def display_evaluation_summary(
    results: list[EvaluationResult],
    title: str = "Evaluation Summary"
) -> None:
    """
    Display summary of multiple evaluation results.
    
    Args:
        results: List of EvaluationResult objects
        title: Title for the summary
    """
    metrics = compute_domain_metrics(results)
    
    html = f"""
<div style="border: 2px solid #3b82f6; border-radius: 8px; padding: 16px; margin: 10px 0; background: #f9fafb;">
    <h3 style="margin-top: 0; color: #3b82f6;">{title}</h3>
    
    <table style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 4px;"><strong>Total evaluations:</strong></td>
            <td style="padding: 4px;">{metrics['num_evaluations']}</td>
        </tr>
        <tr>
            <td style="padding: 4px;"><strong>Passed:</strong></td>
            <td style="padding: 4px; color: #10b981;">{metrics['num_passed']}</td>
        </tr>
        <tr>
            <td style="padding: 4px;"><strong>Failed:</strong></td>
            <td style="padding: 4px; color: #ef4444;">{metrics['num_failed']}</td>
        </tr>
        <tr>
            <td style="padding: 4px;"><strong>Pass rate:</strong></td>
            <td style="padding: 4px;">{metrics['pass_rate']:.1%}</td>
        </tr>
        <tr>
            <td style="padding: 4px;"><strong>Average ratio:</strong></td>
            <td style="padding: 4px;">{metrics['avg_ratio']:.1%}</td>
        </tr>
        <tr>
            <td style="padding: 4px;"><strong>Total sources:</strong></td>
            <td style="padding: 4px;">{metrics['total_sources']}</td>
        </tr>
        <tr>
            <td style="padding: 4px;"><strong>Total preferred:</strong></td>
            <td style="padding: 4px;">{metrics['total_preferred']}</td>
        </tr>
        <tr>
            <td style="padding: 4px;"><strong>Overall ratio:</strong></td>
            <td style="padding: 4px;">{metrics['overall_ratio']:.1%}</td>
        </tr>
    </table>
</div>
"""
    display(HTML(html))


def print_html(
    content: Any,
    title: str | None = None,
    style: str = "default"
) -> None:
    """
    Pretty-print content in a styled card (compatible with M4 utils).
    
    Args:
        content: Content to display (string, HTML, or EvaluationResult)
        title: Optional title for the card
        style: Style preset ('default', 'success', 'warning', 'error')
    """
    # Handle EvaluationResult objects
    if isinstance(content, EvaluationResult):
        display(HTML(content.to_html()))
        return
    
    # Style presets
    border_colors = {
        "default": "#3b82f6",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
    }
    
    border_color = border_colors.get(style, border_colors["default"])
    
    # Convert content to HTML
    if isinstance(content, str):
        if content.strip().startswith("<"):
            # Already HTML
            rendered = content
        else:
            # Plain text - wrap in pre/code
            from html import escape
            rendered = f"<pre><code>{escape(content)}</code></pre>"
    else:
        from html import escape
        rendered = f"<pre><code>{escape(str(content))}</code></pre>"
    
    css = f"""
<style>
.eval-card {{
    font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
    border: 2px solid {border_color};
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
    background: #ffffff;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}}
.eval-card-title {{
    font-weight: 700;
    margin-bottom: 12px;
    font-size: 16px;
    color: {border_color};
}}
.eval-card pre {{
    background: #f3f4f6;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 13px;
}}
.eval-card code {{
    font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
}}
</style>
"""
    
    title_html = f'<div class="eval-card-title">{title}</div>' if title else ""
    card = f'<div class="eval-card">{title_html}{rendered}</div>'
    
    display(HTML(css + card))


def display_domain_comparison(
    result1: EvaluationResult,
    result2: EvaluationResult,
    label1: str = "Result 1",
    label2: str = "Result 2"
) -> None:
    """
    Display side-by-side comparison of two evaluation results.
    
    Args:
        result1: First evaluation result
        result2: Second evaluation result
        label1: Label for first result
        label2: Label for second result
    """
    html = f"""
<div style="display: flex; gap: 16px; margin: 10px 0;">
    <div style="flex: 1;">
        <h4 style="margin-top: 0;">{label1}</h4>
        {result1.to_html(include_details=False)}
    </div>
    <div style="flex: 1;">
        <h4 style="margin-top: 0;">{label2}</h4>
        {result2.to_html(include_details=False)}
    </div>
</div>
"""
    
    # Show improvement/degradation
    ratio_change = result2.ratio - result1.ratio
    change_color = "#10b981" if ratio_change > 0 else "#ef4444" if ratio_change < 0 else "#6b7280"
    change_icon = "📈" if ratio_change > 0 else "📉" if ratio_change < 0 else "➡️"
    
    html += f"""
<div style="border: 2px solid {change_color}; border-radius: 8px; padding: 12px; margin-top: 16px; background: #f9fafb;">
    <strong>{change_icon} Change:</strong> {ratio_change:+.1%} 
    ({result1.ratio:.1%} → {result2.ratio:.1%})
</div>
"""
    
    display(HTML(html))
