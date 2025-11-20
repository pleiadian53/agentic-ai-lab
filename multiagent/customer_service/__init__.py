"""Customer service agent package (single-agent, code-as-plan).

This package exposes a reusable customer-service agent that can be
invoked from notebooks, scripts, or larger agentic systems. It follows
the "code as plan" pattern, where an LLM writes Python that becomes the
executable plan over a simple store of inventory and transactions.

The current implementation focuses on a TinyDB-backed demo, with
pluggable data stores and configurable prompts so the same patterns can
be extended to richer domains (e.g., DuckDB/SQLite today, or future
bio- / multiomics-specific workflows).
"""

from .data_access import CustomerServiceStore, TinyDBStore, DuckDBStore, SQLiteStore
from .planning import generate_llm_code
from .execution import execute_generated_code
from .single_agent import customer_service_agent
from .tool_registry import (
    TOOL_REGISTRY,
    TOOL_SIGNATURES,
    run_tools_for_step,
    run_tool_validation,
    canonicalize_args,
    missing_required,
)
from .tool_planning import (
    generate_plan,
    reflect_on_plan,
    explain_execution_error,
)
from .tool_execution import (
    execute_plan,
    execute_plan_with_summary,
    format_execution_report,
)
from .tool_agent import (
    tool_based_agent,
    tool_based_agent_simple,
    print_execution_report,
)

__all__ = [
    # Data access
    "CustomerServiceStore",
    "TinyDBStore",
    "DuckDBStore",
    "SQLiteStore",
    # Single-agent (code-as-plan)
    "generate_llm_code",
    "execute_generated_code",
    "customer_service_agent",
    # Tool registry (multi-agent / tools-based)
    "TOOL_REGISTRY",
    "TOOL_SIGNATURES",
    "run_tools_for_step",
    "run_tool_validation",
    "canonicalize_args",
    "missing_required",
    # Tool-based agent (plan-reflect-execute)
    "generate_plan",
    "reflect_on_plan",
    "explain_execution_error",
    "execute_plan",
    "execute_plan_with_summary",
    "format_execution_report",
    "tool_based_agent",
    "tool_based_agent_simple",
    "print_execution_report",
]
