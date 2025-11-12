"""
Utility functions for inspecting and displaying research agent outputs.

This module provides helper functions to visualize and analyze outputs from
reflection_and_rewrite() and other research agent functions.
"""

from IPython.display import display, HTML


def inspect_reflection_output(result: dict, max_length: int = 500):
    """
    Pretty-print the output from reflection_and_rewrite() for easy inspection.
    
    Args:
        result (dict): Output from reflection_and_rewrite() with keys 'reflection' and 'revised_report'
        max_length (int): Maximum characters to display for each section (default: 500)
    """
    # Extract sections
    reflection = result.get("reflection", "")
    revised_report = result.get("revised_report", "")
    
    # Truncate if needed
    reflection_display = reflection if len(reflection) <= max_length else reflection[:max_length] + "..."
    revised_display = revised_report if len(revised_report) <= max_length else revised_report[:max_length] + "..."
    
    # Create HTML output
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 900px;">
        <h2 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
            📊 Reflection & Revision Output
        </h2>
        
        <div style="margin: 20px 0;">
            <h3 style="color: #e74c3c; margin-bottom: 10px;">🔍 Reflection</h3>
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #e74c3c; border-radius: 4px;">
                <pre style="white-space: pre-wrap; margin: 0; font-size: 14px;">{reflection_display}</pre>
            </div>
            <p style="color: #7f8c8d; font-size: 12px; margin-top: 5px;">
                Length: {len(reflection)} characters
            </p>
        </div>
        
        <div style="margin: 20px 0;">
            <h3 style="color: #27ae60; margin-bottom: 10px;">✍️ Revised Report</h3>
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #27ae60; border-radius: 4px;">
                <pre style="white-space: pre-wrap; margin: 0; font-size: 14px;">{revised_display}</pre>
            </div>
            <p style="color: #7f8c8d; font-size: 12px; margin-top: 5px;">
                Length: {len(revised_report)} characters
            </p>
        </div>
        
        <div style="margin-top: 20px; padding: 10px; background-color: #ecf0f1; border-radius: 4px;">
            <strong>Summary:</strong>
            <ul style="margin: 5px 0;">
                <li>Reflection sections: {count_reflection_sections(reflection)}</li>
                <li>Revision improvement: {len(revised_report) - len(reflection)} chars difference</li>
            </ul>
        </div>
    </div>
    """
    
    display(HTML(html))
    
    # Also print full text option
    print("\n" + "="*80)
    print("💡 To see full text, use:")
    print("   print(result['reflection'])")
    print("   print(result['revised_report'])")
    print("="*80)


def count_reflection_sections(reflection: str) -> str:
    """
    Helper to count which reflection sections are present.
    
    Args:
        reflection (str): The reflection text to analyze
        
    Returns:
        str: Summary of found sections (e.g., "4/4 (Strengths, Limitations, ...)")
    """
    sections = ["strengths", "limitations", "suggestions", "opportunities"]
    found = [s.title() for s in sections if s.lower() in reflection.lower()]
    return f"{len(found)}/4 ({', '.join(found)})" if found else "0/4"


def inspect_reflection_simple(result: dict):
    """
    Simple text-based inspection of reflection output (no HTML).
    
    Args:
        result (dict): Output from reflection_and_rewrite()
    """
    print("="*80)
    print("🔍 REFLECTION")
    print("="*80)
    print(result["reflection"])
    print("\n" + "="*80)
    print("✍️ REVISED REPORT")
    print("="*80)
    print(result["revised_report"])
    print("\n" + "="*80)
    print(f"Stats: Reflection={len(result['reflection'])} chars, "
          f"Revised={len(result['revised_report'])} chars")
    print("="*80)


def compare_reports(original: str, result: dict):
    """
    Compare original report with revised version.
    
    Args:
        original (str): The original report text
        result (dict): Output from reflection_and_rewrite() containing revised report
    """
    revised = result["revised_report"]
    
    print("📊 Report Comparison")
    print("="*80)
    print(f"Original length:  {len(original):,} characters")
    print(f"Revised length:   {len(revised):,} characters")
    print(f"Change:           {len(revised) - len(original):+,} characters")
    
    if len(original) > 0:
        growth_pct = (len(revised) / len(original) - 1) * 100
        print(f"Growth:           {growth_pct:+.1f}%")
    
    print("="*80)


def display_research_report(report: str, title: str = "Research Report"):
    """
    Display a research report with nice formatting.
    
    Args:
        report (str): The report text to display
        title (str): Title for the display (default: "Research Report")
    """
    html = f"""
    <div style="font-family: Georgia, serif; max-width: 900px; margin: 20px 0;">
        <h2 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
            📚 {title}
        </h2>
        <div style="background-color: #ffffff; padding: 20px; border: 1px solid #ddd; border-radius: 4px; line-height: 1.6;">
            <pre style="white-space: pre-wrap; font-family: Georgia, serif; margin: 0; font-size: 15px;">{report}</pre>
        </div>
        <p style="color: #7f8c8d; font-size: 12px; margin-top: 10px;">
            Length: {len(report):,} characters | Words: ~{len(report.split()):,}
        </p>
    </div>
    """
    display(HTML(html))


def show_tool_usage_stats(messages: list):
    """
    Analyze and display tool usage statistics from a conversation.
    
    Args:
        messages (list): List of message dicts from the conversation
    """
    tool_calls = []
    tool_results = []
    
    for msg in messages:
        # Check for tool calls in assistant messages
        if isinstance(msg, dict):
            if msg.get("role") == "tool":
                tool_results.append(msg.get("name", "unknown"))
        else:
            # Handle ChatCompletionMessage objects
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for call in msg.tool_calls:
                    tool_calls.append(call.function.name)
    
    print("🛠️ Tool Usage Statistics")
    print("="*80)
    print(f"Total tool calls: {len(tool_calls)}")
    
    if tool_calls:
        from collections import Counter
        tool_counts = Counter(tool_calls)
        print("\nBreakdown:")
        for tool, count in tool_counts.most_common():
            print(f"  • {tool}: {count} call(s)")
    else:
        print("  No tools were called")
    
    print("="*80)
