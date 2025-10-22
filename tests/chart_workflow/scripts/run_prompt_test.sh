#!/bin/bash
# Wrapper to run prompt generation test with proper environment

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Activate environment
eval "$(conda shell.bash hook)"
mamba activate agentic-ai

# Run test
python3 test_prompt_generation.py
