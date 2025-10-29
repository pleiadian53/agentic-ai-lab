# Enhanced Reflection Prompt

## Overview

The reflection prompt in `reflection/chart_workflow/llm.py` has been enhanced with a **structured critique framework** to enable more systematic and autonomous visual evaluation of generated charts.

## What Changed

### Before (Generic Prompt)

```text
You are a data visualization expert.
Your task: critique the attached chart image and the original code...
```

### After (Structured Critique Framework)

```text
You are an expert data visualization critic trained in perceptual psychology, 
information design, and best practices from Edward Tufte and Cleveland-McGill research.

CRITIQUE FRAMEWORK - Evaluate the attached chart systematically:

1. CHART TYPE APPROPRIATENESS
2. PERCEPTUAL ACCURACY & TRUTHFULNESS  
3. CLARITY & READABILITY
4. DATA-INK RATIO (Tufte's Principle)
5. STATISTICAL INTEGRITY
```

## Five Evaluation Dimensions

### 1. Chart Type Appropriateness

- Matches data structure to visual encoding
- Temporal data → line/area charts
- Categorical comparisons → bar charts
- Distributions → histograms/box plots
- Suggests better alternatives (e.g., horizontal bars for long labels)

### 2. Perceptual Accuracy & Truthfulness

- Honest visual encodings (bar charts start at 0)
- Appropriate aspect ratios (avoid compressing trends)
- Easy comparisons (aligned baselines, consistent scales)

### 3. Clarity & Readability

- Legible labels (font size ≥10pt, no overlap)
- Well-positioned legends (or removed if redundant)
- Accessible colors (colorblind-safe palettes)
- Descriptive axis labels and titles

### 4. Data-Ink Ratio (Tufte's Principle)

- Remove chart junk (unnecessary gridlines, 3D effects)
- Maximize information density
- Use direct labeling instead of legends when possible

### 5. Statistical Integrity

- Show error bars/confidence intervals when appropriate
- Handle outliers properly (annotate or explain)
- Clarify aggregation methods (mean vs median)

## Benefits

✅ **Autonomous critique**: LLM can identify visual flaws without explicit user instructions  
✅ **Systematic evaluation**: Covers all major aspects of visualization quality  
✅ **Grounded in theory**: References established design principles (Tufte, Cleveland-McGill)  
✅ **Backward compatible**: Same output format (JSON feedback + code)  
✅ **No workflow changes**: Existing code continues to work unchanged  

## Usage

The enhanced prompt is automatically used in the reflection workflow:

```python
from reflection.chart_workflow import run_reflection_workflow, ChartWorkflowConfig

config = ChartWorkflowConfig(
    generation_model="gpt-4o",
    reflection_model="claude-3-5-sonnet-20241022",  # Vision model
    max_iterations=3,
)

artifacts = run_reflection_workflow(
    dataset="data/sales.csv",
    instruction="Visualize sales trends",
    config=config,
)

# The reflection step now uses the enhanced critique framework
print(artifacts.iterations[1].feedback)  # Structured critique
```

## Example Output

**Before Enhancement:**

```json
{"feedback": "The chart looks okay but could be improved."}
```

**After Enhancement:**

```json
{
  "feedback": "Chart type is appropriate for temporal data. However, axis labels overlap (readability issue), legend obscures data points (clarity issue), and excessive gridlines reduce data-ink ratio. Recommend: rotate x-axis labels 45°, move legend outside plot area, reduce gridline opacity to 0.3."
}
```

## Implementation Details

- **File modified**: `reflection/chart_workflow/llm.py`
- **Function**: `build_reflection_prompt()` (lines 73-138)
- **Backward compatibility**: ✅ Maintained (same function signature and output format)
- **Testing**: Run `tests/chart_workflow/scripts/test_enhanced_reflection_prompt.py`

## Next Steps

This is the first enhancement in a systematic improvement plan:

1. ✅ **Enhanced Reflection Prompt** (implemented)
2. ⏳ Data-driven chart type selection (analyze data structure)
3. ⏳ Multi-step reasoning chain (describe → critique → propose → implement)
4. ⏳ Reference examples (few-shot learning with good/bad pairs)
5. ⏳ Tool use for data exploration (query statistics before deciding)

## References

- **Edward Tufte**: *The Visual Display of Quantitative Information* (data-ink ratio, chart junk)
- **Cleveland & McGill**: *Graphical Perception* (perceptual accuracy hierarchy)
- **Ware**: *Information Visualization: Perception for Design* (perceptual psychology)
