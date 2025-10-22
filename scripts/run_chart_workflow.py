#!/usr/bin/env python3
"""CLI entry point for the reflection-based chart generation workflow."""

from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from reflection.chart_workflow import ChartWorkflowConfig, run_reflection_workflow
from dotenv import load_dotenv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="run_chart_workflow",
        description="Generate and iteratively refine a chart using the reflection workflow.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "dataset",
        help="Path to a CSV file that should be analysed.",
    )
    parser.add_argument(
        "instruction",
        nargs="?",
        default=None,
        help="Natural language description of the visualisation you would like. "
             "When omitted, an instruction is auto-generated from the dataset.",
    )
    parser.add_argument(
        "--generation-model",
        default="gpt-4o-mini",
        help="Model used for the initial code generation prompt.",
    )
    parser.add_argument(
        "--reflection-model",
        default="gpt-4o",
        help="Model used during the reflection pass over the first chart.",
    )
    parser.add_argument(
        "--image-basename",
        default="chart",
        help="Basename for the generated chart files (suffixes _v1/_v2 are appended).",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory where the generated charts should be written.",
    )
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=5,
        help="Number of head rows to include in prompts for additional context.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=2,
        help="Maximum number of refinement iterations (including the initial draft).",
    )
    parser.add_argument(
        "--no-save-final-code",
        dest="save_final_code",
        action="store_false",
        help="Skip writing the final chart code to disk.",
    )
    parser.add_argument(
        "--no-stop-on-convergence",
        dest="stop_on_convergence",
        action="store_false",
        help="Force running all iterations even when the reflection appears to converge early.",
    )
    parser.set_defaults(stop_on_convergence=True)
    parser.set_defaults(save_final_code=True)
    return parser.parse_args()


def main() -> None:
    # Ensure API keys from the project .env are available when the script is invoked directly.
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")

    args = parse_args()

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

    artifacts = run_reflection_workflow(
        dataset=args.dataset,
        instruction=args.instruction,
        config=config,
    )

    print("\nResolved instruction:")
    print(artifacts.instruction)
    print()

    print("Iteration summary:")
    for iteration in artifacts.iterations:
        feedback_display = iteration.feedback if iteration.feedback else "n/a"
        print(
            textwrap.dedent(
                f"""
                -- Iteration {iteration.iteration} --
                   Chart: {iteration.chart_path}
                   Code length: {len(iteration.code)} characters
                   Feedback: {feedback_display}
                """
            ).strip()
        )

    final_chart = artifacts.iterations[-1].chart_path
    print(f"\nWorkflow completed in {len(artifacts.iterations)} iteration(s).")
    print(f"Final chart saved to: {final_chart}")
    if artifacts.final_code_path:
        print(f"Final code written to: {artifacts.final_code_path}")


if __name__ == "__main__":
    main()
