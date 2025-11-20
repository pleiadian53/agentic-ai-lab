"""Tool-based customer service agent with plan-reflect-execute workflow.

This module provides a structured approach to customer service automation using:
- Predefined tools from tool_registry
- LLM-generated plans specifying tool sequences
- Reflection step to validate and revise plans
- Step-by-step execution with validations

This approach trades flexibility for safety and observability, making it suitable
for production environments where constrained actions and explicit logging are required.

Contrast with single_agent.py (code-as-plan):
- Tool-based: Safe, observable, constrained → Production-ready
- Code-as-plan: Flexible, powerful, adaptive → Exploration and complex logic
"""

from __future__ import annotations

from typing import Any, Optional

from openai import OpenAI

from .data_access import CustomerServiceStore, DuckDBStore
from .tool_execution import execute_plan, format_execution_report
from .tool_planning import (
    generate_plan,
    reflect_on_plan,
    explain_execution_error,
)


def tool_based_agent(
    user_query: str,
    store: Optional[CustomerServiceStore] = None,
    client: Optional[OpenAI] = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.1,
    use_reflection: bool = True,
    stop_on_failed_validation: bool = True,
    reseed: bool = False,
) -> dict[str, Any]:
    """Execute a customer service request using tool-based planning.
    
    This is the main entry point for tool-based workflows. It:
    1. Generates a plan using LLM (which tools to call in what order)
    2. Optionally reflects on and revises the plan
    3. Executes the plan step by step
    4. Returns detailed results
    
    Workflow:
        User Query
            ↓
        [LLM Planning] → Draft Plan
            ↓
        [LLM Reflection] → Revised Plan (optional)
            ↓
        [Tool Execution] → Results
    
    Args:
        user_query: Natural language customer request
        store: CustomerServiceStore instance (defaults to DuckDBStore)
        client: OpenAI client (defaults to OpenAI())
        model: Model to use for planning and reflection
        temperature: Sampling temperature for LLM calls
        use_reflection: Whether to run reflection step on draft plan
        stop_on_failed_validation: Whether to stop execution on first validation failure
        reseed: Whether to reseed store with fresh demo data
        
    Returns:
        Dict with:
        - "user_query": str (original request)
        - "draft_plan": dict (initial plan from LLM)
        - "reflection": dict (critique and revised_plan, if use_reflection=True)
        - "final_plan": dict (plan that was executed)
        - "execution_report": dict (detailed step-by-step results)
        - "success": bool (whether execution succeeded)
        - "message": str (human-readable summary)
        - "inventory_rows": list (final inventory state)
        - "transaction_rows": list (final transaction state)
        - "error_explanation": str (if execution failed and use_reflection=True)
    
    Example:
        >>> from openai import OpenAI
        >>> from multiagent.customer_service import tool_based_agent, DuckDBStore
        >>> 
        >>> client = OpenAI()
        >>> store = DuckDBStore()
        >>> 
        >>> result = tool_based_agent(
        ...     "I want to return 2 Aviator sunglasses",
        ...     store=store,
        ...     client=client,
        ...     use_reflection=True
        ... )
        >>> 
        >>> print(result["success"])
        True
        >>> print(result["message"])
        Successfully executed 4 steps.
    """
    # Initialize defaults
    if store is None:
        store = DuckDBStore(db_path=None)  # In-memory
    
    if client is None:
        client = OpenAI()
    
    if reseed:
        store.seed_demo_data()
    
    result: dict[str, Any] = {
        "user_query": user_query,
    }
    
    # Step 1: Generate draft plan
    draft_plan = generate_plan(
        user_query,
        client=client,
        model=model,
        temperature=temperature
    )
    result["draft_plan"] = draft_plan
    
    # Step 2: Optionally reflect on and revise plan
    if use_reflection:
        reflection = reflect_on_plan(
            user_query,
            draft_plan,
            client=client,
            model=model,
            temperature=temperature
        )
        result["reflection"] = reflection
        final_plan = reflection["revised_plan"]
    else:
        final_plan = draft_plan
    
    result["final_plan"] = final_plan
    
    # Step 3: Execute the plan
    execution_report = execute_plan(
        final_plan,
        store=store,
        stop_on_failed_validation=stop_on_failed_validation
    )
    result["execution_report"] = execution_report
    
    # Step 4: Generate summary
    result["success"] = execution_report["ok"]
    
    if execution_report["ok"]:
        result["message"] = f"Successfully executed {len(execution_report['steps'])} steps."
    elif execution_report.get("aborted"):
        result["message"] = (
            f"Execution stopped at step {execution_report['abort_step']} "
            f"due to {execution_report['abort_reason']}."
        )
    else:
        failed_steps = [
            s["step_number"]
            for s in execution_report["steps"]
            if not s.get("step_ok", False)
        ]
        result["message"] = f"Execution failed at step(s): {failed_steps}"
    
    # Step 5: Get final state
    result["inventory_rows"] = store.get_inventory_rows()
    result["transaction_rows"] = store.get_transaction_rows()
    
    # Step 6: If execution failed and reflection is enabled, explain the error
    if not execution_report["ok"] and use_reflection:
        error_explanation = explain_execution_error(
            user_query,
            execution_report,
            client=client,
            model=model,
            temperature=temperature
        )
        result["error_explanation"] = error_explanation
    
    return result


def tool_based_agent_simple(
    user_query: str,
    store: Optional[CustomerServiceStore] = None,
    client: Optional[OpenAI] = None,
    **kwargs
) -> str:
    """Simplified interface returning just the result message.
    
    This is a convenience wrapper for interactive use.
    
    Args:
        user_query: Natural language customer request
        store: CustomerServiceStore instance
        client: OpenAI client
        **kwargs: Additional arguments passed to tool_based_agent
        
    Returns:
        Human-readable result message
    
    Example:
        >>> message = tool_based_agent_simple(
        ...     "I want to buy 3 pairs of classic sunglasses"
        ... )
        >>> print(message)
        Successfully executed 4 steps.
    """
    result = tool_based_agent(
        user_query,
        store=store,
        client=client,
        **kwargs
    )
    
    if result["success"]:
        return result["message"]
    else:
        msg = result["message"]
        if "error_explanation" in result:
            msg += f"\n\nExplanation: {result['error_explanation']}"
        return msg


def print_execution_report(result: dict[str, Any]) -> None:
    """Pretty-print execution report from tool_based_agent.
    
    Args:
        result: Result dict from tool_based_agent
    """
    print("=" * 60)
    print("TOOL-BASED AGENT EXECUTION REPORT")
    print("=" * 60)
    print()
    
    print(f"User Query: {result['user_query']}")
    print()
    
    if "reflection" in result:
        print("Reflection Critique:")
        print(result["reflection"]["critique"])
        print()
    
    print(format_execution_report(result["execution_report"]))
    print()
    
    print(f"Final Status: {result['message']}")
    
    if "error_explanation" in result:
        print()
        print("Error Explanation:")
        print(result["error_explanation"])
    
    print()
    print("=" * 60)
