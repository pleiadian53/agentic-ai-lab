"""
Output validation for research reports.

Detects common issues like editorial commentary, incomplete reports, 
and malformed content before saving.
"""

import re
from typing import Optional, Tuple


def validate_report_output(content: str, topic: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate that the output is a complete research report, not editorial commentary.
    
    Args:
        content: The generated report content
        topic: The research topic (for context)
        
    Returns:
        Tuple of (is_valid, error_message, suggested_fix)
        - is_valid: True if report appears valid
        - error_message: Description of the issue if invalid
        - suggested_fix: Suggestion for how to fix (if applicable)
    """
    
    if not content or len(content.strip()) < 100:
        return False, "Report is too short or empty", "Regenerate with more detailed instructions"
    
    # Check 1: Detect editorial commentary patterns
    editorial_patterns = [
        r"^Below is (?:an?|the) (?:integrated|edited|revised|improved)",
        r"^Here(?:'s| is) (?:an?|the) (?:edited|revised|improved|integrated)",
        r"You can treat this as",
        r"drop[- ]in replacement",
        r"with attention to:",
        r"^\*\*(?:Argumentative strength|Style uniformity|Accuracy)\*\*",
        r"then we can do a final",
        r"I(?:'ve| have) (?:edited|revised|improved|integrated)",
        r"The following (?:is|are) (?:edits|changes|improvements)",
    ]
    
    first_200_chars = content[:200].strip()
    
    for pattern in editorial_patterns:
        if re.search(pattern, first_200_chars, re.IGNORECASE | re.MULTILINE):
            return (
                False, 
                "Output appears to be editorial commentary rather than the final report",
                "Extract the actual report content after the commentary, or regenerate with stricter Editor agent instructions"
            )
    
    # Check 2: Report should start with title/heading or content, not meta-discussion
    meta_discussion_patterns = [
        r"^(?:Note|Important|Please note|FYI|Reminder):",
        r"^This (?:document|report|paper) (?:is|contains|provides)",
        r"^The purpose of this",
    ]
    
    for pattern in meta_discussion_patterns:
        if re.search(pattern, first_200_chars, re.IGNORECASE):
            return (
                False,
                "Output starts with meta-discussion instead of report content",
                "Remove preamble and extract the actual report"
            )
    
    # Check 3: Report should have substantial content (not just an outline)
    lines = content.split('\n')
    non_empty_lines = [l for l in lines if l.strip()]
    
    if len(non_empty_lines) < 20:
        return False, "Report appears to be just an outline or summary", "Regenerate with instructions for full content"
    
    # Check 4: Detect if report starts mid-section (like "Section 10")
    section_start_pattern = r"^##\s+(?:Section\s+)?(\d+)\."
    match = re.search(section_start_pattern, content[:500], re.MULTILINE)
    
    if match:
        section_num = int(match.group(1))
        if section_num > 3:  # Starting at section 4+ is suspicious
            return (
                False,
                f"Report appears to start at Section {section_num}, suggesting earlier sections are missing",
                "Regenerate to get complete report from the beginning"
            )
    
    # Check 5: LaTeX documents should have proper structure
    if '\\documentclass' in content or '\\begin{document}' in content:
        if '\\documentclass' in content and '\\begin{document}' not in content:
            return False, "LaTeX document missing \\begin{document}", "Complete LaTeX structure required"
        if '\\begin{document}' in content and '\\end{document}' not in content:
            return False, "LaTeX document missing \\end{document}", "Complete LaTeX structure required"
    
    # Check 6: Markdown reports should have at least one heading
    if '\\documentclass' not in content:  # Not LaTeX
        has_heading = bool(re.search(r'^#+ ', content, re.MULTILINE))
        if not has_heading:
            return False, "Markdown report has no section headings", "Add proper structure with headings"
    
    # All checks passed
    return True, None, None


def extract_report_from_commentary(content: str) -> Optional[str]:
    """
    Attempt to extract the actual report from editorial commentary.
    
    This is a best-effort extraction for common patterns where the Editor
    returns commentary followed by the actual report.
    
    Args:
        content: The full output including commentary
        
    Returns:
        Extracted report content, or None if extraction fails
    """
    
    # Pattern 1: Look for separator lines (---, ===, etc.)
    separator_pattern = r'\n(?:---|===|___){3,}\n'
    parts = re.split(separator_pattern, content)
    
    if len(parts) > 1:
        # Take the largest part (likely the actual report)
        largest_part = max(parts, key=len)
        if len(largest_part) > len(content) * 0.5:  # At least 50% of original
            return largest_part.strip()
    
    # Pattern 2: Look for "## 1." or "# Introduction" as start of actual report
    report_start_patterns = [
        r'\n##\s+1\.',  # Section 1
        r'\n#\s+(?:Introduction|Abstract|Executive Summary)',  # Common first sections
        r'\n\\documentclass',  # LaTeX start
    ]
    
    for pattern in report_start_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            # Extract from this point onward
            extracted = content[match.start():].strip()
            if len(extracted) > 500:  # Substantial content
                return extracted
    
    # Pattern 3: Remove first paragraph if it looks like commentary
    paragraphs = content.split('\n\n')
    if len(paragraphs) > 2:
        first_para = paragraphs[0].lower()
        if any(word in first_para for word in ['below is', 'here is', 'edited version', 'integrated']):
            # Skip first paragraph
            return '\n\n'.join(paragraphs[1:]).strip()
    
    # Extraction failed
    return None


def validate_and_fix_report(content: str, topic: str, auto_fix: bool = True) -> Tuple[str, list[str]]:
    """
    Validate report and attempt automatic fixes if enabled.
    
    Args:
        content: The generated report content
        topic: The research topic
        auto_fix: Whether to attempt automatic fixes
        
    Returns:
        Tuple of (fixed_content, warnings)
        - fixed_content: The validated/fixed content
        - warnings: List of warning messages about issues found/fixed
    """
    
    warnings = []
    
    # Validate
    is_valid, error_msg, suggestion = validate_report_output(content, topic)
    
    if is_valid:
        return content, warnings
    
    # Not valid - log the issue
    warnings.append(f"⚠️  Validation issue: {error_msg}")
    
    if not auto_fix:
        warnings.append(f"💡 Suggestion: {suggestion}")
        return content, warnings
    
    # Attempt automatic fix
    warnings.append("🔧 Attempting automatic fix...")
    
    extracted = extract_report_from_commentary(content)
    
    if extracted:
        # Re-validate the extracted content
        is_valid_after, _, _ = validate_report_output(extracted, topic)
        
        if is_valid_after:
            warnings.append("✅ Successfully extracted report from commentary")
            return extracted, warnings
        else:
            warnings.append("❌ Extraction failed validation - using original content")
            warnings.append(f"💡 Manual fix needed: {suggestion}")
            return content, warnings
    else:
        warnings.append("❌ Could not extract report automatically")
        warnings.append(f"💡 Manual fix needed: {suggestion}")
        return content, warnings
