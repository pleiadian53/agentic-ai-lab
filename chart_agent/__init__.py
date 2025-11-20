"""Chart Agent - LLM-powered chart generation with code-as-plan and reflection.

This package provides tools for generating data visualizations using LLMs,
combining code generation with iterative refinement through reflection.
"""

from chart_agent.data_access import (
    ChartDataset,
    CSVDataset,
    SQLiteDataset,
    DataFrameDataset,
    ExcelDataset,
    DuckDBDataset,
)

from chart_agent.planning import (
    generate_chart_code,
    generate_chart_code_with_reasoning,
)

from chart_agent.utils import (
    print_html,
    display_models_table,
    models_response_to_dataframe,
    save_models_list,
    load_models_list,
    get_recommended_models,
    display_chart_result,
    display_analysis_summary,
    execute_chart_code,
    save_code_to_file,
    validate_chart_code,
)

from chart_agent.llm_client import (
    call_llm_text,
    call_llm_json,
)

__all__ = [
    # Data access
    "ChartDataset",
    "CSVDataset",
    "SQLiteDataset",
    "DataFrameDataset",
    "ExcelDataset",
    "DuckDBDataset",
    # Planning
    "generate_chart_code",
    "generate_chart_code_with_reasoning",
    # Utilities
    "print_html",
    "display_models_table",
    "models_response_to_dataframe",
    "save_models_list",
    "load_models_list",
    "get_recommended_models",
    "display_chart_result",
    "display_analysis_summary",
    "execute_chart_code",
    "save_code_to_file",
    "validate_chart_code",
    # LLM Client
    "call_llm_text",
    "call_llm_json",
]
