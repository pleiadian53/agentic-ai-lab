"""Prompt construction and LLM API calls for the chart reflection workflow."""

from __future__ import annotations

import json
from dataclasses import dataclass
import re
from typing import Tuple

from reflection.M2_UGL_1 import utils as legacy_utils
from .execution import ensure_tagged


@dataclass(slots=True)
class PromptContext:
    """Lightweight container of dataset metadata injected into prompts."""

    schema: str
    sample_rows_json: str


def build_generation_prompt(
    instruction: str,
    *,
    context: PromptContext,
    output_path: str,
) -> str:
    return f"""
You are a data visualization expert.

Dataset schema:
{context.schema}

Sample rows (JSON):
{context.sample_rows_json}

Return your answer strictly in this format:

1) First line: a valid JSON object with a \"description\" field explaining the chart.
   Example: {{"description": "Horizontal bar chart showing total sales by coffee type, sorted from highest to lowest."}}

2) After a newline, output ONLY the Python code wrapped in:
<execute_python>
# valid python code here
</execute_python>

Constraints:
1. Assume a pandas DataFrame named `df` is already available with the schema above.
2. Use matplotlib for plotting; you may also use pandas for data wrangling.
3. Add a clear title, axis labels, and legend when appropriate.
4. Save the chart to '{output_path}' with dpi=300.
5. Do not call plt.show().
6. Always call plt.close() once the file is saved.
7. Include all necessary import statements inside the code block.
8. Do NOT use deprecated matplotlib styles like 'seaborn-whitegrid'. Use built-in styles or manual styling.

User instruction: {instruction}
""".strip()


def generate_initial_code(
    *,
    instruction: str,
    model_name: str,
    output_path: str,
    prompt_context: PromptContext,
) -> Tuple[str, str]:
    """
    Generate initial chart code with description.
    
    Returns:
        Tuple of (description, code_with_tags)
    """
    prompt = build_generation_prompt(
        instruction,
        context=prompt_context,
        output_path=output_path,
    )
    content = legacy_utils.get_response(model_name, prompt)
    
    # Extract description from first line
    lines = content.strip().splitlines()
    json_line = lines[0].strip() if lines else ""
    
    try:
        desc_obj = json.loads(json_line)
        description = str(desc_obj.get("description", "")).strip()
    except Exception:
        # Fallback: try to find JSON in content
        fallback = re.search(r"\{.*?\}", content, flags=re.DOTALL)
        if fallback:
            try:
                desc_obj = json.loads(fallback.group(0))
                description = str(desc_obj.get("description", "Chart visualization")).strip()
            except Exception:
                description = "Chart visualization"
        else:
            description = "Chart visualization"
    
    # Extract code
    code_match = re.search(r"<execute_python>([\s\S]*?)</execute_python>", content)
    if code_match:
        code = ensure_tagged(code_match.group(1).strip())
    else:
        # Fallback: return content as-is
        code = ensure_tagged(content)
    
    return description, code


