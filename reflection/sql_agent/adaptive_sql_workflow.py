#!/usr/bin/env python3
"""
Adaptive SQL Workflow with Dynamic Iteration

Key improvements over fixed-iteration approach:
1. Early stopping when SQL is already correct
2. Multiple iterations for weak models
3. Convergence detection (identical SQL or no feedback)
4. Error-based stopping (syntax errors, execution failures)
5. Model-aware iteration limits
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
import pandas as pd


@dataclass
class SQLIterationResult:
    """Result from a single SQL generation/refinement iteration."""
    iteration: int
    sql_query: str
    result: pd.DataFrame
    feedback: Optional[str]
    has_error: bool
    error_message: Optional[str]


@dataclass
class SQLWorkflowConfig:
    """Configuration for adaptive SQL workflow."""
    generation_model: str = "gpt-4o-mini"
    evaluation_model: str = "gpt-4o"
    max_iterations: int = 3
    stop_on_convergence: bool = True
    stop_on_success: bool = True  # Stop if SQL executes without errors
    min_iterations: int = 1  # Always do at least this many


def should_stop_iteration(
    iterations: List[SQLIterationResult],
    config: SQLWorkflowConfig,
) -> tuple[bool, str]:
    """
    Determine if we should stop iterating.
    
    Returns:
        (should_stop, reason)
    """
    if len(iterations) == 0:
        return False, ""
    
    current = iterations[-1]
    
    # Check max iterations
    if len(iterations) >= config.max_iterations:
        return True, f"Reached max iterations ({config.max_iterations})"
    
    # Don't stop before minimum iterations
    if len(iterations) < config.min_iterations:
        return False, ""
    
    # Stop on successful execution (if enabled)
    if config.stop_on_success and not current.has_error:
        # Check if result looks reasonable (not empty, no error column)
        if not current.result.empty and "error" not in current.result.columns:
            return True, "SQL executed successfully with valid results"
    
    # Stop on convergence (if enabled and we have at least 2 iterations)
    if config.stop_on_convergence and len(iterations) >= 2:
        previous = iterations[-2]
        
        # SQL is identical
        if current.sql_query.strip() == previous.sql_query.strip():
            return True, "SQL query converged (identical to previous)"
        
        # No feedback provided
        if not current.feedback or not current.feedback.strip():
            return True, "No feedback provided (model satisfied)"
    
    # Stop if current iteration has errors but previous didn't
    # (refinement made things worse)
    if len(iterations) >= 2:
        previous = iterations[-2]
        if current.has_error and not previous.has_error:
            return True, "Refinement introduced errors (reverting to previous)"
    
    return False, ""


def run_adaptive_sql_workflow(
    db_path: str,
    question: str,
    config: SQLWorkflowConfig,
    get_schema_fn,
    generate_sql_fn,
    execute_sql_fn,
    evaluate_and_refine_fn,
) -> Dict[str, Any]:
    """
    Adaptive SQL workflow with dynamic iteration.
    
    Args:
        db_path: Path to SQLite database
        question: Natural language question
        config: Workflow configuration
        get_schema_fn: Function to extract schema
        generate_sql_fn: Function to generate SQL
        execute_sql_fn: Function to execute SQL
        evaluate_and_refine_fn: Function to evaluate and refine SQL
    
    Returns:
        Dictionary with all iterations and final result
    """
    schema = get_schema_fn(db_path)
    print(f"📘 Schema extracted: {len(schema)} characters")
    
    iterations: List[SQLIterationResult] = []
    
    # Generate initial SQL (V1)
    print(f"\n{'='*80}")
    print(f"Iteration 1: Initial Generation")
    print(f"{'='*80}")
    
    sql_v1 = generate_sql_fn(question, schema, config.generation_model)
    print(f"🧠 Generated SQL:\n{sql_v1}\n")
    
    df_v1 = execute_sql_fn(sql_v1, db_path)
    has_error_v1 = "error" in df_v1.columns
    error_msg_v1 = df_v1["error"].iloc[0] if has_error_v1 else None
    
    if has_error_v1:
        print(f"❌ Execution error: {error_msg_v1}")
    else:
        print(f"✅ Executed successfully ({len(df_v1)} rows)")
        print(df_v1.head())
    
    iterations.append(SQLIterationResult(
        iteration=1,
        sql_query=sql_v1,
        result=df_v1,
        feedback=None,
        has_error=has_error_v1,
        error_message=error_msg_v1,
    ))
    
    # Check if we should stop after V1
    should_stop, reason = should_stop_iteration(iterations, config)
    if should_stop:
        print(f"\n🛑 Stopping after iteration 1: {reason}")
        return _build_result(iterations, reason)
    
    # Refinement loop
    previous_sql = sql_v1
    previous_df = df_v1
    
    for iteration_num in range(2, config.max_iterations + 1):
        print(f"\n{'='*80}")
        print(f"Iteration {iteration_num}: Refinement")
        print(f"{'='*80}")
        
        # Evaluate and refine
        feedback, refined_sql = evaluate_and_refine_fn(
            question=question,
            sql_query=previous_sql,
            df=previous_df,
            schema=schema,
            model=config.evaluation_model,
        )
        
        print(f"📝 Feedback:\n{feedback}\n")
        print(f"🔁 Refined SQL:\n{refined_sql}\n")
        
        # Execute refined SQL
        refined_df = execute_sql_fn(refined_sql, db_path)
        has_error = "error" in refined_df.columns
        error_msg = refined_df["error"].iloc[0] if has_error else None
        
        if has_error:
            print(f"❌ Execution error: {error_msg}")
        else:
            print(f"✅ Executed successfully ({len(refined_df)} rows)")
            print(refined_df.head())
        
        iterations.append(SQLIterationResult(
            iteration=iteration_num,
            sql_query=refined_sql,
            result=refined_df,
            feedback=feedback,
            has_error=has_error,
            error_message=error_msg,
        ))
        
        # Check if we should stop
        should_stop, reason = should_stop_iteration(iterations, config)
        if should_stop:
            print(f"\n🛑 Stopping after iteration {iteration_num}: {reason}")
            break
        
        previous_sql = refined_sql
        previous_df = refined_df
    
    return _build_result(iterations, reason if should_stop else "Max iterations reached")


def _build_result(iterations: List[SQLIterationResult], stop_reason: str) -> Dict[str, Any]:
    """Build final result dictionary."""
    # Find best iteration (prefer non-error, then latest)
    best_iteration = None
    for it in reversed(iterations):
        if not it.has_error:
            best_iteration = it
            break
    
    if best_iteration is None:
        best_iteration = iterations[-1]  # Use last even if it has errors
    
    return {
        "iterations": iterations,
        "best_iteration": best_iteration,
        "final_sql": best_iteration.sql_query,
        "final_result": best_iteration.result,
        "total_iterations": len(iterations),
        "stop_reason": stop_reason,
        "success": not best_iteration.has_error,
    }


def get_model_recommended_config(generation_model: str) -> SQLWorkflowConfig:
    """
    Get recommended configuration based on generation model capability.
    
    Strong models (GPT-4, Claude 3.5) → fewer iterations, early stopping
    Weak models (GPT-3.5, small models) → more iterations, forced refinement
    """
    # Strong models - likely to get it right first time
    if any(m in generation_model.lower() for m in ["gpt-4", "claude-3.5", "claude-3-opus"]):
        return SQLWorkflowConfig(
            generation_model=generation_model,
            evaluation_model=generation_model,  # Use same model
            max_iterations=2,
            stop_on_convergence=True,
            stop_on_success=True,
            min_iterations=1,
        )
    
    # Medium models - might need 1-2 refinements
    elif any(m in generation_model.lower() for m in ["gpt-3.5", "claude-3-sonnet", "gpt-4o-mini"]):
        return SQLWorkflowConfig(
            generation_model=generation_model,
            evaluation_model="gpt-4o",  # Use stronger model for evaluation
            max_iterations=3,
            stop_on_convergence=True,
            stop_on_success=True,
            min_iterations=1,
        )
    
    # Weak models - need multiple refinements
    else:
        return SQLWorkflowConfig(
            generation_model=generation_model,
            evaluation_model="gpt-4o",  # Definitely use stronger model
            max_iterations=5,
            stop_on_convergence=True,
            stop_on_success=False,  # Don't trust first success
            min_iterations=2,  # Force at least one refinement
        )


# Example usage
if __name__ == "__main__":
    print("""
Adaptive SQL Workflow - Model-Aware Configuration Examples:

1. Strong Model (GPT-4):
   • Max 2 iterations
   • Stops on first success
   • Same model for generation and evaluation
   • Rationale: Likely correct on first try

2. Medium Model (GPT-3.5):
   • Max 3 iterations
   • Stops on success or convergence
   • Stronger model (GPT-4) for evaluation
   • Rationale: May need 1-2 refinements

3. Weak Model (Custom/Small):
   • Max 5 iterations
   • Requires minimum 2 iterations
   • GPT-4 for evaluation
   • Rationale: Needs multiple refinements

Key Features:
✅ Early stopping when SQL is correct
✅ Multiple iterations for weak models
✅ Convergence detection
✅ Error-based stopping
✅ Model-aware defaults
    """)
