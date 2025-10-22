#!/usr/bin/env python3
"""
Test script to preview auto-generated prompts without running the full workflow.
This helps verify that the prompting module generates sensible instructions.
"""

from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[3]  # Go up 3 levels: scripts -> chart_workflow -> tests -> root
sys.path.insert(0, str(project_root))

import pandas as pd
from reflection.chart_workflow.prompting import suggest_initial_instruction


def print_section(title: str, char: str = "=") -> None:
    """Print a formatted section header."""
    print(f"\n{char * 80}")
    print(f"  {title}")
    print(f"{char * 80}\n")


def test_dataset(dataset_path: str, description: str) -> None:
    """Test prompt generation for a dataset."""
    print_section(f"Dataset: {dataset_path}", "-")
    print(f"Description: {description}\n")
    
    # Load dataset
    try:
        if dataset_path.endswith('.tsv'):
            df = pd.read_csv(dataset_path, sep='\t', nrows=1000)  # Sample for speed
        else:
            df = pd.read_csv(dataset_path, nrows=1000)
        
        print(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
        print(f"Columns: {', '.join(df.columns.tolist()[:10])}")
        if len(df.columns) > 10:
            print(f"         ... and {len(df.columns) - 10} more")
        print()
        
        # Detect column types
        print("Column Analysis:")
        print(f"  • Numeric columns: {sum(1 for c in df.columns if pd.api.types.is_numeric_dtype(df[c]))}")
        print(f"  • Object/categorical columns: {sum(1 for c in df.columns if pd.api.types.is_object_dtype(df[c]))}")
        print()
        
        # Generate instruction
        instruction = suggest_initial_instruction(df)
        
        print("AUTO-GENERATED INSTRUCTION:")
        print("-" * 80)
        print(instruction)
        print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Test prompt generation for different datasets."""
    print_section("Auto-Generated Prompt Testing")
    print("This script tests the prompting module's ability to generate")
    print("sensible visualization instructions based on dataset characteristics.\n")
    
    # Test 1: Genomic data (splice sites)
    test_dataset(
        "data/splice_sites_enhanced.tsv",
        "Complex genomic dataset with splice site annotations"
    )
    
    # Test 2: Simple temporal data (coffee sales)
    test_dataset(
        "reflection/M2_UGL_1/coffee_sales.csv",
        "Simple temporal dataset with sales transactions"
    )
    
    # Summary
    print_section("Summary")
    print("Review the auto-generated instructions above to verify:")
    print("  ✓ Instructions are specific to the dataset")
    print("  ✓ Instructions suggest appropriate chart types")
    print("  ✓ Instructions reference actual column names")
    print("  ✓ Genomic data gets domain-specific suggestions")
    print("  ✓ General data gets exploratory suggestions")
    print()
    print("To test the full workflow with auto-generated prompts:")
    print("  ./test_auto_prompt.sh")
    print()


if __name__ == "__main__":
    main()
