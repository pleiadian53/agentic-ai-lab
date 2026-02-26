# Report Length Configuration Guide

## Overview

The Research Agent now supports **configurable report lengths** to generate anything from brief summaries to comprehensive technical papers.

## No Hard Limits in Current Implementation ✅

**Good news**: There are NO hard-coded word or token limits in the system:
- No `max_tokens` parameter in LLM calls
- No length constraints in agent prompts
- No truncation in the pipeline

The only limits are the **model's native output capacity**.

## Model Output Capacities

| Model | Context Window | Max Output Tokens | Best For |
|-------|---------------|-------------------|----------|
| `gpt-4o-mini` | 128K | ~16K tokens (~12K words) | Brief-Standard reports |
| `gpt-4o` | 128K | ~16K tokens (~12K words) | Standard reports |
| `gpt-5` | 200K | ~32K tokens (~24K words) | Comprehensive reports |
| `gpt-5.1` | 200K | ~64K tokens (~48K words) | Technical papers |
| `gpt-5-pro` | 1M | ~100K tokens (~75K words) | Long-form papers |

## Report Length Options

### 1. **Brief** (2-3 pages, ~1,500-2,500 words)
- **Sections**: 3-4 main sections
- **Depth**: High-level overview with key findings
- **Plan Steps**: 8-12 steps
- **Use Cases**: Executive summaries, quick overviews
- **Recommended Model**: `gpt-4o-mini`

### 2. **Standard** (5-10 pages, ~3,500-7,000 words) [DEFAULT]
- **Sections**: 5-7 main sections with subsections
- **Depth**: Balanced coverage with detailed analysis
- **Plan Steps**: 12-18 steps
- **Use Cases**: Standard research reports, whitepapers
- **Recommended Model**: `gpt-4o` or `gpt-5`

### 3. **Comprehensive** (15-25 pages, ~10,000-18,000 words)
- **Sections**: 8-12 main sections with multiple subsections
- **Depth**: In-depth analysis, extensive literature review
- **Plan Steps**: 20-30 steps
- **Use Cases**: Detailed technical reports, grant proposals
- **Recommended Model**: `gpt-5` or `gpt-5.1`

### 4. **Technical Paper** (25-40 pages, ~18,000-30,000 words)
- **Sections**: Full academic structure (Abstract, Intro, Lit Review, Methodology, Results, Discussion, Conclusion, References)
- **Depth**: Publication-quality with comprehensive citations
- **Plan Steps**: 30-50 steps
- **Use Cases**: Academic publications (Nature, Science, IEEE), PhD dissertations
- **Recommended Model**: `gpt-5.1` or `gpt-5-pro`

## Usage Examples

### CLI

```bash
# Brief report (2-3 pages)
python -m multiagent.research_agent.run "CRISPR gene editing" --length brief --model openai:gpt-4o-mini

# Standard report (5-10 pages) - DEFAULT
python -m multiagent.research_agent.run "Quantum computing advances" --model openai:gpt-4o

# Comprehensive report (15-25 pages)
python -m multiagent.research_agent.run "Climate change mitigation strategies" \
    --length comprehensive \
    --model openai:gpt-5

# Technical paper (25-40 pages)
python -m multiagent.research_agent.run "Novel cancer immunotherapy approaches" \
    --length technical-paper \
    --model openai:gpt-5.1
```

### Python API

```python
from multiagent.research_agent import pipeline

# Brief report
result = pipeline.generate_research_report(
    topic="AI safety research",
    model="openai:gpt-4o-mini",
    report_length="brief"
)

# Technical paper
result = pipeline.generate_research_report(
    topic="Quantum error correction codes",
    model="openai:gpt-5.1",
    report_length="technical-paper"
)
```

### Web API

```bash
curl -X POST http://localhost:8004/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Recent advances in quantum computing",
    "model": "openai:gpt-5.1",
    "report_length": "technical-paper",
    "context": "Focus on error correction and scalability. Include both theoretical and experimental work."
  }'
```

## How It Works

### 1. Planner Agent Enhancement

The planner receives length-specific guidance:

