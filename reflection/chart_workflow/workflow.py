"""Orchestration logic for the chart reflection workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Mapping, Any

import pandas as pd

from .data import DataSource, Preprocessor, dataframe_sample, dataframe_schema, load_dataframe
from .execution import execute_python
from .llm import PromptContext, generate_initial_code, reflect_on_chart
from .prompting import suggest_initial_instruction


@dataclass(slots=True)
class ChartWorkflowConfig:
    generation_model: str
    reflection_model: str
    image_basename: str = "chart"
    output_dir: Path = field(default_factory=lambda: Path.cwd())
    sample_rows: int = 5


@dataclass(slots=True)
class WorkflowArtifacts:
    code_v1: str
    chart_v1: Path
    feedback: str
    code_v2: str
    chart_v2: Path
    globals_v1: Mapping[str, Any]
    globals_v2: Mapping[str, Any]
    instruction: str


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

    Returns
    -------
    WorkflowArtifacts
        All intermediate assets generated during the workflow run.
    """
    df = load_dataframe(dataset, loader=loader, preprocessors=preprocessors)

    resolved_instruction = instruction or suggest_initial_instruction(df)

    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    chart_v1_path = output_dir / f"{config.image_basename}_v1.png"
    chart_v2_path = output_dir / f"{config.image_basename}_v2.png"

    prompt_context = PromptContext(
        schema=dataframe_schema(df),
        sample_rows_json=dataframe_sample(df, rows=config.sample_rows),
    )

    code_v1 = generate_initial_code(
        instruction=resolved_instruction,
        model_name=config.generation_model,
        output_path=str(chart_v1_path),
        prompt_context=prompt_context,
    )

    globals_v1 = execute_python(code_v1, globals_dict={"df": df})

    feedback, code_v2 = reflect_on_chart(
        chart_path=str(chart_v1_path),
        instruction=resolved_instruction,
        model_name=config.reflection_model,
        output_path=str(chart_v2_path),
        original_code=code_v1,
        prompt_context=prompt_context,
    )

    globals_v2 = execute_python(code_v2, globals_dict={"df": df})

    return WorkflowArtifacts(
        code_v1=code_v1,
        chart_v1=chart_v1_path,
        feedback=feedback,
        code_v2=code_v2,
        chart_v2=chart_v2_path,
        globals_v1=globals_v1,
        globals_v2=globals_v2,
        instruction=resolved_instruction,
    )
