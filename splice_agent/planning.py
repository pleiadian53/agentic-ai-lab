"""LLM-based chart code generation (code-as-plan approach).

This module generates Python plotting code from user requests and dataset descriptions.
Similar to customer_service planning.py but specialized for chart generation.
"""

from __future__ import annotations

from typing import Any, Optional

from openai import OpenAI

from .data_access import ChartDataset

from .llm_client import call_llm_text


# =========================
# Planning Specification
# =========================

CHART_GENERATION_SPEC = """You are an expert data visualization specialist. Generate Python code to create charts from datasets.

REQUIREMENTS:
1. Analyze the dataset schema and sample data
2. Understand the user's visualization request
3. Generate complete, executable Python code
4. Use appropriate chart types and libraries
5. Follow visualization best practices

AVAILABLE LIBRARIES:
- matplotlib.pyplot as plt (for basic charts)
- seaborn as sns (for statistical visualizations)
- plotly.express as px (for interactive charts)
- pandas as pd (data is already loaded as 'df')

GUIDELINES:
1. **Chart Selection:**
   - Bar/Column: Categorical comparisons
   - Line: Trends over time
   - Scatter: Relationships between variables
   - Histogram: Distribution of single variable
   - Box/Violin: Distribution comparisons
   - Heatmap: Correlation matrices
   - Pie: Part-to-whole (use sparingly)

2. **Code Structure:**
   ```python
   import matplotlib.pyplot as plt
   import seaborn as sns
   # import plotly.express as px  # if using plotly
   
   # Data is already loaded as 'df'
   # Your plotting code here
   
   # For matplotlib/seaborn:
   plt.figure(figsize=(10, 6))
   # ... plotting code ...
   plt.title("Chart Title")
   plt.xlabel("X Label")
   plt.ylabel("Y Label")
   plt.tight_layout()
   # Chart will be captured automatically
   
   # For plotly:
   # fig = px.bar(df, x='column', y='value')
   # fig.update_layout(title="Chart Title")
   # Chart will be captured automatically
   ```

3. **Best Practices:**
   - Clear, descriptive titles and labels
   - Appropriate figure size
   - Readable fonts and colors
   - Handle missing data gracefully
   - Use tight_layout() for matplotlib
   - Add legends when multiple series
   - Use color palettes wisely

4. **Data Preparation:**
   - Filter/aggregate data as needed
   - Handle datetime parsing
   - Sort data appropriately
   - Limit to top N items if too many categories

5. **Error Handling:**
   - Check for empty data
   - Handle missing columns gracefully
   - Use try-except for data operations

STRICT RULES:
- Return ONLY executable Python code
- NO markdown code fences (```python)
- NO explanatory text before/after code
- Code must be complete and runnable
- Assume 'df' variable contains the data
- Do NOT include df loading code
- Do NOT include plt.show() or fig.show()

OUTPUT FORMAT:
Pure Python code only, no markdown, no explanations.
"""


# =========================
# Code Generation Functions
# =========================

def generate_chart_code(
    dataset: ChartDataset,
    user_request: str,
    client: OpenAI,
    model: str = "gpt-4o-mini",
    temperature: float = 0.1,
    preferred_library: str = "auto"
) -> dict[str, Any]:
    """Generate Python code for chart creation.
    
    Args:
        dataset: ChartDataset instance with schema and sample data
        user_request: Natural language description of desired chart
        client: OpenAI client instance
        model: Model to use for code generation
        temperature: Sampling temperature
        preferred_library: "matplotlib", "seaborn", "plotly", or "auto"
        
    Returns:
        Dict with:
        - "code": Generated Python code
        - "library": Detected library ("matplotlib", "seaborn", or "plotly")
        - "chart_type": Inferred chart type
        - "reasoning": LLM's reasoning (if available)
    """
    # Get dataset context
    schema = dataset.get_schema_description()
    sample = dataset.get_sample_data(rows=5)
    
    # Build prompt
    library_hint = ""
    if preferred_library != "auto":
        library_hint = f"\nPREFERRED LIBRARY: Use {preferred_library} for this chart.\n"
    
    prompt = f"""{CHART_GENERATION_SPEC}

{library_hint}
DATASET SCHEMA:
{schema}

SAMPLE DATA (first 5 rows):
{sample}

USER REQUEST:
{user_request}

Generate the Python code now (code only, no markdown):
"""
    
    # Call LLM
    # response = client.chat.completions.create(
    #     model=model,
    #     messages=[
    #         {"role": "system", "content": "You are an expert data visualization specialist. Return ONLY executable Python code."},
    #         {"role": "user", "content": prompt}
    #     ],
    #     temperature=temperature,
    # )
    
    # code = response.choices[0].message.content.strip()

    # Call LLM (via unified helper so we support both Chat and Responses API models)
    code = call_llm_text(
        client=client,
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert data visualization specialist. "
                    "Return ONLY executable Python code."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )


    # Clean up code (remove markdown if LLM added it anyway)
    code = _clean_generated_code(code)
    
    # Detect library and chart type
    library = _detect_library(code, preferred_library)
    chart_type = _infer_chart_type(code)
    
    return {
        "code": code,
        "library": library,
        "chart_type": chart_type,
        "model": model,
    }


