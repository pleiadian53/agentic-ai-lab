# Integration Guide: Evaluation Package with Research Agent

## Design Question: Should we integrate eval into tool_use/research_agent?

**Short Answer**: **Yes, but as an optional feature, not a core dependency.**

## Recommended Integration Strategy

### ✅ Option 1: Loose Coupling (Recommended)

Keep `eval` as a separate package that can optionally enhance `research_agent`:

**Pros:**
- ✅ Separation of concerns (research vs. evaluation)
- ✅ Users can use research_agent without evaluation overhead
- ✅ Easier to maintain and test independently
- ✅ Evaluation can be applied to other agents/workflows
- ✅ No circular dependencies

**Cons:**
- ⚠️ Requires explicit import and integration by users
- ⚠️ Not automatic out-of-the-box

**Implementation:**

```python
# In tool_use/research_agent/run_research_workflow.py

def run_research_workflow(
    topic: str,
    # ... existing params ...
    evaluate_sources: bool = False,  # Optional flag
    min_source_ratio: float = 0.5,
):
    """
    Run complete research workflow with optional source evaluation.
    
    Args:
        evaluate_sources: Enable source quality evaluation
        min_source_ratio: Minimum ratio of preferred sources
    """
    results = {}
    
    # Step 1: Research
    preliminary_report = generate_research_report_with_tools(topic, ...)
    results["preliminary_report"] = preliminary_report
    
    # Optional: Evaluate sources
    if evaluate_sources:
        try:
            from eval import evaluate_sources as eval_func
            eval_result = eval_func(preliminary_report, min_ratio=min_source_ratio)
            results["source_evaluation"] = eval_result
            
            if not eval_result.passed:
                print(f"⚠️ Source quality warning: {eval_result.ratio:.1%} preferred sources")
        except ImportError:
            print("⚠️ eval package not available, skipping source evaluation")
    
    # Continue with rest of workflow...
    return results
```

### ❌ Option 2: Tight Coupling (Not Recommended)

Make evaluation a core part of research_agent:

**Pros:**
- ✅ Automatic evaluation for all users
- ✅ Consistent quality checks

**Cons:**
- ❌ Adds complexity to research_agent
- ❌ Forces evaluation overhead on all users
- ❌ Harder to maintain (mixed concerns)
- ❌ Less flexible for users who don't need it

## Recommended Implementation Plan

### Phase 1: Keep Separate (Current State)

```text
agentic-ai-lab/
├── eval/                    # Standalone evaluation package
│   ├── __init__.py
│   ├── domain_evaluator.py
│   ├── metrics.py
│   ├── config.py
│   ├── visualize.py
│   ├── integration.py
│   └── README.md
│
└── tool_use/research_agent/ # Research agent (no eval dependency)
    ├── research_agent.py
    ├── run_research_workflow.py
    └── ...
```

### Phase 2: Add Optional Integration

Add evaluation as an **optional feature** in research_agent:

```python
# tool_use/research_agent/run_research_workflow.py

# Add CLI flag
parser.add_argument(
    "--evaluate-sources",
    action="store_true",
    help="Evaluate source quality (requires eval package)"
)

parser.add_argument(
    "--min-source-ratio",
    type=float,
    default=0.5,
    help="Minimum ratio of preferred sources (default: 0.5)"
)
```

### Phase 3: Document Integration

Update research_agent README with evaluation examples:

```markdown
## Optional: Source Quality Evaluation

The research agent can optionally evaluate source quality using the `eval` package:

\`\`\`bash
# With source evaluation
python run_research_workflow.py "quantum computing" --evaluate-sources --min-source-ratio 0.6
\`\`\`

\`\`\`python
# In Python/notebooks
from tool_use.research_agent import run_research_workflow

results = run_research_workflow(
    "quantum computing",
    evaluate_sources=True,
    min_source_ratio=0.6
)

if "source_evaluation" in results:
    print(results["source_evaluation"].status)
\`\`\`
```

## Integration Patterns

### Pattern 1: Callback-Based (Most Flexible)

```python
# research_agent.py
def generate_research_report_with_tools(
    prompt: str,
    evaluation_callback: Callable | None = None,
    ...
):
    # ... generate report ...
    
    # Optional evaluation callback
    if evaluation_callback:
        eval_result = evaluation_callback(final_text)
        if not eval_result.passed:
            print(f"⚠️ Source quality: {eval_result.ratio:.1%}")
    
    return final_text
```

