#!/usr/bin/env python3
"""
CLI driver for the reflective essay writing research agent.

Features:
- Iterative draft-reflect-revise workflow
- Configurable models for each step
- Multiple refinement iterations
- Convergence detection
- Saves all drafts, feedback, and final essay
"""

from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from reflection.research_agent import ResearchAgentConfig, run_research_workflow
from dotenv import load_dotenv
import aisuite as ai


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
        prog="run-reflection-research-agent",
        description=textwrap.dedent("""
            Generate and iteratively refine essays using the REFLECTION pattern.
            
            Features:
            • Draft-Reflect-Revise workflow (reflection pattern)
            • Configurable iteration count (1-N refinement rounds)
            • Convergence detection (early stopping)
            • Saves all drafts, feedback, and final essay
            • Different models for drafting, reflection, and revision
        """),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              # Basic usage
              %(prog)s "Should social media platforms be regulated?"
              
              # Multiple iterations with custom output
              %(prog)s "The impact of AI on education" \\
                  --max-iterations 3 \\
                  --output-dir ./my_essays \\
                  --essay-basename ai_education
              
              # Use different models for each step
              %(prog)s "Climate change solutions" \\
                  --draft-model "openai:gpt-4o-mini" \\
                  --reflection-model "openai:o1-mini" \\
                  --revision-model "openai:gpt-4o"
        """),
    )
    
    # Required arguments
    parser.add_argument(
        "topic",
        help="Essay topic or question to address.",
    )
    
    # Model configuration
    model_group = parser.add_argument_group("Model Configuration")
    model_group.add_argument(
        "--draft-model",
        default="openai:gpt-4o-mini",
        help="Model for initial draft generation (default: openai:gpt-4o-mini).",
    )
    model_group.add_argument(
        "--reflection-model",
        default="openai:gpt-4o",
        help="Model for reflection and critique (default: openai:gpt-4o).",
    )
    model_group.add_argument(
        "--revision-model",
        default="openai:gpt-4o",
        help="Model for revision (default: openai:gpt-4o).",
    )
    
    # Output configuration
    output_group = parser.add_argument_group("Output Configuration")
    output_group.add_argument(
        "--essay-basename",
        default="essay",
        help="Basename for generated essay files (default: essay).",
    )
    output_group.add_argument(
        "--output-dir",
        default="./essays",
        help="Directory for generated essays and feedback (default: ./essays).",
    )
    output_group.add_argument(
        "--no-save-artifacts",
        dest="save_artifacts",
        action="store_false",
        help="Skip saving essay drafts and feedback to disk.",
    )
    output_group.add_argument(
        "--generate-pdf",
        action="store_true",
        help="Generate PDF versions of essays (requires weasyprint, pandoc, or markdown-pdf).",
    )
    output_group.add_argument(
        "--wrap-width",
        type=int,
        default=88,
        help="Line width for text wrapping (default: 88 characters).",
    )
    
    # Workflow configuration
    workflow_group = parser.add_argument_group("Workflow Configuration")
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
            Force all iterations even when essay converges early.
            By default, stops when minimal changes detected.
        """),
    )
    workflow_group.add_argument(
        "--min-words",
        type=int,
        default=800,
        help="Minimum target word count (default: 800).",
    )
    workflow_group.add_argument(
        "--max-words",
        type=int,
        default=6000,
        help=textwrap.dedent("""
            Maximum target word count (default: 6000, typical conference paper).
            The model will use its judgment—complex topics get comprehensive treatment.
        """),
    )
    
    # Temperature settings
    temp_group = parser.add_argument_group("Temperature Settings")
    temp_group.add_argument(
        "--draft-temperature",
        type=float,
        default=1.0,
        help="Temperature for draft generation (default: 1.0).",
    )
    temp_group.add_argument(
        "--reflection-temperature",
        type=float,
        default=1.0,
        help="Temperature for reflection (default: 1.0).",
    )
    temp_group.add_argument(
        "--revision-temperature",
        type=float,
        default=0.7,
        help="Temperature for revision (default: 0.7).",
    )
    
    # Display options
    display_group = parser.add_argument_group("Display Options")
    display_group.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed progress and intermediate outputs.",
    )
    display_group.add_argument(
        "--show-essays",
        action="store_true",
        help="Display essay text for each iteration.",
    )
    
    parser.set_defaults(stop_on_convergence=True, save_artifacts=True)
    return parser.parse_args()