def generate_chart_code_with_reasoning(
    dataset: ChartDataset,
    user_request: str,
    client: OpenAI,
    model: str = "gpt-4o",
    temperature: float = 0.1,
    preferred_library: str = "auto"
) -> dict[str, Any]:
    """Generate chart code with explicit reasoning step.
    
    This uses a two-step process:
    1. LLM explains its approach
    2. LLM generates the code
    
    Useful for complex requests or debugging.
    
    Args:
        dataset: ChartDataset instance
        user_request: Natural language chart request
        client: OpenAI client
        model: Model to use (recommend gpt-4o for reasoning)
        temperature: Sampling temperature
        preferred_library: Library preference
        
    Returns:
        Dict with "code", "library", "chart_type", and "reasoning"
    """
    schema = dataset.get_schema_description()
    sample = dataset.get_sample_data(rows=5)
    
    # Step 1: Get reasoning
    reasoning_prompt = f"""Analyze this visualization request:

DATASET SCHEMA:
{schema}

SAMPLE DATA:
{sample}

USER REQUEST:
{user_request}

Explain your approach:
1. What chart type is most appropriate?
2. What data transformations are needed?
3. What library should be used?
4. What are the key visualization elements?

Provide a brief analysis (2-3 sentences):
"""
    
    reasoning_response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a data visualization expert."},
            {"role": "user", "content": reasoning_prompt}
        ],
        temperature=temperature,
    )
    
    reasoning = reasoning_response.choices[0].message.content.strip()
    
    # Step 2: Generate code with reasoning context
    result = generate_chart_code(
        dataset=dataset,
        user_request=f"{user_request}\n\nApproach: {reasoning}",
        client=client,
        model=model,
        temperature=temperature,
        preferred_library=preferred_library
    )
    
    result["reasoning"] = reasoning
    return result


# =========================
# Helper Functions
# =========================

def _clean_generated_code(code: str) -> str:
    """Remove markdown code fences and extra whitespace."""
    # Remove markdown code fences
    if code.startswith("```python"):
        code = code[len("```python"):].strip()
    elif code.startswith("```"):
        code = code[3:].strip()
    
    if code.endswith("```"):
        code = code[:-3].strip()
    
    # Remove any leading/trailing whitespace
    code = code.strip()
    
    return code


def _detect_library(code: str, preferred: str) -> str:
    """Detect which plotting library is used in the code."""
    if preferred != "auto":
        return preferred
    
    code_lower = code.lower()
    
    # Check for plotly
    if "plotly" in code_lower or "px." in code or "go." in code:
        return "plotly"
    
    # Check for seaborn
    if "seaborn" in code_lower or "sns." in code:
        return "seaborn"
    
    # Default to matplotlib
    return "matplotlib"


def _infer_chart_type(code: str) -> str:
    """Infer chart type from code."""
    code_lower = code.lower()
    
    # Check for common chart types
    if "scatter" in code_lower:
        return "scatter"
    elif "bar" in code_lower or "barh" in code_lower:
        return "bar"
    elif "line" in code_lower or "plot(" in code_lower:
        return "line"
    elif "hist" in code_lower:
        return "histogram"
    elif "box" in code_lower:
        return "box"
    elif "violin" in code_lower:
        return "violin"
    elif "heatmap" in code_lower:
        return "heatmap"
    elif "pie" in code_lower:
        return "pie"
    else:
        return "unknown"
