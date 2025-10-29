#!/usr/bin/env python3
"""
Test script to preview the enhanced reflection prompt.
Demonstrates the structured critique framework without requiring LLM calls.
"""

from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from reflection.chart_workflow.llm import build_reflection_prompt, PromptContext


def print_section(title: str, char: str = "=") -> None:
    """Print a formatted section header."""
    print(f"\n{char * 80}")
    print(f"  {title}")
    print(f"{char * 80}\n")


def main():
    """Preview the enhanced reflection prompt structure."""
    print_section("Enhanced Reflection Prompt Preview")
    print("This demonstrates the structured critique framework added to guide")
    print("the LLM in performing systematic visual evaluation.\n")
    
    # Create sample context
    sample_schema = """
- date: datetime64[ns]
- sales: float64
- region: object
- product_category: object
    """.strip()
    
    sample_rows_json = """
[
  {"date": "2024-01-01", "sales": 1500.0, "region": "North", "product_category": "Electronics"},
  {"date": "2024-01-02", "sales": 1800.0, "region": "South", "product_category": "Clothing"},
  {"date": "2024-01-03", "sales": 1200.0, "region": "East", "product_category": "Electronics"}
]
    """.strip()
    
    context = PromptContext(
        schema=sample_schema,
        sample_rows_json=sample_rows_json,
    )
    
    # Sample instruction and code
    instruction = "Create a bar chart showing sales by region"
    original_code = """
import matplotlib.pyplot as plt
df.groupby('region')['sales'].sum().plot(kind='bar')
plt.title('Sales by Region')
plt.savefig('output.png', dpi=300)
plt.close()
    """.strip()
    
    # Build the prompt
    prompt = build_reflection_prompt(
        instruction=instruction,
        original_code=original_code,
        context=context,
        output_path="chart_v2.png",
    )
    
    print_section("Generated Reflection Prompt", "-")
    print(prompt)
    print()
    
    print_section("Key Enhancements")
    print("✓ Structured critique framework with 5 evaluation dimensions:")
    print("  1. Chart type appropriateness (data structure → visual encoding)")
    print("  2. Perceptual accuracy (truthful scales, aspect ratios)")
    print("  3. Clarity & readability (legible labels, accessible colors)")
    print("  4. Data-ink ratio (Tufte's principle: minimize clutter)")
    print("  5. Statistical integrity (error bars, outlier handling)")
    print()
    print("✓ References established design principles (Tufte, Cleveland-McGill)")
    print("✓ Provides specific guidance for common issues (overlapping labels, etc.)")
    print("✓ Maintains backward-compatible output format (JSON feedback + code)")
    print()
    
    print_section("Usage")
    print("This enhanced prompt is automatically used in the reflection workflow.")
    print("No code changes needed - just run your existing workflow:")
    print()
    print("  from reflection.chart_workflow import run_reflection_workflow")
    print("  artifacts = run_reflection_workflow(...)")
    print()
    print("The LLM will now perform more systematic visual critique.")
    print()


if __name__ == "__main__":
    main()
