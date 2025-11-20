# Enhanced Research Agent with Integrated Evaluation

Production-ready research agent that combines research generation with component-wise source evaluation to improve output quality.

## Overview

This package extends the base research agent (`tool_use/research_agent`) with **integrated evaluation capabilities** that assess source quality during the research process and automatically retry with improved prompts if sources are insufficient.

### Key Enhancements

| Feature | Base Agent | Evaluated Agent |
|---------|------------|-----------------|
| **Source Evaluation** | ❌ No | ✅ Real-time evaluation |
| **Quality Feedback** | ❌ No | ✅ Automatic retry if poor |
| **Domain Filtering** | ❌ No | ✅ Configurable preferred domains |
| **Evaluation Metrics** | ❌ No | ✅ Comprehensive metrics |
| **Reflection with Context** | ⚠️ Basic | ✅ Includes evaluation feedback |
| **Research Tools** | ⚠️ Basic | ✅ Production tools from eval/ |

## Quick Start

### Basic Usage

```python
from eval.research_agent import EvaluatedResearchAgent
from eval import ACADEMIC_DOMAINS

# Initialize agent
agent = EvaluatedResearchAgent(
    preferred_domains=ACADEMIC_DOMAINS,
    min_source_ratio=0.5,  # Require 50% from preferred domains
    max_retries=2
)

# Generate research report
results = agent.generate_report("quantum computing applications")

# Check evaluation
print(f"Status: {results['evaluation'].status}")
print(f"Source quality: {results['evaluation'].preferred_ratio:.1%}")
print(f"Retries needed: {results['retry_count']}")

# Access the report
print(results['report'])
```

### Command-Line Usage

```bash
# Basic research
python -m eval.research_agent.workflow "quantum computing"

# With biology-focused domains
python -m eval.research_agent.workflow "CRISPR gene editing" --domains biology

# High quality threshold (70% preferred sources)
python -m eval.research_agent.workflow "climate change" --min-ratio 0.7

# Fast mode (skip reflection)
python -m eval.research_agent.workflow "AI safety" --no-reflection

# Custom output directory
python -m eval.research_agent.workflow "RNA therapeutics" \
    --output-dir ./my_research \
    --domains biology \
    --min-ratio 0.6
```

## How It Works

### The Evaluation Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                    Evaluated Research Workflow                   │
└─────────────────────────────────────────────────────────────────┘

1. GENERATE RESEARCH REPORT
   ├─ LLM uses tools (arXiv, Tavily, Wikipedia)
   ├─ Gathers information and writes report
   └─ Returns report with sources

2. EVALUATE SOURCES
   ├─ Extract URLs from report
   ├─ Check against preferred domains
   ├─ Compute quality ratio
   └─ Status: PASS or FAIL

3. DECISION POINT
   ├─ If PASS → Continue to next step
   └─ If FAIL → Retry with improved prompt
       ├─ Add domain guidance
       ├─ Emphasize quality sources
       └─ Repeat (up to max_retries)

4. REFLECTION (Optional)
   ├─ Include evaluation feedback
   ├─ Analyze source quality
   └─ Generate improved version

5. OUTPUT
   ├─ Final report (text)
   ├─ Evaluation metrics
   ├─ HTML version
   └─ All intermediate outputs
```

### Automatic Quality Improvement

The agent automatically improves source quality through:

1. **Initial Attempt**: Standard research prompt
2. **Evaluation**: Check if sources meet quality threshold
3. **Retry with Guidance**: If quality is poor, retry with:
   - Explicit instructions to use preferred domains
   - List of high-quality source types
   - Emphasis on academic/authoritative sources
4. **Best Result**: Return best result after all retries

## Complete Workflow

### Full Example

```python
from eval.research_agent import run_evaluated_workflow
from eval import BIOLOGY_FOCUSED_DOMAINS

results = run_evaluated_workflow(
    topic="mRNA vaccine technology",
    output_dir="./research_outputs",
    preferred_domains=BIOLOGY_FOCUSED_DOMAINS,
    min_source_ratio=0.6,
    max_retries=2,
    save_intermediate=True,
    generate_html=True,
    run_reflection=True,
    verbose=True
)

# Access results
print(f"Topic: {results['topic']}")
print(f"Status: {results['evaluation'].status}")
print(f"Retries: {results['retry_count']}")

# Files generated
for key, path in results['files'].items():
    print(f"{key}: {path}")
