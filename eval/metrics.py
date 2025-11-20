"""
Metrics and result classes for evaluation.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvaluationResult:
    """
    Results from a domain evaluation.
    
    Attributes:
        passed: Whether evaluation passed (ratio >= min_ratio)
        total: Total number of sources found
        preferred: Number of preferred sources
        ratio: Ratio of preferred to total sources (0.0-1.0)
        min_ratio: Minimum ratio required to pass
        sources: List of source dictionaries with details
    """
    passed: bool
    total: int
    preferred: int
    ratio: float
    min_ratio: float
    sources: list[dict] = field(default_factory=list)
    
    @property
    def status(self) -> str:
        """Get status string (PASS/FAIL)."""
        return "✅ PASS" if self.passed else "❌ FAIL"
    
    @property
    def not_preferred(self) -> int:
        """Get count of non-preferred sources."""
        return self.total - self.preferred
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "status": self.status,
            "total": self.total,
            "preferred": self.preferred,
            "not_preferred": self.not_preferred,
            "ratio": self.ratio,
            "min_ratio": self.min_ratio,
            "sources": self.sources,
        }
    
    def to_markdown(self, include_details: bool = True, max_sources: int = 10) -> str:
        """
        Generate markdown report.
        
        Args:
            include_details: Include per-source details
            max_sources: Maximum number of sources to show in details
            
        Returns:
            Markdown-formatted string
        """
        lines = [
            f"### Evaluation — Preferred Domains ({self.status})",
            "",
            f"- **Total sources**: {self.total}",
            f"- **Preferred sources**: {self.preferred}",
            f"- **Non-preferred sources**: {self.not_preferred}",
            f"- **Ratio**: {self.ratio:.1%}",
            f"- **Threshold**: {self.min_ratio:.0%}",
            "",
        ]
        
        if include_details and self.sources:
            lines.append("**Source Details:**")
            lines.append("")
            
            sources_to_show = self.sources[:max_sources]
            for source in sources_to_show:
                url = source.get("url", "")
                domain = source.get("domain", "")
                is_preferred = source.get("is_preferred", False)
                status_icon = "✅" if is_preferred else "❌"
                
                lines.append(f"- {status_icon} `{domain}` — {url}")
            
            if len(self.sources) > max_sources:
                remaining = len(self.sources) - max_sources
                lines.append(f"- ... and {remaining} more source(s)")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def to_html(self, include_details: bool = True, max_sources: int = 10) -> str:
        """
        Generate HTML report.
        
        Args:
            include_details: Include per-source details
            max_sources: Maximum number of sources to show
            
        Returns:
            HTML-formatted string
        """
        status_color = "#10b981" if self.passed else "#ef4444"
        
        html = f"""
<div style="border: 2px solid {status_color}; border-radius: 8px; padding: 16px; margin: 10px 0; background: #f9fafb;">
    <h3 style="margin-top: 0; color: {status_color};">
        Evaluation — Preferred Domains {self.status}
    </h3>
    
    <table style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 4px;"><strong>Total sources:</strong></td>
            <td style="padding: 4px;">{self.total}</td>
        </tr>
        <tr>
            <td style="padding: 4px;"><strong>Preferred sources:</strong></td>
            <td style="padding: 4px; color: #10b981;">{self.preferred}</td>
        </tr>
        <tr>
            <td style="padding: 4px;"><strong>Non-preferred sources:</strong></td>
            <td style="padding: 4px; color: #ef4444;">{self.not_preferred}</td>
        </tr>
        <tr>
            <td style="padding: 4px;"><strong>Ratio:</strong></td>
            <td style="padding: 4px;">{self.ratio:.1%}</td>
        </tr>
        <tr>
            <td style="padding: 4px;"><strong>Threshold:</strong></td>
            <td style="padding: 4px;">{self.min_ratio:.0%}</td>
        </tr>
    </table>
"""
        
        if include_details and self.sources:
            html += """
    <h4 style="margin-top: 16px; margin-bottom: 8px;">Source Details:</h4>
    <ul style="list-style: none; padding-left: 0;">
"""
            sources_to_show = self.sources[:max_sources]
            for source in sources_to_show:
                url = source.get("url", "")
                domain = source.get("domain", "")
                is_preferred = source.get("is_preferred", False)
                status_icon = "✅" if is_preferred else "❌"
                
                html += f"""
        <li style="margin: 4px 0;">
            {status_icon} <code>{domain}</code> — <a href="{url}" target="_blank">{url[:60]}...</a>
        </li>
"""
            
            if len(self.sources) > max_sources:
                remaining = len(self.sources) - max_sources
                html += f"""
        <li style="margin: 4px 0; font-style: italic;">
            ... and {remaining} more source(s)
        </li>
"""
            
            html += """
    </ul>
"""
        
        html += """
</div>
"""
        return html
    
    def __str__(self) -> str:
        """String representation."""
        return self.to_markdown(include_details=False)
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"EvaluationResult(passed={self.passed}, total={self.total}, "
            f"preferred={self.preferred}, ratio={self.ratio:.2%})"
        )


def compute_domain_metrics(results: list[EvaluationResult]) -> dict[str, Any]:
    """
    Compute aggregate metrics across multiple evaluation results.
    
    Args:
        results: List of EvaluationResult objects
        
    Returns:
        Dictionary with aggregate metrics
        
    Examples:
        >>> r1 = EvaluationResult(True, 10, 8, 0.8, 0.4, [])
        >>> r2 = EvaluationResult(False, 10, 3, 0.3, 0.4, [])
        >>> metrics = compute_domain_metrics([r1, r2])
        >>> metrics['pass_rate']
        0.5
    """
    if not results:
        return {
            "num_evaluations": 0,
            "pass_rate": 0.0,
            "avg_ratio": 0.0,
            "total_sources": 0,
            "total_preferred": 0,
        }
    
    num_passed = sum(1 for r in results if r.passed)
    total_sources = sum(r.total for r in results)
    total_preferred = sum(r.preferred for r in results)
    avg_ratio = sum(r.ratio for r in results) / len(results)
    
    return {
        "num_evaluations": len(results),
        "num_passed": num_passed,
        "num_failed": len(results) - num_passed,
        "pass_rate": num_passed / len(results),
        "avg_ratio": avg_ratio,
        "total_sources": total_sources,
        "total_preferred": total_preferred,
        "overall_ratio": total_preferred / total_sources if total_sources > 0 else 0.0,
    }