def display_iteration_summary(artifacts, verbose: bool = False, show_essays: bool = False) -> None:
    """Display a summary of all iterations."""
    print_banner("Iteration Summary", "-")
    
    for iteration in artifacts.iterations:
        print(f"\n📝 Iteration {iteration.iteration}")
        print(f"   Word count: {iteration.word_count}")
        
        if iteration.feedback:
            # Extract rubric scores if present
            feedback_preview = iteration.feedback[:300]
            print(f"   Feedback preview: {feedback_preview}...")
        else:
            print(f"   Feedback: Initial draft (no reflection)")
        
        if show_essays:
            print(f"\n   --- Essay Text (first 500 chars) ---")
            print(textwrap.indent(iteration.essay_text[:500], "   "))
            if len(iteration.essay_text) > 500:
                print("   ...")
        
        if verbose and iteration.feedback:
            print(f"\n   --- Full Feedback ---")
            print(textwrap.indent(iteration.feedback, "   "))


def display_final_summary(artifacts, config: ResearchAgentConfig) -> None:
    """Display final workflow summary."""
    print_banner("Workflow Complete ✅")
    
    print(f"📈 Final Results:")
    print(f"   Total iterations: {artifacts.total_iterations}")
    print(f"   Max allowed: {config.max_iterations}")
    print(f"   Early stopping: {'enabled' if config.stop_on_convergence else 'disabled'}")
    print()
    
    print(f"📁 Output Files:")
    if artifacts.final_essay_path:
        print(f"   • {artifacts.final_essay_path.name} (final essay)")
        
        # List all iteration files
        for iteration in artifacts.iterations:
            iteration_file = f"{config.essay_basename}_v{iteration.iteration}.txt"
            print(f"   • {iteration_file}")
        
        if artifacts.feedback_path:
            print(f"   • {artifacts.feedback_path.name} (feedback and iterations)")
    print()
    
    print(f"🎯 Final Essay: {artifacts.final_essay_path}")
    print(f"   Word count: {artifacts.iterations[-1].word_count}")
    print()
    
    print(f"📝 Topic:")
    print(textwrap.indent(artifacts.topic, "   "))


def main() -> None:
    """Main entry point for the research agent."""
    # Load environment variables
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    
    args = parse_args()
    
    print_banner("Research Agent: Reflection Pattern")
    
    # Display configuration
    print("🔧 Configuration:")
    print(f"   Topic: {args.topic}")
    print(f"   Draft model: {args.draft_model}")
    print(f"   Reflection model: {args.reflection_model}")
    print(f"   Revision model: {args.revision_model}")
    print(f"   Max iterations: {args.max_iterations}")
    print(f"   Stop on convergence: {args.stop_on_convergence}")
    print(f"   Word count range: {args.min_words}-{args.max_words}")
    print(f"   Output directory: {args.output_dir}")
    print(f"   Save artifacts: {args.save_artifacts}")
    print(f"   Generate PDF: {args.generate_pdf}")
    print(f"   Text wrap width: {args.wrap_width}")
    print()
    
    # Create configuration
    config = ResearchAgentConfig(
        draft_model=args.draft_model,
        reflection_model=args.reflection_model,
        revision_model=args.revision_model,
        max_iterations=args.max_iterations,
        stop_on_convergence=args.stop_on_convergence,
        output_dir=Path(args.output_dir),
        essay_basename=args.essay_basename,
        save_artifacts=args.save_artifacts,
        generate_pdf=args.generate_pdf,
        wrap_width=args.wrap_width,
        min_words=args.min_words,
        max_words=args.max_words,
        draft_temperature=args.draft_temperature,
        reflection_temperature=args.reflection_temperature,
        revision_temperature=args.revision_temperature,
    )
    
    # Initialize client
    client = ai.Client()
    
    # Run workflow
    try:
        print_progress("Initializing workflow")
        print_progress("Starting draft-reflect-revise cycle", f"{args.max_iterations} iteration(s) max")
        print()
        
        artifacts = run_research_workflow(
            topic=args.topic,
            config=config,
            client=client,
        )
        
        # Display results
        display_iteration_summary(artifacts, verbose=args.verbose, show_essays=args.show_essays)
        display_final_summary(artifacts, config)
        
        # Success message
        print("✨ Research agent workflow completed successfully!")
        print()
        print("💡 The reflective writing workflow provides:")
        print("   1. Initial draft generation")
        print("   2. Structured critique and feedback")
        print("   3. Iterative revision and improvement")
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