Usage:

```python
from eval.integration import create_evaluation_callback

eval_callback = create_evaluation_callback(min_ratio=0.6)

report = generate_research_report_with_tools(
    "quantum computing",
    evaluation_callback=eval_callback
)
```

### Pattern 2: Decorator-Based (Clean API)

```python
from eval.integration import with_source_evaluation

@with_source_evaluation(min_ratio=0.5, auto_display=True)
def my_research_workflow(topic):
    return generate_research_report_with_tools(topic)

# Returns (output, evaluation)
output, eval_result = my_research_workflow("quantum computing")
```

### Pattern 3: Wrapper-Based (Object-Oriented)

```python
from eval.integration import EvaluatedResearchAgent

# Wrap existing function
agent = EvaluatedResearchAgent(
    generate_research_report_with_tools,
    min_ratio=0.6
)

# Use like normal function, but with evaluation
result = agent("quantum computing")
print(result.evaluation.status)

# Track performance over time
print(f"Pass rate: {agent.get_pass_rate():.1%}")
```

## Benefits of This Approach

### 1. Modularity
- `eval` package works with any text/JSON output
- Can evaluate outputs from other agents (email_agent, sql_agent, etc.)
- Easy to test in isolation

### 2. Flexibility
- Users choose when to enable evaluation
- Different evaluation criteria for different use cases
- Can swap evaluation strategies without changing research_agent

### 3. Maintainability
- Clear separation of concerns
- Changes to evaluation don't affect research logic
- Each package has focused responsibility

### 4. Extensibility
- Easy to add new evaluation types (e.g., content quality, citation accuracy)
- Can create domain-specific evaluators
- Evaluation package can grow independently

## Example: Full Integration

```python
# tool_use/research_agent/run_research_workflow.py

def run_research_workflow(
    topic: str,
    model: str = "gpt-4o",
    parallel: bool = True,
    generate_pdf: bool = True,
    evaluate_sources: bool = False,  # NEW
    min_source_ratio: float = 0.5,   # NEW
    preferred_domains: set[str] | None = None,  # NEW
    output_dir: str = "research_outputs",
    verbose: bool = True,
):
    """
    Run complete research workflow with optional evaluation.
    """
    results = {}
    
    # Step 1: Generate preliminary report
    if verbose:
        print("\n" + "="*80)
        print("STEP 1: GENERATING PRELIMINARY REPORT")
        print("="*80)
    
    preliminary_report = generate_research_report_with_tools(
        topic,
        model=model,
        parallel=parallel,
        verbose=verbose
    )
    results["preliminary_report"] = preliminary_report
    
    # Optional: Evaluate sources
    if evaluate_sources:
        if verbose:
            print("\n" + "="*80)
            print("EVALUATION: SOURCE QUALITY CHECK")
            print("="*80)
        
        try:
            from eval import DomainEvaluator
            
            evaluator = DomainEvaluator(
                preferred_domains=preferred_domains,
                min_ratio=min_source_ratio
            )
            eval_result = evaluator.evaluate_text(preliminary_report)
            results["source_evaluation"] = eval_result
            
            if verbose:
                print(eval_result.to_markdown(include_details=False))
            
            if not eval_result.passed:
                print(f"\n⚠️  WARNING: Source quality below threshold")
                print(f"    Preferred ratio: {eval_result.ratio:.1%} < {min_source_ratio:.0%}")
                print(f"    Consider adjusting search parameters or reviewing sources manually")
        
        except ImportError:
            if verbose:
                print("⚠️  eval package not available, skipping source evaluation")
                print("    Install with: pip install -e .")
    
    # Continue with rest of workflow (reflection, HTML, PDF)...
    
    return results
```

## Conclusion

**Recommendation**: Keep `eval` as a **separate, optional package** that integrates with `research_agent` through:

1. **Optional CLI flags** (`--evaluate-sources`, `--min-source-ratio`)
2. **Optional function parameters** (`evaluate_sources=True`)
3. **Callback/decorator patterns** for advanced users
4. **Clear documentation** showing integration examples

This provides the best balance of:
- ✅ Modularity and maintainability
- ✅ User flexibility and choice
- ✅ Clean separation of concerns
- ✅ Extensibility for future enhancements

The evaluation layer enhances the research agent without being tightly coupled to it.