```

### Output Files

The workflow generates:

```
evaluated_research_outputs/
├── 20241113_223045_mRNA_vaccine_technology_preliminary.txt
├── 20241113_223045_mRNA_vaccine_technology_evaluation.md
├── 20241113_223045_mRNA_vaccine_technology_reflection.txt
├── 20241113_223045_mRNA_vaccine_technology_revised.txt
├── 20241113_223045_mRNA_vaccine_technology_revised_evaluation.md
└── 20241113_223045_mRNA_vaccine_technology_report.html
```

## Configuration Options

### Domain Sets

Choose from predefined domain sets:

```python
from eval import (
    ACADEMIC_DOMAINS,           # General academic sources
    BIOLOGY_FOCUSED_DOMAINS,    # Biology/life sciences
    NEWS_DOMAINS,               # News outlets
    GOVERNMENT_DOMAINS          # Government sources
)

# Or create custom
custom_domains = [
    "arxiv.org",
    "nature.com",
    "science.org",
    "nih.gov"
]

agent = EvaluatedResearchAgent(preferred_domains=custom_domains)
```

### Quality Thresholds

```python
# Lenient (40% preferred sources)
agent = EvaluatedResearchAgent(min_source_ratio=0.4)

# Moderate (50% - default)
agent = EvaluatedResearchAgent(min_source_ratio=0.5)

# Strict (70% preferred sources)
agent = EvaluatedResearchAgent(min_source_ratio=0.7)
```

### Retry Strategy

```python
# No retries (fastest)
agent = EvaluatedResearchAgent(max_retries=0)

# Moderate retries (default)
agent = EvaluatedResearchAgent(max_retries=2)

# Aggressive retries (best quality)
agent = EvaluatedResearchAgent(max_retries=5)
```

## API Reference

### EvaluatedResearchAgent

**Constructor:**

```python
agent = EvaluatedResearchAgent(
    preferred_domains=None,      # List of preferred domains (default: ACADEMIC_DOMAINS)
    min_source_ratio=0.4,        # Minimum ratio of preferred sources
    model="gpt-4o",              # OpenAI model for research
    reflection_model="gpt-4o-mini",  # Model for reflection
    max_retries=2,               # Maximum retries if quality is poor
    verbose=True                 # Print progress messages
)
```

**Methods:**

```python
# Generate research report with evaluation
results = agent.generate_report(
    prompt="research topic",
    max_turns=10,
    evaluate_sources=True
)
# Returns: dict with keys: report, evaluation, tool_calls, messages, retry_count

# Reflect and rewrite with evaluation feedback
reflection = agent.reflect_and_rewrite(
    report="...",
    evaluation=eval_result  # Optional
)
# Returns: dict with keys: reflection, revised_report

# Convert to HTML
html = agent.convert_to_html(report="...")
# Returns: HTML string
```

### run_evaluated_workflow

**Function:**

```python
results = run_evaluated_workflow(
    topic="research topic",
    output_dir="./outputs",
    preferred_domains=None,
    min_source_ratio=0.5,
    max_retries=2,
    save_intermediate=True,
    generate_html=True,
    run_reflection=True,
    verbose=True
)
```

**Returns:**

```python
{
    "topic": "...",
    "timestamp": "...",
    "preliminary_report": "...",
    "evaluation": EvaluationResult(...),
    "reflection": "...",
    "revised_report": "...",
    "revised_evaluation": EvaluationResult(...),
    "html": "...",
    "retry_count": 0,
    "tool_calls": [...],
    "files": {
        "preliminary_report": "path/to/file.txt",
        "evaluation": "path/to/eval.md",
        ...
    },
    "config": {...}
}
```

## Evaluation Metrics

### EvaluationResult Object

```python
evaluation = results['evaluation']

# Status
print(evaluation.status)  # "PASS" or "FAIL"

# Counts
print(evaluation.total_sources)      # Total URLs found
print(evaluation.preferred_count)    # Preferred domain count
print(evaluation.other_count)        # Other domain count

# Ratio
print(evaluation.preferred_ratio)    # 0.0 to 1.0

# Sources
for source in evaluation.preferred_sources:
    print(f"{source.domain}: {source.url}")

# Export
markdown = evaluation.to_markdown()
html = evaluation.to_html()
```

## Advanced Usage

### Custom Evaluation Logic

```python
from eval import DomainEvaluator

# Create custom evaluator
evaluator = DomainEvaluator(
    preferred_domains=["arxiv.org", "nature.com"],
    min_ratio=0.7
)

# Use in agent
agent = EvaluatedResearchAgent(
    preferred_domains=evaluator.preferred_domains,
    min_source_ratio=evaluator.min_ratio
)
```

### Programmatic Workflow Control

```python
agent = EvaluatedResearchAgent()

# Step 1: Generate
research = agent.generate_report("topic", evaluate_sources=True)

# Step 2: Check quality
if research['evaluation'].status == "FAIL":
    print("⚠️  Poor source quality detected")
    print(f"Only {research['evaluation'].preferred_ratio:.1%} from preferred domains")

# Step 3: Reflect with evaluation context
reflection = agent.reflect_and_rewrite(
    research['report'],
    evaluation=research['evaluation']
)

# Step 4: Convert to HTML
html = agent.convert_to_html(reflection['revised_report'])

