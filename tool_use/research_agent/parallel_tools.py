"""
Parallel tool execution for LLM-instructed tool calls.

This module provides utilities for executing multiple tool calls concurrently,
improving performance when the LLM requests multiple independent operations.
"""

import json
import threading
import concurrent.futures
from typing import List, Dict, Any, Callable
from collections import defaultdict


class ParallelToolExecutor:
    """
    Executes LLM-instructed tool calls in parallel with proper error handling.
    """
    
    def __init__(self, tool_mapping: Dict[str, Callable], max_workers: int = 5):
        """
        Initialize the parallel tool executor.
        
        Args:
            tool_mapping: Dictionary mapping tool names to callable functions
            max_workers: Maximum number of concurrent workers (default: 5)
        """
        self.tool_mapping = tool_mapping
        self.max_workers = max_workers
        self._stats = defaultdict(int)
        self._lock = threading.Lock()
    
    def execute_tool_calls(self, tool_calls: List[Any], verbose: bool = True) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls in parallel.
        
        Args:
            tool_calls: List of tool call objects from LLM response
            verbose: Whether to print execution progress
            
        Returns:
            List of dicts with 'call', 'result', 'error', and 'execution_time' keys
        """
        if not tool_calls:
            return []
        
        if verbose:
            print(f"🛠️  Executing {len(tool_calls)} tool(s) in parallel...")
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tool calls
            future_to_call = {}
            for call in tool_calls:
                future = executor.submit(self._execute_single_tool, call, verbose)
                future_to_call[future] = call
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_call):
                call = future_to_call[future]
                try:
                    result_data = future.result()
                    results.append(result_data)
                except Exception as e:
                    # Fallback error handling
                    results.append({
                        "call": call,
                        "result": {"error": f"Executor error: {str(e)}"},
                        "error": str(e),
                        "execution_time": 0
                    })
        
        if verbose:
            self._print_summary(results)
        
        return results
    
    def _execute_single_tool(self, call: Any, verbose: bool) -> Dict[str, Any]:
        """
        Execute a single tool call with error handling and timing.
        
        Args:
            call: Tool call object from LLM
            verbose: Whether to print progress
            
        Returns:
            Dict with execution results
        """
        import time
        
        tool_name = call.function.name
        start_time = time.time()
        
        try:
            args = json.loads(call.function.arguments)
            
            if verbose:
                print(f"  → {tool_name}({args})")
            
            # Get tool function
            if tool_name not in self.tool_mapping:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            tool_func = self.tool_mapping[tool_name]
            
            # Execute tool
            result = tool_func(**args)
            
            # Track stats
            with self._lock:
                self._stats[tool_name] += 1
                self._stats["total_calls"] += 1
            
            execution_time = time.time() - start_time
            
            return {
                "call": call,
                "result": result,
                "error": None,
                "execution_time": execution_time
            }
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON arguments for {tool_name}: {str(e)}"
            return {
                "call": call,
                "result": {"error": error_msg},
                "error": error_msg,
                "execution_time": time.time() - start_time
            }
        
        except Exception as e:
            error_msg = f"Error executing {tool_name}: {str(e)}"
            return {
                "call": call,
                "result": {"error": error_msg},
                "error": error_msg,
                "execution_time": time.time() - start_time
            }
    
    def _print_summary(self, results: List[Dict[str, Any]]):
        """Print execution summary."""
        total_time = sum(r["execution_time"] for r in results)
        max_time = max(r["execution_time"] for r in results) if results else 0
        errors = sum(1 for r in results if r["error"])
        
        print(f"  ✅ Completed {len(results)} tool(s) in {max_time:.2f}s (total: {total_time:.2f}s)")
        if errors:
            print(f"  ⚠️  {errors} error(s) occurred")
    
    def get_stats(self) -> Dict[str, int]:
        """Get execution statistics."""
        with self._lock:
            return dict(self._stats)
    
    def reset_stats(self):
        """Reset execution statistics."""
        with self._lock:
            self._stats.clear()


def format_tool_results_for_messages(results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Format parallel execution results into message format for LLM.
    
    Args:
        results: List of result dicts from ParallelToolExecutor
        
    Returns:
        List of message dicts ready to append to conversation
    """
    messages = []
    
    for result_data in results:
        call = result_data["call"]
        result = result_data["result"]
        
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "name": call.function.name,
            "content": json.dumps(result)
        })
    
    return messages


# Convenience function for simple use cases
def execute_tools_parallel(tool_calls: List[Any], tool_mapping: Dict[str, Callable], 
                          verbose: bool = True) -> List[Dict[str, str]]:
    """
    Simple function to execute tool calls in parallel and return formatted messages.
    
    Args:
        tool_calls: List of tool call objects from LLM
        tool_mapping: Dict mapping tool names to functions
        verbose: Whether to print progress
        
    Returns:
        List of message dicts ready for LLM
    """
    executor = ParallelToolExecutor(tool_mapping)
    results = executor.execute_tool_calls(tool_calls, verbose=verbose)
    return format_tool_results_for_messages(results)
