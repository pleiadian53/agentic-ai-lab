# Evaluation Package for Agentic AI Research Workflows

Component-level evaluation tools for assessing source quality in research agent outputs.

## Overview

This package provides tools to evaluate whether sources retrieved by research agents come from preferred/trusted domains. It implements **objective, per-example ground truth evaluation** as described in the M4 course module.

### Key Features

- ✅ **Domain-based evaluation**: Check if sources come from preferred domains
- ✅ **Flexible configuration**: Predefined domain sets (academic, government, news, etc.)
- ✅ **Multiple input formats**: Text, JSON, structured data
- ✅ **Rich visualization**: HTML and Markdown reports for notebooks
- ✅ **Integration ready**: Decorators and wrappers for existing workflows
- ✅ **Metrics tracking**: Aggregate statistics across multiple evaluations

## Quick Start

### Basic Usage

```python
from eval import evaluate_sources

# Evaluate text containing URLs
text = """
Recent papers on quantum computing:
- https://arxiv.org/abs/2301.12345
- https://nature.com/articles/s41586-023-12345
- https://random-blog.com/quantum-post
"""

result = evaluate_sources(text, min_ratio=0.5)
print(result.status)  # ✅ PASS or ❌ FAIL
print(f"Ratio: {result.ratio:.1%}")  # 66.7%
```

### In Jupyter Notebooks

```python
from eval import DomainEvaluator
from eval.visualize import display_evaluation

# Create evaluator
evaluator = DomainEvaluator(min_ratio=0.6)

# Evaluate research output
result = evaluator.evaluate_text(research_output)

# Display rich HTML report
display_evaluation(result)
```

### With Research Agent Integration

```python
from eval.integration import with_source_evaluation

@with_source_evaluation(min_ratio=0.5, auto_display=True)
def find_references(topic: str) -> str:
    # Your research function here
    return research_output

# Returns (output, evaluation_result)
output, eval_result = find_references("quantum computing")
```

## Installation

The package is part of the `agentic-ai-lab` repository. No additional installation needed if you have the repository cloned.

```bash
# Ensure you're in the project root
cd agentic-ai-lab

# The eval package is ready to use
python -c "from eval import evaluate_sources; print('✅ Ready!')"
```

## Module Structure

```text
eval/
├── __init__.py              # Package exports
├── config.py                # Domain configurations
├── domain_evaluator.py      # Core evaluation logic
├── metrics.py               # Result classes and metrics
├── visualize.py             # Notebook visualization
├── integration.py           # Research agent integration
└── README.md                # This file
```

## Core Components

### 1. Domain Evaluator

The main evaluation engine:

```python
from eval import DomainEvaluator

evaluator = DomainEvaluator(
    preferred_domains={'arxiv.org', 'nature.com'},
    min_ratio=0.5
)

# Evaluate different formats
result = evaluator.evaluate_text(text)
result = evaluator.evaluate_json(json_data)
result = evaluator.evaluate(any_data)  # Auto-detect format
```

### 2. Configuration

Predefined domain sets:

```python
from eval.config import (
    ACADEMIC_DOMAINS,      # arxiv.org, nature.com, etc.
    GOVERNMENT_DOMAINS,    # nasa.gov, nih.gov, etc.
    NEWS_DOMAINS,          # bbc.com, reuters.com, etc.
    DEFAULT_PREFERRED_DOMAINS  # All combined
)

# Or create custom sets
from eval.config import create_custom_domain_set

domains = create_custom_domain_set(
    'academic', 'government',
    extra_domains={'myjournal.org'}
)
```

### 3. Evaluation Results

Rich result objects:

```python
result = evaluate_sources(data)

# Access properties
result.passed          # True/False
result.total           # Total sources found
result.preferred       # Preferred sources count
result.ratio           # Preferred/total ratio
result.status          # "✅ PASS" or "❌ FAIL"

# Generate reports
print(result.to_markdown())
display(HTML(result.to_html()))
```

### 4. Visualization

Display results in notebooks:

```python
from eval.visualize import (
    display_evaluation,
    display_evaluation_summary,
    display_domain_comparison,
    print_html
)

# Single evaluation
display_evaluation(result)

# Multiple evaluations
display_evaluation_summary([result1, result2, result3])

# Compare two results
display_domain_comparison(before, after, "Before", "After")
```

