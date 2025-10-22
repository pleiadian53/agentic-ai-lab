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
    )

    artifacts = run_reflection_workflow(
        dataset=args.dataset,
        instruction=args.instruction,
        config=config,
    )

    print("\nResolved instruction:")
    print(artifacts.instruction)
    print()

    summary = textwrap.dedent(
        f"""
        Workflow completed.
          • V1 code length: {len(artifacts.code_v1)} characters
          • V1 chart saved to: {artifacts.chart_v1}
          • Reflection feedback: {artifacts.feedback or 'n/a'}
          • V2 chart saved to: {artifacts.chart_v2}
        """
    ).strip()

    print(summary)


if __name__ == "__main__":
    main()