def build_reflection_prompt(
    *,
    instruction: str,
    original_code: str,
    context: PromptContext,
    output_path: str,
) -> str:
    """
    Construct an enhanced reflection prompt with structured critique framework.

    The prompt guides the LLM to systematically evaluate charts across five dimensions:
    1. Chart type appropriateness (matching data structure to visual encoding)
    2. Perceptual accuracy (truthful scales, aspect ratios, baselines)
    3. Clarity & readability (legible labels, accessible colors, legend placement)
    4. Data-ink ratio (Tufte's principle: maximize information, minimize clutter)
    5. Statistical integrity (error bars, outlier handling, aggregation clarity)

    This structured approach enables autonomous visual critique without requiring
    explicit user instructions about what to fix.
    """
    return f"""
You are an expert data visualization critic trained in perceptual psychology, information design, and best practices from Edward Tufte and Cleveland-McGill research.

Dataset schema:
{context.schema}

Sample rows (JSON):
{context.sample_rows_json}

CRITIQUE FRAMEWORK - Evaluate the attached chart systematically:

1. CHART TYPE APPROPRIATENESS
   - Does the chart type match the data structure and user intent?
   - Temporal data → line/area charts; Categorical comparisons → bar charts; Distributions → histograms/box plots
   - Are there better alternatives? (e.g., horizontal bars for long labels, heatmap for 2D categorical data)

2. PERCEPTUAL ACCURACY & TRUTHFULNESS
   - Are visual encodings honest? (bar charts should start at 0, avoid misleading scales)
   - Is the aspect ratio appropriate? (avoid compressing/stretching trends)
   - Are comparisons easy? (aligned baselines, consistent scales)

3. CLARITY & READABILITY
   - Are labels legible? (font size ≥10pt, no overlapping text, appropriate rotation)
   - Is the legend necessary and well-positioned? (remove if redundant, place outside plot area)
   - Are colors distinguishable and accessible? (avoid red-green for colorblind users)
   - Are axis labels and titles descriptive and properly formatted?

4. DATA-INK RATIO (Tufte's Principle)
   - Remove chart junk: unnecessary gridlines, 3D effects, decorative elements
   - Maximize information density while maintaining clarity
   - Use direct labeling instead of legends when possible

5. STATISTICAL INTEGRITY
   - Are error bars/confidence intervals shown when appropriate?
   - Are outliers handled properly? (annotated or explained)
   - Is aggregation method clear? (mean vs median, etc.)

Original instruction:
{instruction}

Original code for context:
{original_code}

OUTPUT FORMAT (STRICT):
1) First line: a valid JSON object with \"feedback\" and \"description\" fields.
   Example: {{"feedback": "Chart type is appropriate, but axis labels overlap.", "description": "Horizontal bar chart showing total sales by coffee type with improved label spacing."}}
2) After a newline, output ONLY the refined Python code wrapped in:
<execute_python>
...
</execute_python>
3) Include all required import statements within the code block.

Hard constraints:
- Use pandas and matplotlib only.
- Assume `df` already exists; do not reload data from disk.
- Save the figure to '{output_path}' with dpi=300.
- Always call plt.close() at the end (no plt.show()).
- Do NOT use deprecated matplotlib styles like 'seaborn-whitegrid'. Use built-in styles or manual styling.
- Apply your critique to generate measurably better visualization code.
""".strip()


def _call_multimodal_model(
    *,
    model_name: str,
    prompt: str,
    media_type: str,
    payload_b64: str,
) -> str:
    lower = model_name.lower()
    if "claude" in lower or "anthropic" in lower:
        return legacy_utils.image_anthropic_call(model_name, prompt, media_type, payload_b64)
    return legacy_utils.image_openai_call(model_name, prompt, media_type, payload_b64)


def reflect_on_chart(
    *,
    chart_path: str,
    instruction: str,
    model_name: str,
    output_path: str,
    original_code: str,
    prompt_context: PromptContext,
) -> Tuple[str, str, str]:
    """
    Return a tuple of (feedback, description, refined_code_with_tags).
    """
    media_type, payload = legacy_utils.encode_image_b64(chart_path)
    prompt = build_reflection_prompt(
        instruction=instruction,
        original_code=original_code,
        context=prompt_context,
        output_path=output_path,
    )
    content = _call_multimodal_model(
        model_name=model_name,
        prompt=prompt,
        media_type=media_type,
        payload_b64=payload,
    )

    lines = content.strip().splitlines()
    json_line = lines[0].strip() if lines else ""

    try:
        response_obj = json.loads(json_line)
    except Exception as error:
        fallback = re.search(r"\{.*?\}", content, flags=re.DOTALL)
        if fallback:
            try:
                response_obj = json.loads(fallback.group(0))
            except Exception as nested_error:
                response_obj = {
                    "feedback": f"Failed to parse JSON: {nested_error!s}",
                    "description": "Chart visualization"
                }
        else:
            response_obj = {
                "feedback": f"Failed to find JSON: {error!s}",
                "description": "Chart visualization"
            }

    feedback = str(response_obj.get("feedback", "")).strip()
    description = str(response_obj.get("description", "Chart visualization")).strip()

    refined_code_body = ""
    match = re.search(r"<execute_python>([\s\S]*?)</execute_python>", content)
    if match:
        refined_code_body = match.group(1).strip()

    refined_code = ensure_tagged(refined_code_body)
    return feedback, description, refined_code
