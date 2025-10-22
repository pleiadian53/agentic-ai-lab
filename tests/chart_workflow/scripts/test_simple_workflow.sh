#!/bin/bash
# Quick test script for chart workflow with simple and complex datasets

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "  Chart Workflow Quick Test"
echo "=========================================="
echo ""

# Activate the conda environment
echo "🔧 Activating agentic-ai environment..."
eval "$(conda shell.bash hook)"
mamba activate agentic-ai
echo "✅ Environment activated: $(which python3)"
echo ""

# Create output directory
OUTPUT_DIR="tests/chart_workflow/outputs/quick_test"
mkdir -p "$OUTPUT_DIR"

# Test 1: Simple dataset (Coffee Sales)
echo "📊 Test 1: Coffee Sales - Quarterly Comparison"
echo "Dataset: reflection/M2_UGL_1/coffee_sales.csv"
echo "----------------------------------------"
python scripts/run_chart_workflow.py \
    "reflection/M2_UGL_1/coffee_sales.csv" \
    "Create a bar chart comparing Q1 coffee sales between 2024 and 2025" \
    --generation-model "gpt-5.0-mini" \
    --reflection-model "o4-mini" \
    --image-basename "coffee_q1_comparison" \
    --output-dir "$OUTPUT_DIR/coffee_sales"

echo ""
echo "✅ Test 1 completed!"
echo ""

# Test 2: Complex dataset (Splice Sites)
echo "📊 Test 2: Splice Sites - Type Distribution"
echo "Dataset: data/splice_sites_enhanced.tsv"
echo "----------------------------------------"
python scripts/run_chart_workflow.py \
    "data/splice_sites_enhanced.tsv" \
    "Create a bar chart showing the count of donor vs acceptor splice sites by chromosome" \
    --generation-model "gpt-5.0-mini" \
    --reflection-model "o4-mini" \
    --image-basename "splice_sites_distribution" \
    --output-dir "$OUTPUT_DIR/splice_sites"

echo ""
echo "✅ Test 2 completed!"
echo ""

# Summary
echo "=========================================="
echo "  All Tests Completed!"
echo "=========================================="
echo ""
echo "📁 Output directory: $OUTPUT_DIR"
echo ""
echo "Generated charts:"
ls -lh "$OUTPUT_DIR"/*/*.png 2>/dev/null || echo "  (No PNG files found - check for errors above)"
echo ""
echo "Review the charts to assess:"
echo "  • V1 (initial generation)"
echo "  • V2 (after reflection and refinement)"
echo "  • Quality improvements from reflection"
