"""Splice Agent - AI-Powered Splice Site Analysis.

A specialized framework for genomic splice site prediction and analysis using LLMs.
Built on the Chart Agent foundation with domain-specific enhancements for
splice site biology, alternative splicing, and transcript structure analysis.
"""

__version__ = "0.1.0"

from splice_agent.data_access import (
    ChartDataset,
    CSVDataset,
    DuckDBDataset,
    SQLiteDataset,
    DataFrameDataset,
    ExcelDataset,
    create_dataset,
)

from splice_agent.planning import (
    generate_chart_code,
    generate_chart_code_with_reasoning,
)

from splice_agent.utils import (
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
    get_available_models,
    display_code,
)

from splice_agent.llm_client import (
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
