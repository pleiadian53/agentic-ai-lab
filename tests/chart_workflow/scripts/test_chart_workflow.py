#!/usr/bin/env python3
"""
Test script for the reflection-based chart workflow.

This script tests the chart_workflow package with datasets of varying complexity:
1. Simple dataset: Coffee sales (temporal, categorical)
2. Complex dataset: Genomic splice sites (multi-dimensional, biological)

The workflow uses the reflection pattern to iteratively improve chart quality.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import NamedTuple

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from reflection.chart_workflow import ChartWorkflowConfig, run_reflection_workflow
from dotenv import load_dotenv


class TestCase(NamedTuple):
    """Defines a test case for the chart workflow."""
    name: str
    dataset: str
    instruction: str
    description: str
    generation_model: str = "gpt-5.0-mini"
    reflection_model: str = "o4-mini"


def print_section(title: str, char: str = "=") -> None:
    """Print a formatted section header."""
    print(f"\n{char * 80}")
    print(f"  {title}")
    print(f"{char * 80}\n")


def run_test_case(test: TestCase, output_dir: Path) -> None:
    """Execute a single test case."""
    print_section(f"Test Case: {test.name}", "-")
    print(f"Description: {test.description}")
    print(f"Dataset: {test.dataset}")
    print(f"Instruction: {test.instruction}")
    print(f"Generation Model: {test.generation_model}")
    print(f"Reflection Model: {test.reflection_model}")
    print()

    # Create test-specific output directory
    test_output_dir = output_dir / test.name.lower().replace(" ", "_")
    test_output_dir.mkdir(parents=True, exist_ok=True)

    # Configure workflow
    config = ChartWorkflowConfig(
        generation_model=test.generation_model,
        reflection_model=test.reflection_model,
        image_basename="chart",
        output_dir=test_output_dir,
        sample_rows=5,
    )

    try:
        # Run workflow
        print("🚀 Running workflow...")
        artifacts = run_reflection_workflow(
            dataset=test.dataset,
            instruction=test.instruction,
            config=config,
        )

        # Print results
        print("\n✅ Workflow completed successfully!")
        print(f"   • V1 code: {len(artifacts.code_v1)} characters")
        print(f"   • V1 chart: {artifacts.chart_v1}")
        print(f"   • Feedback: {artifacts.feedback[:100]}..." if len(artifacts.feedback) > 100 else f"   • Feedback: {artifacts.feedback}")
        print(f"   • V2 code: {len(artifacts.code_v2)} characters")
        print(f"   • V2 chart: {artifacts.chart_v2}")
        print(f"   • Output directory: {test_output_dir}")
        
        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main() -> None:
    """Run all test cases."""
    # Load environment variables
    load_dotenv(project_root / ".env")

    print_section("Chart Workflow Testing Suite")
    print("Testing the reflection-based chart generation workflow")
    print("with datasets of varying complexity.\n")

    # Define output directory
    output_dir = project_root / "tests" / "chart_workflow" / "outputs" / "comprehensive"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}\n")

    # Define test cases
    test_cases = [
        # ===== SIMPLE DATASET: Coffee Sales =====
        TestCase(
            name="Coffee Sales - Quarterly Comparison",
            dataset=str(project_root / "reflection/M2_UGL_1/coffee_sales.csv"),
            instruction="Create a bar chart comparing Q1 coffee sales between 2024 and 2025. Use different colors for each year and add a legend.",
            description="Simple temporal comparison with categorical data",
        ),
        
        TestCase(
            name="Coffee Sales - Revenue Trend",
            dataset=str(project_root / "reflection/M2_UGL_1/coffee_sales.csv"),
            instruction="Create a line chart showing daily revenue trends over time. Add a 7-day moving average to smooth the trend.",
            description="Time series analysis with trend smoothing",
        ),
        
        TestCase(
            name="Coffee Sales - Product Distribution",
            dataset=str(project_root / "reflection/M2_UGL_1/coffee_sales.csv"),
            instruction="Create a pie chart showing the distribution of sales by coffee type. Include percentages and a legend.",
            description="Categorical distribution visualization",
        ),
        
        # ===== COMPLEX DATASET: Genomic Splice Sites =====
        TestCase(
            name="Splice Sites - Type Distribution",
            dataset=str(project_root / "data/splice_sites_enhanced.tsv"),
            instruction="Create a bar chart showing the count of donor vs acceptor splice sites by chromosome. Use a grouped bar chart with different colors for each site type.",
            description="Multi-dimensional categorical comparison (genomic data)",
        ),
        
        TestCase(
            name="Splice Sites - Strand Distribution",
            dataset=str(project_root / "data/splice_sites_enhanced.tsv"),
            instruction="Create a stacked bar chart showing the distribution of splice site types (donor/acceptor) across different strands (+ and -). Include percentages.",
            description="Nested categorical relationships in genomic data",
        ),
        
        TestCase(
            name="Splice Sites - Positional Analysis",
            dataset=str(project_root / "data/splice_sites_enhanced.tsv"),
            instruction="Create a scatter plot showing the genomic positions of splice sites, colored by site type (donor/acceptor). Use chromosome 1 data only for clarity.",
            description="Spatial distribution of genomic features",
        ),
        
        TestCase(
            name="Splice Sites - Gene Biotype",
            dataset=str(project_root / "data/splice_sites_enhanced.tsv"),
            instruction="Create a horizontal bar chart showing the top 10 gene biotypes by number of splice sites. Sort from highest to lowest.",
            description="Ranked categorical analysis of biological features",
        ),
    ]

    # Run test cases
    results = []
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"Running Test {i}/{len(test_cases)}")
        print(f"{'=' * 80}")
        
        success = run_test_case(test, output_dir)
        results.append((test.name, success))
        
        if not success:
            print(f"\n⚠️  Test '{test.name}' failed. Continuing with remaining tests...")

    # Print summary
    print_section("Test Summary")
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    print(f"Total tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print()
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n📁 All outputs saved to: {output_dir}")
    print("\nReview the generated charts to assess quality and iterative improvements!")


if __name__ == "__main__":
    main()