```python
length_specs = {
    "technical-paper": {
        "pages": "25-40 pages",
        "sections": "Full academic structure: Abstract, Introduction, Literature Review...",
        "depth": "Publication-quality depth with comprehensive citations",
        "steps": "30-50 steps"
    }
}
```

This guides the planner to create:
- **More research steps**: Multiple arXiv searches, Europe PMC queries, web searches
- **Detailed writing steps**: Separate steps for each major section
- **Multiple editing passes**: Structure, clarity, citations, final polish

### 2. Writer Agent Behavior

The Writer Agent naturally produces longer content when given more specific tasks:

**Brief**: "Draft introduction" → 1-2 paragraphs  
**Standard**: "Draft introduction section" → 3-5 paragraphs  
**Comprehensive**: "Draft comprehensive introduction with background and significance" → 1-2 pages  
**Technical Paper**: "Draft introduction section covering background, significance, and research objectives" → 2-3 pages

### 3. Multi-Pass Editing

Longer reports include multiple editing passes:
- **Brief**: 1 editing pass
- **Standard**: 1-2 editing passes
- **Comprehensive**: 2-3 editing passes (structure, clarity, citations)
- **Technical Paper**: 3-4 editing passes (structure, technical accuracy, citations, final polish)

## Best Practices for Long Reports

### 1. Use Premium Models

For technical papers (25-40 pages):
```python
{
    "planner": "gpt-5.1-codex",  # Structured planning
    "research": "gpt-5-pro",      # Deep analysis
    "writer": "gpt-5.1",          # Best prose
    "editor": "gpt-5-pro"         # Rigorous review
}
```

### 2. Provide Detailed Context

```python
context = """
Focus on papers from 2024-2025.
Include both theoretical foundations and experimental validations.
Cover surface codes, topological codes, and LDPC codes.
Discuss scalability challenges and recent breakthroughs.
Target audience: quantum computing researchers.
"""
```

### 3. Expect Longer Generation Time

| Length | Typical Time | Steps | Tool Calls |
|--------|-------------|-------|------------|
| Brief | 2-4 minutes | 8-12 | 5-10 |
| Standard | 4-8 minutes | 12-18 | 10-20 |
| Comprehensive | 10-20 minutes | 20-30 | 25-40 |
| Technical Paper | 20-40 minutes | 30-50 | 40-70 |

### 4. Monitor Costs

Approximate costs (using GPT-5.1 for technical paper):
- **Input tokens**: ~50K-100K (context, tool results)
- **Output tokens**: ~40K-60K (25-40 pages)
- **Estimated cost**: $15-30 per technical paper

## Troubleshooting

### Report Too Short

**Problem**: Generated report is shorter than expected

**Solutions**:
1. Use a more capable model (`gpt-5.1` instead of `gpt-4o-mini`)
2. Provide more detailed context
3. Increase report length setting
4. Check if planner generated enough steps

### Report Incomplete

**Problem**: Report cuts off mid-section

**Solutions**:
1. Use model with higher output capacity (`gpt-5.1` or `gpt-5-pro`)
2. Break into multiple writing steps (planner should do this automatically)
3. Check for API errors in logs

### Inconsistent Quality

**Problem**: Some sections detailed, others superficial

**Solutions**:
1. Use consistent model across all agents
2. Ensure planner creates balanced steps
3. Add more editing passes
4. Use `gpt-5-pro` for editor agent

## Future Enhancements

Planned improvements:
- [ ] Automatic section-by-section assembly for very long reports
- [ ] Progress tracking for long-running generations
- [ ] Intermediate checkpoints and resume capability
- [ ] PDF export with proper formatting
- [ ] Citation management (BibTeX export)
- [ ] Figure/diagram generation integration

## Summary

✅ **No hard limits** - only model output capacity  
✅ **Four length tiers** - brief to technical paper  
✅ **Configurable via CLI, API, and web interface**  
✅ **Intelligent planning** - more steps for longer reports  
✅ **Model recommendations** - match model to report length  

For publication-quality technical papers, use:
```bash
python -m multiagent.research_agent.run "Your Topic" \
    --length technical-paper \
    --model openai:gpt-5.1
```