### 5. Integration

Add evaluation to existing workflows:

```python
from eval.integration import (
    with_source_evaluation,
    EvaluatedResearchAgent,
    evaluate_research_workflow,
    create_evaluation_callback
)

# Decorator approach
@with_source_evaluation(min_ratio=0.5)
def my_research(topic):
    return research_output

# Wrapper approach
agent = EvaluatedResearchAgent(my_research, min_ratio=0.5)
result = agent("quantum computing")
print(f"Pass rate: {agent.get_pass_rate():.1%}")

# Callback approach
eval_callback = create_evaluation_callback(min_ratio=0.5)
eval_result = eval_callback(intermediate_output)
```

## Usage Examples

### Example 1: Evaluate Tavily Search Results

```python
from eval import evaluate_sources

# Tavily API response
tavily_results = [
    {"url": "https://arxiv.org/abs/2301.12345", "title": "Quantum Paper"},
    {"url": "https://nature.com/articles/123", "title": "Nature Article"},
    {"url": "https://random-blog.com/post", "title": "Blog Post"}
]

result = evaluate_sources(tavily_results, min_ratio=0.6)

if result.passed:
    print(f"✅ Quality check passed: {result.ratio:.1%} preferred sources")
else:
    print(f"❌ Quality check failed: {result.ratio:.1%} < {result.min_ratio:.0%}")
```

### Example 2: Evaluate Research Agent Output

```python
from eval import DomainEvaluator
from eval.config import ACADEMIC_DOMAINS

# Focus on academic sources only
evaluator = DomainEvaluator(
    preferred_domains=ACADEMIC_DOMAINS,
    min_ratio=0.7  # Require 70% academic sources
)

# Evaluate research output
research_output = generate_research_report("black hole science")
result = evaluator.evaluate_text(research_output)

# Display in notebook
from eval.visualize import display_evaluation
display_evaluation(result)
```

### Example 3: Batch Evaluation

```python
from eval import DomainEvaluator
from eval.metrics import compute_domain_metrics

evaluator = DomainEvaluator(min_ratio=0.5)

# Evaluate multiple topics
topics = ["quantum computing", "climate change", "gene editing"]
results = []

for topic in topics:
    output = research_function(topic)
    result = evaluator.evaluate(output)
    results.append(result)
    print(f"{topic}: {result.status}")

# Compute aggregate metrics
metrics = compute_domain_metrics(results)
print(f"\nOverall pass rate: {metrics['pass_rate']:.1%}")
print(f"Average ratio: {metrics['avg_ratio']:.1%}")
```

### Example 4: Integration with tool_use/research_agent

```python
# Add evaluation to existing research agent
from tool_use.research_agent import generate_research_report_with_tools
from eval.integration import with_source_evaluation

# Wrap the function
@with_source_evaluation(min_ratio=0.5, auto_display=True)
def evaluated_research(topic):
    return generate_research_report_with_tools(topic)

# Use it
output, eval_result = evaluated_research("extraterrestrial life")

if not eval_result.passed:
    print("⚠️ Warning: Low quality sources detected")
    print(f"Preferred ratio: {eval_result.ratio:.1%}")
```

### Example 5: Custom Domain Set for Specific Field

```python
from eval import DomainEvaluator

# Create domain set for astronomy research
astronomy_domains = {
    'arxiv.org',
    'nasa.gov',
    'eso.org',
    'stsci.edu',
    'aas.org',
    'iau.org',
    'nature.com',
    'science.org'
}

evaluator = DomainEvaluator(
    preferred_domains=astronomy_domains,
    min_ratio=0.6
)

result = evaluator.evaluate_text(astronomy_research_output)
```

## Configuration Options

### Threshold Levels

```python
from eval.config import (
    THRESHOLD_STRICT,    # 0.8 (80%)
    THRESHOLD_MODERATE,  # 0.6 (60%)
    THRESHOLD_LENIENT,   # 0.4 (40%)
)

# Use predefined thresholds
evaluator = DomainEvaluator(min_ratio=THRESHOLD_STRICT)
```

### Domain Categories

```python
from eval.config import get_domain_set

# Get specific category
academic = get_domain_set('academic')
government = get_domain_set('government')
all_domains = get_domain_set('all')
```

