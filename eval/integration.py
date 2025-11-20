"""
Integration with research_agent workflows.

Provides decorators and wrappers to add evaluation capabilities
to existing research agent functions.
"""

import functools
from typing import Callable, Any

from .domain_evaluator import DomainEvaluator
from .metrics import EvaluationResult
from .config import DEFAULT_PREFERRED_DOMAINS, DEFAULT_MIN_RATIO


def with_source_evaluation(
    preferred_domains: set[str] | None = None,
    min_ratio: float = DEFAULT_MIN_RATIO,
    auto_display: bool = False
):
    """
    Decorator to add source evaluation to research functions.
    
    The decorated function will return a tuple of (original_result, evaluation_result).
    
    Args:
        preferred_domains: Set of preferred domains
        min_ratio: Minimum ratio for passing
        auto_display: Automatically display evaluation in notebooks
        
    Examples:
        >>> @with_source_evaluation(min_ratio=0.5)
        ... def my_research(topic):
        ...     return "Results with https://arxiv.org/abs/1234"
        >>> result, eval_result = my_research("quantum computing")
        >>> eval_result.passed
        True
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Call original function
            result = func(*args, **kwargs)
            
            # Evaluate the result
            evaluator = DomainEvaluator(preferred_domains, min_ratio)
            eval_result = evaluator.evaluate(result)
            
            # Auto-display if requested
            if auto_display:
                try:
                    from .visualize import display_evaluation
                    display_evaluation(eval_result)
                except ImportError:
                    pass
            
            return result, eval_result
        
        return wrapper
    return decorator


class EvaluatedResearchAgent:
    """
    Wrapper for research agent functions that adds automatic evaluation.
    
    This class wraps research functions and automatically evaluates their
    outputs for source quality.
    
    Examples:
        >>> def my_research(topic):
        ...     return "Results with https://arxiv.org/abs/1234"
        >>> agent = EvaluatedResearchAgent(my_research, min_ratio=0.5)
        >>> result = agent("quantum computing")
        >>> result.evaluation.passed
        True
    """
    
    def __init__(
        self,
        research_func: Callable,
        preferred_domains: set[str] | None = None,
        min_ratio: float = DEFAULT_MIN_RATIO,
        auto_display: bool = False
    ):
        """
        Initialize evaluated research agent.
        
        Args:
            research_func: Function that performs research
            preferred_domains: Set of preferred domains
            min_ratio: Minimum ratio for passing
            auto_display: Automatically display evaluation
        """
        self.research_func = research_func
        self.evaluator = DomainEvaluator(preferred_domains, min_ratio)
        self.auto_display = auto_display
        self.history: list[tuple[Any, EvaluationResult]] = []
    
    def __call__(self, *args, **kwargs) -> "ResearchResult":
        """Execute research and evaluation."""
        # Call research function
        output = self.research_func(*args, **kwargs)
        
        # Evaluate
        evaluation = self.evaluator.evaluate(output)
        
        # Store in history
        self.history.append((output, evaluation))
        
        # Auto-display if requested
        if self.auto_display:
            try:
                from .visualize import display_evaluation
                display_evaluation(evaluation)
            except ImportError:
                pass
        
        return ResearchResult(output, evaluation)
    
    def get_pass_rate(self) -> float:
        """Get pass rate across all evaluations in history."""
        if not self.history:
            return 0.0
        passed = sum(1 for _, eval_result in self.history if eval_result.passed)
        return passed / len(self.history)
    
    def get_avg_ratio(self) -> float:
        """Get average preferred ratio across all evaluations."""
        if not self.history:
            return 0.0
        return sum(eval_result.ratio for _, eval_result in self.history) / len(self.history)


class ResearchResult:
    """
    Container for research output and its evaluation.
    
    Attributes:
        output: Original research output
        evaluation: EvaluationResult object
    """
    
    def __init__(self, output: Any, evaluation: EvaluationResult):
        self.output = output
        self.evaluation = evaluation
    
    @property
    def passed(self) -> bool:
        """Whether evaluation passed."""
        return self.evaluation.passed
    
    def __str__(self) -> str:
        """String representation."""
        return str(self.output)
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"ResearchResult(passed={self.passed}, ratio={self.evaluation.ratio:.2%})"


def evaluate_research_workflow(
    workflow_func: Callable,
    preferred_domains: set[str] | None = None,
    min_ratio: float = DEFAULT_MIN_RATIO,
    step_name: str = "research"
) -> Callable:
    """
    Decorator for full research workflows that evaluates a specific step.
    
    The workflow function should return a dict with a key matching step_name
    containing the research output to evaluate.
    
    Args:
        workflow_func: Workflow function returning dict
        preferred_domains: Set of preferred domains
        min_ratio: Minimum ratio for passing
        step_name: Key in result dict to evaluate
        
    Examples:
        >>> @evaluate_research_workflow(step_name="preliminary_report")
        ... def workflow(topic):
        ...     return {"preliminary_report": "Results with https://arxiv.org"}
        >>> result = workflow("quantum computing")
        >>> result["evaluation"].passed
        True
    """
    @functools.wraps(workflow_func)
    def wrapper(*args, **kwargs):
        # Call original workflow
        result = workflow_func(*args, **kwargs)
        
        # Extract step to evaluate
        if isinstance(result, dict) and step_name in result:
            step_output = result[step_name]
            
            # Evaluate
            evaluator = DomainEvaluator(preferred_domains, min_ratio)
            evaluation = evaluator.evaluate(step_output)
            
            # Add evaluation to result
            result["evaluation"] = evaluation
        
        return result
    
    return wrapper


def create_evaluation_callback(
    preferred_domains: set[str] | None = None,
    min_ratio: float = DEFAULT_MIN_RATIO,
    verbose: bool = True
) -> Callable:
    """
    Create a callback function for use in research workflows.
    
    The callback can be called at any point in a workflow to evaluate
    intermediate results.
    
    Args:
        preferred_domains: Set of preferred domains
        min_ratio: Minimum ratio for passing
        verbose: Print evaluation results
        
    Returns:
        Callback function that takes data and returns EvaluationResult
        
    Examples:
        >>> eval_callback = create_evaluation_callback(min_ratio=0.5)
        >>> result = eval_callback("Results with https://arxiv.org")
        >>> result.passed
        True
    """
    evaluator = DomainEvaluator(preferred_domains, min_ratio)
    
    def callback(data: Any) -> EvaluationResult:
        """Evaluate data and optionally print results."""
        result = evaluator.evaluate(data)
        
        if verbose:
            print(result.to_markdown(include_details=False))
        
        return result
    
    return callback