# Step 5: Save
Path("output.html").write_text(html)
```

### Batch Processing

```python
topics = [
    "quantum computing",
    "CRISPR gene editing",
    "climate change mitigation"
]

agent = EvaluatedResearchAgent(min_source_ratio=0.6)

for topic in topics:
    print(f"\nResearching: {topic}")
    results = agent.generate_report(topic)
    
    print(f"Quality: {results['evaluation'].preferred_ratio:.1%}")
    print(f"Retries: {results['retry_count']}")
    
    # Save report
    filename = topic.replace(" ", "_") + ".txt"
    Path(filename).write_text(results['report'])
```

## Comparison with Base Agent

### Base Agent (tool_use/research_agent)

```python
from tool_use.research_agent import generate_research_report_with_tools

# Generate report
report = generate_research_report_with_tools("quantum computing")

# No evaluation - you don't know source quality
# No automatic retry
# No quality metrics
```

### Evaluated Agent (eval/research_agent)

```python
from eval.research_agent import EvaluatedResearchAgent

agent = EvaluatedResearchAgent(min_source_ratio=0.5)
results = agent.generate_report("quantum computing")

# ✅ Automatic source evaluation
# ✅ Retry if quality is poor
# ✅ Comprehensive metrics
# ✅ Evaluation feedback in reflection

print(f"Quality: {results['evaluation'].preferred_ratio:.1%}")
print(f"Status: {results['evaluation'].status}")
```

## Best Practices

### 1. Choose Appropriate Domain Sets

```python
# For scientific research
agent = EvaluatedResearchAgent(preferred_domains=ACADEMIC_DOMAINS)

# For biology/life sciences
agent = EvaluatedResearchAgent(preferred_domains=BIOLOGY_FOCUSED_DOMAINS)

# For current events
agent = EvaluatedResearchAgent(preferred_domains=NEWS_DOMAINS)
```

### 2. Set Realistic Quality Thresholds

```python
# Exploratory research (lenient)
agent = EvaluatedResearchAgent(min_source_ratio=0.3)

# Standard research (balanced)
agent = EvaluatedResearchAgent(min_source_ratio=0.5)

# Academic paper (strict)
agent = EvaluatedResearchAgent(min_source_ratio=0.7)
```

### 3. Balance Speed vs. Quality

```python
# Fast (no retries, no reflection)
results = run_evaluated_workflow(
    topic,
    max_retries=0,
    run_reflection=False
)

# Balanced (default)
results = run_evaluated_workflow(
    topic,
    max_retries=2,
    run_reflection=True
)

# High quality (more retries)
results = run_evaluated_workflow(
    topic,
    max_retries=5,
    run_reflection=True,
    min_source_ratio=0.7
)
```

### 4. Monitor Evaluation Results

```python
results = agent.generate_report(topic)

if results['retry_count'] > 0:
    print(f"⚠️  Required {results['retry_count']} retries")

if results['evaluation'].status == "FAIL":
    print("❌ Failed to meet quality threshold")
    print(f"   Only {results['evaluation'].preferred_ratio:.1%} from preferred domains")
else:
    print(f"✅ Quality threshold met: {results['evaluation'].preferred_ratio:.1%}")
```

## Troubleshooting

### Low Source Quality

**Problem**: Agent consistently fails to meet quality threshold

**Solutions**:
1. Lower the threshold: `min_source_ratio=0.3`
2. Increase retries: `max_retries=5`
3. Expand domain list: Add more acceptable domains
4. Check if topic has limited academic sources

### Too Many Retries

**Problem**: Agent uses all retries but still fails

**Solutions**:
1. Topic may not have sufficient academic sources
2. Try different domain set (e.g., NEWS_DOMAINS for current events)
3. Lower quality threshold
4. Check if preferred domains are too restrictive

### Slow Performance

**Problem**: Workflow takes too long

**Solutions**:
1. Disable reflection: `run_reflection=False`
2. Reduce retries: `max_retries=1`
3. Skip HTML generation: `generate_html=False`
4. Use faster model: `reflection_model="gpt-4o-mini"`

## Examples

See `eval/research_agent/examples/` for complete working examples:

- `basic_usage.py` - Simple research with evaluation
- `custom_domains.py` - Using custom domain sets
- `batch_research.py` - Processing multiple topics
- `quality_comparison.py` - Comparing base vs. evaluated agent

## See Also

- [eval/README.md](../README.md) - Main evaluation package documentation
- [eval/RESEARCH_TOOLS_GUIDE.md](../RESEARCH_TOOLS_GUIDE.md) - Production research tools
- [eval/INTEGRATION_GUIDE.md](../INTEGRATION_GUIDE.md) - Integration patterns
- [tool_use/research_agent/README.md](../../tool_use/research_agent/README.md) - Base research agent

## License

Same as parent project.
