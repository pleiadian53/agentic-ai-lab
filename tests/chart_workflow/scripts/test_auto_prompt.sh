#!/bin/bash
# Test auto-generated prompts for chart workflow

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "  Testing Auto-Generated Prompts"
echo "=========================================="
echo ""

# Activate environment
echo "🔧 Activating agentic-ai environment..."
eval "$(conda shell.bash hook)"
mamba activate agentic-ai
echo "✅ Environment activated"
echo ""

# Create output directory
OUTPUT_DIR="tests/chart_workflow/outputs/auto_prompt_test"
mkdir -p "$OUTPUT_DIR"

# Test 1: Auto-generated prompt (no instruction provided)
echo "=========================================="
echo "Test 1: AUTO-GENERATED PROMPT"
echo "=========================================="
echo "Dataset: data/splice_sites_enhanced.tsv"
echo "Instruction: [AUTO-GENERATED]"
echo ""

python3 scripts/run_chart_workflow.py \
    data/splice_sites_enhanced.tsv \
    --generation-model gpt-4o-mini \
    --reflection-model gpt-4o \
    --image-basename auto_generated \
    --output-dir "$OUTPUT_DIR/auto_generated"

echo ""
echo "✅ Test 1 completed!"
echo ""

# Test 2: User-specified prompt
echo "=========================================="
echo "Test 2: USER-SPECIFIED PROMPT"
echo "=========================================="
echo "Dataset: data/splice_sites_enhanced.tsv"
echo "Instruction: [USER-PROVIDED]"
echo ""

python3 scripts/run_chart_workflow.py \
    data/splice_sites_enhanced.tsv \
    "Create a bar chart showing the distribution of splice site types (donor vs acceptor) across different chromosomes. Use the top 10 chromosomes by count." \
    --generation-model gpt-4o-mini \
    --reflection-model gpt-4o \
    --image-basename user_specified \
    --output-dir "$OUTPUT_DIR/user_specified"

echo ""
echo "✅ Test 2 completed!"
echo ""

# Summary
echo "=========================================="
echo "  Test Summary"
echo "=========================================="
echo ""
echo "📁 Output directory: $OUTPUT_DIR"
echo ""
echo "Compare the results:"
echo "  • Auto-generated: $OUTPUT_DIR/auto_generated/"
echo "  • User-specified: $OUTPUT_DIR/user_specified/"
echo ""
echo "Review the 'Resolved instruction' output above to see:"
echo "  1. What instruction was auto-generated for Test 1"
echo "  2. How the user instruction was used in Test 2"
