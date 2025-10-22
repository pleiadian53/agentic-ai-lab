"""Orchestration logic for the chart reflection workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Mapping, Any

import pandas as pd

from .data import DataSource, Preprocessor, dataframe_sample, dataframe_schema, load_dataframe
from .execution import execute_python, extract_execute_block, ensure_tagged
from .llm import PromptContext, generate_initial_code, reflect_on_chart
from .prompting import suggest_initial_instruction


@dataclass(slots=True)
class ChartWorkflowConfig:
    generation_model: str
    reflection_model: str
    image_basename: str = "chart"
    output_dir: Path = field(default_factory=lambda: Path.cwd())
    sample_rows: int = 5
    max_iterations: int = 2
    stop_on_convergence: bool = True
    save_final_code: bool = True


@dataclass(slots=True)
class WorkflowArtifacts:
    instruction: str
    iterations: list["IterationResult"]
    final_code_path: Path | None

    @property
    def code_v1(self) -> str:
        return self.iterations[0].code

    @property
    def chart_v1(self) -> Path:
        return self.iterations[0].chart_path

    @property
    def feedback(self) -> str:
        # For backwards compatibility, surface the final feedback (if any)
        return self.iterations[-1].feedback or ""

    @property
    def code_v2(self) -> str:
        if len(self.iterations) >= 2:
            return self.iterations[1].code
        return self.iterations[0].code

    @property
    def chart_v2(self) -> Path:
        if len(self.iterations) >= 2:
            return self.iterations[1].chart_path
        return self.iterations[0].chart_path

    @property
    def globals_v1(self) -> Mapping[str, Any]:
        return self.iterations[0].globals_namespace

    @property
    def globals_v2(self) -> Mapping[str, Any]:
        if len(self.iterations) >= 2:
            return self.iterations[1].globals_namespace
        return self.iterations[0].globals_namespace

    @property
    def final_code(self) -> str:
        return self.iterations[-1].code


@dataclass(slots=True)
class IterationResult:
    iteration: int
    code: str
    chart_path: Path
    feedback: str | None
    globals_namespace: Mapping[str, Any]


def run_reflection_workflow(
    *,
    dataset: DataSource,
    instruction: str | None,
    config: ChartWorkflowConfig,
    loader: Callable[[Path | str], pd.DataFrame] | None = None,
    preprocessors: Iterable[Preprocessor] | None = None,
) -> WorkflowArtifacts:
    """
    Execute the full reflection workflow on the provided dataset.

    Parameters
    ----------
    dataset:
        Either a dataframe or a path-like object to load via `loader`.
    instruction:
        Natural language request describing the desired visualization.
    config:
        Model names, output locations, and prompt tuning parameters.
    loader:
        Optional loader override. When omitted, uses the legacy helper that
        reads CSV files and adds calendar features when applicable.
    preprocessors:
        Optional preprocessing callables applied after loading.
    config.max_iterations:
        Determines how many total iterations (initial draft + refinements) are attempted.
    config.stop_on_convergence:
        When True, the loop exits early if the reflection returns identical code or no feedback.

    Returns
    -------
    WorkflowArtifacts
        All intermediate assets generated during the workflow run.
    """
    df = load_dataframe(dataset, loader=loader, preprocessors=preprocessors)

    resolved_instruction = instruction or suggest_initial_instruction(df)

    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    prompt_context = PromptContext(
        schema=dataframe_schema(df),
        sample_rows_json=dataframe_sample(df, rows=config.sample_rows),
    )

    iterations: list[IterationResult] = []

    chart_v1_path = output_dir / f"{config.image_basename}_v1.png"

    code_v1 = generate_initial_code(
        instruction=resolved_instruction,
        model_name=config.generation_model,
        output_path=str(chart_v1_path),
        prompt_context=prompt_context,
    )

    globals_v1 = execute_python(code_v1, globals_dict={"df": df})

    iterations.append(
        IterationResult(
            iteration=1,
            code=code_v1,
            chart_path=chart_v1_path,
            feedback=None,
            globals_namespace=globals_v1,
        )
    )

    previous_code = code_v1
    previous_chart_path = chart_v1_path

    max_iters = max(1, config.max_iterations)

    for iteration_index in range(2, max_iters + 1):
        chart_path = output_dir / f"{config.image_basename}_v{iteration_index}.png"

        feedback, candidate_code = reflect_on_chart(
            chart_path=str(previous_chart_path),
            instruction=resolved_instruction,
            model_name=config.reflection_model,
            output_path=str(chart_path),
            original_code=previous_code,
            prompt_context=prompt_context,
        )

        normalized_previous = previous_code.strip()
        normalized_candidate = candidate_code.strip()

        if config.stop_on_convergence and (
            normalized_candidate == normalized_previous or not feedback.strip()
        ):
            break

        globals_namespace = execute_python(candidate_code, globals_dict={"df": df})

        iterations.append(
            IterationResult(
                iteration=iteration_index,
                code=candidate_code,
                chart_path=chart_path,
                feedback=feedback,
                globals_namespace=globals_namespace,
            )
        )

        previous_code = candidate_code
        previous_chart_path = chart_path

    final_code_path: Path | None = None
    if config.save_final_code:
        final_code_path = output_dir / f"{config.image_basename}_final.py"
        final_code_path.write_text(
            extract_execute_block(ensure_tagged(iterations[-1].code)),
            encoding="utf-8",
        )

    return WorkflowArtifacts(
        instruction=resolved_instruction,
        iterations=iterations,
        final_code_path=final_code_path,
    )
