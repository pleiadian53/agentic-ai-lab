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

<execute_python>
# valid python code here
</execute_python>

Do not add explanations, only the tags and the code.

Constraints:
1. Assume a pandas DataFrame named `df` is already available with the schema above.
2. Use matplotlib for plotting; you may also use pandas for data wrangling.
3. Add a clear title, axis labels, and legend when appropriate.
4. Save the chart to '{output_path}' with dpi=300.
5. Do not call plt.show().
6. Always call plt.close() once the file is saved.
7. Include all necessary import statements inside the code block.

User instruction: {instruction}
""".strip()


def generate_initial_code(
    *,
    instruction: str,
    model_name: str,
    output_path: str,
    prompt_context: PromptContext,
) -> str:
    prompt = build_generation_prompt(
        instruction,
        context=prompt_context,
        output_path=output_path,
    )
    return legacy_utils.get_response(model_name, prompt)


def build_reflection_prompt(
    *,
    instruction: str,
    original_code: str,
    context: PromptContext,
    output_path: str,
) -> str:
    return f"""
You are a data visualization expert.

Dataset schema:
{context.schema}

Sample rows (JSON):
{context.sample_rows_json}

Your task: critique the attached chart image and the original code against the
instruction below, then return improved matplotlib code.

Original instruction:
{instruction}

Original code for context:
{original_code}

OUTPUT FORMAT (STRICT):
1) First line: a valid JSON object with ONLY the \"feedback\" field.
   Example: {{"feedback": "The legend is unclear and the axis labels overlap."}}
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
) -> Tuple[str, str]:
    """
    Return a tuple of (feedback, refined_code_with_tags).
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
        feedback_obj = json.loads(json_line)
    except Exception as error:
        fallback = re.search(r"\{.*?\}", content, flags=re.DOTALL)
        if fallback:
            try:
                feedback_obj = json.loads(fallback.group(0))
            except Exception as nested_error:
                feedback_obj = {"feedback": f"Failed to parse JSON: {nested_error!s}"}
        else:
            feedback_obj = {"feedback": f"Failed to find JSON: {error!s}"}

    feedback = str(feedback_obj.get("feedback", "")).strip()

    refined_code_body = ""
    match = re.search(r"<execute_python>([\s\S]*?)</execute_python>", content)
    if match:
        refined_code_body = match.group(1).strip()

    refined_code = ensure_tagged(refined_code_body)
    return feedback, refined_code
