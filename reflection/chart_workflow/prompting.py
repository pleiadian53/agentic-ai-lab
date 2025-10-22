"""Heuristics for crafting initial visualization instructions."""

from __future__ import annotations

import textwrap

import pandas as pd


def _categorical_columns(df: pd.DataFrame, max_unique: int = 15) -> list[str]:
    cats: list[str] = []
    for col in df.columns:
        series = df[col]
        if pd.api.types.is_bool_dtype(series):
            cats.append(col)
        elif pd.api.types.is_categorical_dtype(series):
            cats.append(col)
        elif pd.api.types.is_object_dtype(series):
            cats.append(col)
        elif pd.api.types.is_integer_dtype(series) and series.nunique(dropna=True) <= max_unique:
            cats.append(col)
    return cats


def _numeric_columns(df: pd.DataFrame) -> list[str]:
    nums: list[str] = []
    for col in df.columns:
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            if not pd.api.types.is_bool_dtype(series):
                nums.append(col)
    return nums


def _select_best(items: Iterable[str], preferred: Iterable[str]) -> str | None:
    preferred_lower = [p.lower() for p in preferred]
    for pref in preferred_lower:
        for item in items:
            if item.lower() == pref:
                return item
    return next(iter(items), None)


def suggest_initial_instruction(df: pd.DataFrame) -> str:
    """
    Generate a multi-part instruction well-suited for exploratory plotting.

    The heuristic favors categorical comparisons and numeric distributions.
    Domain-specific tweaks are added for genomic-style dataframes.
    """
    if df.empty:
        return (
            "The dataframe `df` is empty. Summarize the lack of rows in a simple chart "
            "that explains no records are available."
        )

    cats = _categorical_columns(df)
    nums = _numeric_columns(df)

    parts: list[str] = []

    columns_lower = {c.lower() for c in df.columns}
    is_genomic = {"chrom", "start", "end"}.issubset(columns_lower) or "position" in columns_lower
    strand_col = _select_best(cats, ["strand"])
    site_type_col = _select_best(cats, ["site_type", "event", "label"])
    chrom_col = _select_best(cats, ["chrom", "chromosome"])
    exon_col = _select_best(nums, ["exon_rank", "exon_number"])

    if is_genomic and site_type_col and chrom_col:
        parts.append(
            f"A ranked bar chart comparing counts of {site_type_col} values across the most "
            f"frequent {chrom_col} entries (top 10 by volume)."
        )
        if strand_col:
            parts.append(
                f"A stacked visualization showing how {site_type_col} splits across {strand_col} "
                f"for the same top {chrom_col} groupings."
            )
        if exon_col:
            parts.append(
                f"A histogram of {exon_col} to reveal positional patterns of splice sites."
            )
    else:
        if cats:
            primary_cat = _select_best(cats, ["category", "type", "label"]) or cats[0]
            parts.append(
                f"A bar chart of `{primary_cat}` showing the top categories and their counts."
            )
        if len(cats) >= 2:
            secondary_cat = [c for c in cats if c != primary_cat]
            if secondary_cat:
                parts.append(
                    f"A grouped bar or heatmap comparing `{primary_cat}` against `{secondary_cat[0]}`."
                )
        if nums:
            num_col = _select_best(nums, ["price", "value", "amount"]) or nums[0]
            parts.append(
                f"A distribution plot (histogram or box plot) for `{num_col}` with annotations "
                "highlighting notable percentiles."
            )

    if not parts:
        parts.append(
            "A simple table-style visualization summarising row counts, since no obvious numeric "
            "or categorical columns were detected."
        )

    numbered_parts = "\n".join(f"{idx + 1}) {part}" for idx, part in enumerate(parts))

    instruction = textwrap.dedent(
        """\
        Create an exploratory multi-panel figure for the dataframe `df` that includes:
        {numbered_parts}

        Use pandas/matplotlib, give each subplot a descriptive title, label axes clearly,
        annotate any notable trends, and save the final figure with tight layout handling.
        """
    ).format(numbered_parts=numbered_parts)

    return instruction
