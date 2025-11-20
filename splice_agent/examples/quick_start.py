"""Quick Start Examples for Splice Agent.

This script demonstrates basic usage patterns for splice site analysis.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from splice_agent import create_dataset
from splice_agent.splice_analysis import (
    generate_analysis_insight,
    generate_exploratory_insight,
    list_available_analyses,
)

# Load environment variables
load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "splice_sites_enhanced.tsv"
OUTPUT_DIR = PROJECT_ROOT / "output" / "quick_start"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def example_1_list_analyses():
    """Example 1: List available analysis templates."""
    print("=" * 60)
    print("Example 1: Available Analysis Templates")
    print("=" * 60)
    
    analyses = list_available_analyses()
    print(f"\nFound {len(analyses)} predefined analyses:\n")
    for analysis in analyses:
        print(f"  - {analysis}")
    print()


def example_2_template_analysis():
    """Example 2: Generate analysis using template."""
    print("=" * 60)
    print("Example 2: Template-Based Analysis")
    print("=" * 60)
    
    # Load dataset
    print(f"\nLoading dataset: {DATA_PATH}")
    dataset = create_dataset(str(DATA_PATH))
    
    # Initialize OpenAI client
    client = OpenAI()
    
    # Generate analysis
    print("\nGenerating 'high_alternative_splicing' analysis...")
    result = generate_analysis_insight(
        dataset=dataset,
        analysis_type="high_alternative_splicing",
        client=client,
        model="gpt-4o-mini"
    )
    
    print(f"\nTitle: {result['title']}")
    print(f"Description: {result['description']}")
    print(f"Library: {result['library']}")
    print(f"Chart Type: {result['chart_type']}")
    
    # Save code
    output_file = OUTPUT_DIR / "high_alternative_splicing.py"
    with open(output_file, "w") as f:
        f.write(f"# {result['title']}\n")
        f.write(f"# {result['description']}\n\n")
        f.write(result["chart_code"])
    
    print(f"\nSaved code to: {output_file}")
    print("\nTo execute:")
    print(f"  python {output_file}")
    
    dataset.close()


def example_3_exploratory_analysis():
    """Example 3: Exploratory analysis with custom question."""
    print("\n" + "=" * 60)
    print("Example 3: Exploratory Analysis")
    print("=" * 60)
    
    # Load dataset
    print(f"\nLoading dataset: {DATA_PATH}")
    dataset = create_dataset(str(DATA_PATH))
    
    # Initialize OpenAI client
    client = OpenAI()
    
    # Custom research question
    question = "What is the distribution of splice sites across chromosomes?"
    
    print(f"\nResearch Question: {question}")
    print("\nGenerating exploratory analysis...")
    
    result = generate_exploratory_insight(
        dataset=dataset,
        research_question=question,
        client=client,
        model="gpt-4o-mini"
    )
    
    print(f"\nReasoning: {result['reasoning']}")
    print(f"\nKey Insights:")
    for insight in result["key_insights"]:
        print(f"  - {insight}")
    
    # Save code
    output_file = OUTPUT_DIR / "exploratory_analysis.py"
    with open(output_file, "w") as f:
        f.write(f"# Research Question: {question}\n")
        f.write(f"# Reasoning: {result['reasoning']}\n\n")
        f.write(result["chart_code"])
    
    print(f"\nSaved code to: {output_file}")
    
    dataset.close()


def example_4_multiple_analyses():
    """Example 4: Generate multiple analyses."""
    print("\n" + "=" * 60)
    print("Example 4: Batch Analysis")
    print("=" * 60)
    
    # Load dataset
    print(f"\nLoading dataset: {DATA_PATH}")
    dataset = create_dataset(str(DATA_PATH))
    
    # Initialize OpenAI client
    client = OpenAI()
    
    # Analyses to generate
    analyses_to_run = [
        "high_alternative_splicing",
        "splice_site_genomic_view",
        "strand_bias"
    ]
    
    print(f"\nGenerating {len(analyses_to_run)} analyses...")
    
    for analysis_type in analyses_to_run:
        print(f"\n  Processing: {analysis_type}...")
        
        result = generate_analysis_insight(
            dataset=dataset,
            analysis_type=analysis_type,
            client=client,
            model="gpt-4o-mini"
        )
        
        # Save code
        output_file = OUTPUT_DIR / f"{analysis_type}.py"
        with open(output_file, "w") as f:
            f.write(f"# {result['title']}\n")
            f.write(f"# {result['description']}\n\n")
            f.write(result["chart_code"])
        
        print(f"    Saved: {output_file}")
    
    print(f"\nAll analyses saved to: {OUTPUT_DIR}")
    
    dataset.close()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("SPLICE AGENT - QUICK START EXAMPLES")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\nError: OPENAI_API_KEY not set")
        print("Please set it in your .env file or environment")
        return
    
    # Check for data file
    if not DATA_PATH.exists():
        print(f"\nError: Data file not found: {DATA_PATH}")
        print("Please add your splice site dataset")
        return
    
    # Run examples
    try:
        example_1_list_analyses()
        example_2_template_analysis()
        example_3_exploratory_analysis()
        example_4_multiple_analyses()
        
        print("\n" + "=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\nGenerated files in: {OUTPUT_DIR}")
        print("\nNext steps:")
        print("  1. Review the generated code")
        print("  2. Execute the scripts to generate charts")
        print("  3. Customize the code as needed")
        print("  4. Try your own research questions!")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