## Best Practices

### 1. Choose Appropriate Thresholds

- **Strict (80%+)**: For critical applications requiring high-quality sources
- **Moderate (60%+)**: For general research with balanced quality
- **Lenient (40%+)**: For exploratory research or broad topics

### 2. Customize Domain Lists

```python
# Start with a base set and add domain-specific sources
from eval.config import ACADEMIC_DOMAINS

my_domains = ACADEMIC_DOMAINS | {
    'myfield-journal.org',
    'specialized-database.edu'
}

evaluator = DomainEvaluator(preferred_domains=my_domains)
```

### 3. Track Metrics Over Time

```python
# Keep history of evaluations
evaluator = EvaluatedResearchAgent(research_func)

# Run multiple evaluations
for topic in topics:
    result = evaluator(topic)

# Analyze trends
print(f"Pass rate: {evaluator.get_pass_rate():.1%}")
print(f"Avg ratio: {evaluator.get_avg_ratio():.1%}")
```

### 4. Use Component-Level Evaluation

Evaluate individual steps rather than full pipelines:

```python
# ✅ Good: Evaluate research step separately
research_output = find_references(topic)
eval_result = evaluate_sources(research_output)

if eval_result.passed:
    # Continue with reflection and rewriting
    final_report = reflect_and_rewrite(research_output)

# ❌ Less efficient: Evaluate full pipeline each time
```

## Integration with Research Agent

### Option 1: Add as Optional Step

```python
# In tool_use/research_agent/run_research_workflow.py
from eval import evaluate_sources

def run_research_workflow(
    topic: str,
    evaluate_sources: bool = True,
    min_source_ratio: float = 0.5,
    ...
):
    # Step 1: Research
    preliminary_report = generate_research_report_with_tools(topic)
    
    # Optional: Evaluate sources
    if evaluate_sources:
        eval_result = evaluate_sources(preliminary_report, min_ratio=min_source_ratio)
        if not eval_result.passed:
            print(f"⚠️ Warning: Source quality below threshold ({eval_result.ratio:.1%})")
        results["source_evaluation"] = eval_result
    
    # Continue with workflow...
```

### Option 2: Add as Callback

```python
from eval.integration import create_evaluation_callback

eval_callback = create_evaluation_callback(min_ratio=0.5, verbose=True)

# Use in workflow
preliminary_report = generate_research_report_with_tools(topic)
eval_result = eval_callback(preliminary_report)  # Prints evaluation

if eval_result.passed:
    proceed_with_reflection()
```

## API Reference

See individual module docstrings for detailed API documentation:

- `eval.domain_evaluator`: Core evaluation logic
- `eval.metrics`: Result classes and metrics computation
- `eval.config`: Domain configuration
- `eval.visualize`: Notebook visualization
- `eval.integration`: Workflow integration

## Testing

```python
# Run basic tests
from eval import evaluate_sources

# Test with known good sources
good_text = "Check https://arxiv.org and https://nature.com"
result = evaluate_sources(good_text, min_ratio=0.5)
assert result.passed

# Test with known bad sources
bad_text = "Check https://random-blog.com"
result = evaluate_sources(bad_text, min_ratio=0.5)
assert not result.passed
```

## Troubleshooting

### Issue: No URLs detected

**Solution**: Ensure URLs are properly formatted (http:// or https://)

```python
# ❌ Won't work
text = "Check arxiv.org"

# ✅ Works
text = "Check https://arxiv.org"
```

### Issue: Unexpected pass/fail

**Solution**: Check domain matching logic

```python
# Subdomains are matched
'blog.arxiv.org' matches 'arxiv.org' ✅
'www.nature.com' matches 'nature.com' ✅

# But not partial matches
'arxiv.org.fake.com' does NOT match 'arxiv.org' ❌
```

### Issue: Import errors

**Solution**: Ensure you're importing from the correct location

```python
# ✅ Correct
from eval import evaluate_sources

# ❌ Wrong
from eval.M4 import evaluate_sources  # Old location
```

## Contributing

To add new domain categories or improve evaluation logic:

1. Add domains to `config.py`
2. Update tests
3. Document in this README

## License

Part of the agentic-ai-lab project.
