#!/usr/bin/env python3
"""
Enhanced CLI entry point for the reflection-based chart generation workflow.

Features:
- Enhanced reflection prompt with structured critique framework
- Configurable iterative refinement (1-N iterations)
- Code persistence with optional final code saving
- Progress tracking and detailed output
- Backward compatible with original run_chart_workflow.py
"""

from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from reflection.chart_workflow import ChartWorkflowConfig, run_reflection_workflow
from dotenv import load_dotenv


def print_banner(text: str, char: str = "=") -> None:
    """Print a formatted banner."""
    width = 80
    print(f"\n{char * width}")
    print(f"  {text}")
    print(f"{char * width}\n")


def print_progress(step: str, detail: str = "") -> None:
    """Print a progress indicator."""
    if detail:
        print(f"⚙️  {step}: {detail}")
    else:
        print(f"⚙️  {step}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="run-enhanced-chart-workflow",
        description=textwrap.dedent("""
            Generate and iteratively refine charts using the enhanced reflection workflow.
            
            Features:
            • Structured critique framework (Tufte, Cleveland-McGill principles)
            • Configurable iteration count (1-N refinement rounds)
            • Code persistence (save final executable Python code)
            • Convergence detection (early stopping when no improvements)
            • Auto-generated instructions (when not provided)
        """),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              # Basic usage with auto-generated instruction
              %(prog)s data/sales.csv
              
              # Specify custom instruction and 3 iterations
              %(prog)s data/sales.csv "Show sales trends over time" --max-iterations 3
              
              # Use Claude for reflection, save to custom directory
              %(prog)s data/sales.csv --reflection-model claude-3-5-sonnet-20241022 \\
                  --output-dir ./charts --image-basename sales_analysis
              
              # Force all iterations (no early stopping)
              %(prog)s data/sales.csv --max-iterations 4 --no-stop-on-convergence
        """),
    )
    
    # Required arguments
    parser.add_argument(
        "dataset",
        help="Path to a CSV file to analyze and visualize.",
    )
    parser.add_argument(
        "instruction",
        nargs="?",
        default=None,
        help=textwrap.dedent("""
            Natural language description of the desired visualization.
            When omitted, an instruction is auto-generated from the dataset.
        """),
    )
    
    # Model configuration
    model_group = parser.add_argument_group("Model Configuration")
    model_group.add_argument(
        "--generation-model",
        default="gpt-4o-mini",
        help="Model for initial code generation (default: gpt-4o-mini).",
    )
    model_group.add_argument(
        "--reflection-model",
        default="gpt-4o",
        help=textwrap.dedent("""
            Model for visual reflection and critique (default: gpt-4o).
            Recommended: gpt-4o, claude-3-5-sonnet-20241022 (vision models).
        """),
    )
    
    # Output configuration
    output_group = parser.add_argument_group("Output Configuration")
    output_group.add_argument(
        "--image-basename",
        default="chart",
        help="Basename for generated chart files (default: chart).",
    )
    output_group.add_argument(
        "--output-dir",
        default="./charts",
        help="Directory for generated charts and code (default: ./charts).",
    )
    output_group.add_argument(
        "--no-save-final-code",
        dest="save_final_code",
        action="store_false",
        help="Skip saving the final chart code to disk.",
    )
    
    # Workflow configuration
    workflow_group = parser.add_argument_group("Workflow Configuration")
    workflow_group.add_argument(
        "--sample-rows",
        type=int,
        default=5,
        help="Number of sample rows to include in prompts (default: 5).",
    )
    workflow_group.add_argument(
        "--max-iterations",
        type=int,
        default=2,
        help=textwrap.dedent("""
            Maximum refinement iterations including initial draft (default: 2).
            Examples: 1 (no refinement), 2 (one refinement), 3+ (multiple rounds).
        """),
    )
    workflow_group.add_argument(
        "--no-stop-on-convergence",
        dest="stop_on_convergence",
        action="store_false",
        help=textwrap.dedent("""
            Force all iterations even when reflection converges early.
            By default, stops when code unchanged or no feedback.
        """),
    )
    
    # Display options
    display_group = parser.add_argument_group("Display Options")
    display_group.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed progress and intermediate outputs.",
    )
    display_group.add_argument(
        "--show-code",
        action="store_true",
        help="Display generated code for each iteration.",
    )
    
    parser.set_defaults(stop_on_convergence=True, save_final_code=True)
    return parser.parse_args()


def display_iteration_summary(artifacts, verbose: bool = False, show_code: bool = False) -> None:
    """Display a summary of all iterations."""
    print_banner("Iteration Summary", "-")
    
    for iteration in artifacts.iterations:
        feedback_display = iteration.feedback if iteration.feedback else "n/a"
        
        print(f"\n📊 Iteration {iteration.iteration}")
        print(f"   Chart: {iteration.chart_path}")
        
        # Display chart description
        if iteration.description:
            print(f"   📋 Description: {iteration.description}")
        
        print(f"   Code length: {len(iteration.code)} characters")
        
        if iteration.feedback:
            print(f"   Feedback: {feedback_display[:200]}{'...' if len(feedback_display) > 200 else ''}")
        else:
            print(f"   Feedback: Initial generation (no reflection)")
        
        if show_code:
            print(f"\n   --- Code Preview (first 300 chars) ---")
            print(textwrap.indent(iteration.code[:300], "   "))
            if len(iteration.code) > 300:
                print("   ...")
        
        if verbose and iteration.globals_namespace:
            print(f"   Globals: {list(iteration.globals_namespace.keys())[:5]}")


def display_final_summary(artifacts, config: ChartWorkflowConfig) -> None:
    """Display final workflow summary."""
    print_banner("Workflow Complete ✅")
    
    print(f"📈 Final Results:")
    print(f"   Total iterations: {len(artifacts.iterations)}")
    print(f"   Max allowed: {config.max_iterations}")
    print(f"   Early stopping: {'enabled' if config.stop_on_convergence else 'disabled'}")
    print()
    
    print(f"📁 Output Files:")
    for iteration in artifacts.iterations:
        print(f"   • {iteration.chart_path.name}")
    
    if artifacts.final_code_path:
        print(f"   • {artifacts.final_code_path.name} (executable Python code)")
        # Descriptions file has same basename
        descriptions_file = artifacts.final_code_path.parent / f"{config.image_basename}_descriptions.md"
        if descriptions_file.exists():
            print(f"   • {descriptions_file.name} (chart descriptions and feedback)")
    print()
    
    print(f"🎯 Final Chart: {artifacts.iterations[-1].chart_path}")
    if artifacts.iterations[-1].description:
        print(f"📋 Chart Type: {artifacts.iterations[-1].description}")
    if artifacts.final_code_path:
        print(f"💾 Final Code: {artifacts.final_code_path}")
    print()
    
    print(f"📝 Instruction Used:")
    print(textwrap.indent(artifacts.instruction, "   "))


def main() -> None:
    """Main entry point for the enhanced chart workflow."""
    # Load environment variables
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    
    args = parse_args()
    
    print_banner("Enhanced Chart Workflow with Structured Reflection")
    
    # Display configuration
    print("🔧 Configuration:")
    print(f"   Dataset: {args.dataset}")
    print(f"   Instruction: {args.instruction or '(auto-generated)'}")
    print(f"   Generation model: {args.generation_model}")
    print(f"   Reflection model: {args.reflection_model}")
    print(f"   Max iterations: {args.max_iterations}")
    print(f"   Stop on convergence: {args.stop_on_convergence}")
    print(f"   Output directory: {args.output_dir}")
    print(f"   Save final code: {args.save_final_code}")
    print()
    
    # Validate dataset exists
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"❌ Error: Dataset not found: {args.dataset}")
        sys.exit(1)
    
    # Create configuration
    config = ChartWorkflowConfig(
        generation_model=args.generation_model,
        reflection_model=args.reflection_model,
        image_basename=args.image_basename,
        output_dir=Path(args.output_dir),
        sample_rows=args.sample_rows,
        max_iterations=args.max_iterations,
        stop_on_convergence=args.stop_on_convergence,
        save_final_code=args.save_final_code,
    )
    
    # Run workflow
    try:
        print_progress("Loading dataset", args.dataset)
        
        if args.instruction:
            print_progress("Using provided instruction")
        else:
            print_progress("Generating instruction from dataset structure")
        
        print_progress("Starting workflow", f"{args.max_iterations} iteration(s) max")
        print()
        
        artifacts = run_reflection_workflow(
            dataset=args.dataset,
            instruction=args.instruction,
            config=config,
        )
        
        # Display results
        display_iteration_summary(artifacts, verbose=args.verbose, show_code=args.show_code)
        display_final_summary(artifacts, config)
        
        # Success message
        print("✨ Enhanced reflection workflow completed successfully!")
        print()
        print("💡 The enhanced reflection prompt provides structured critique across:")
        print("   1. Chart type appropriateness")
        print("   2. Perceptual accuracy & truthfulness")
        print("   3. Clarity & readability")
        print("   4. Data-ink ratio (Tufte's principle)")
        print("   5. Statistical integrity")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Error: {type(e).__name__}: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
