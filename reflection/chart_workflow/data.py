"""Utilities for loading dataframes and extracting lightweight summaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Iterable

import pandas as pd

from reflection.M2_UGL_1 import utils as legacy_utils


DataSource = Path | str | pd.DataFrame
Preprocessor = Callable[[pd.DataFrame], pd.DataFrame]


def load_dataframe(
    source: DataSource,
    *,
    loader: Callable[[Path | str], pd.DataFrame] | None = None,
    preprocessors: Iterable[Preprocessor] | None = None,
) -> pd.DataFrame:
    """
    Load a dataframe from a CSV path/URL or accept an existing dataframe.

    Parameters
    ----------
    source:
        Either a pandas dataframe (returned as a copy) or a path-like reference
        that will be passed to `loader`.
    loader:
        Callable used to create the dataframe when `source` is not already a
        dataframe. Defaults to the legacy helper that adds convenient date
        features when present.
    preprocessors:
        Optional callables that will be applied sequentially to the dataframe.
    """
    if isinstance(source, pd.DataFrame):
        df = source.copy()
    else:
        loader_fn = loader or legacy_utils.load_and_prepare_data
        df = loader_fn(Path(source))

    if preprocessors:
        for transform in preprocessors:
            df = transform(df)

    return df


def dataframe_schema(df: pd.DataFrame) -> str:
    """Return a minimal textual schema description for prompt conditioning."""
    if df.empty:
        return "The dataframe is empty."
    try:
        return legacy_utils.make_schema_text(df)
    except Exception:
        return "\n".join(f"- {col}: {dtype}" for col, dtype in df.dtypes.items())


def dataframe_sample(df: pd.DataFrame, *, rows: int = 5) -> str:
    """Serialize a head sample as JSON for inclusion in LLM prompts."""
    if df.empty:
        return "[]"
    head = df.head(rows)
    # Convert to JSON-serializable types without leaking nan/inf tokens.
    records = json.loads(head.to_json(orient="records", date_format="iso"))
    return json.dumps(records, indent=2)
