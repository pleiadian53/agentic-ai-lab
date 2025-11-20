"""Unified LLM client helpers for chat + responses API.

This module provides thin wrappers so the rest of the chart_agent code
can call a single helper function and transparently work with either:

- Chat Completions API models (gpt-4o, gpt-4o-mini, gpt-4.1, etc.)
- Responses API–only models (gpt-5.x, gpt-5.1-codex-mini, etc.)

Usage
-----
from .llm_client import call_llm_text, call_llm_json

text = call_llm_text(client, model, messages=[...])
obj  = call_llm_json(client, model, messages=[...])
"""

from __future__ import annotations

from typing import Any, Dict, List
import json

from openai import OpenAI


# ---- Model routing --------------------------------------------------------


def _uses_responses_api(model: str) -> bool:
    """Return True if the model should be called via the Responses API.

    Heuristic:
    - All gpt-5* models
    - Codex mini variants that are responses-only
    - Image models (for completeness, though we don't use them here)

    This is intentionally conservative: chat-compatible models like gpt-4o
    will still go through the chat.completions endpoint.
    """
    if not model:
        return False

    model = model.lower()
    if model.startswith("gpt-5"):
        return True
    if "codex-mini" in model:
        return True
    if model.startswith("gpt-image-"):
        return True

    return False


def _flatten_messages_to_prompt(messages: List[Dict[str, str]]) -> str:
    """Convert a chat-style messages list into a single prompt string.

    This is used when talking to Responses-only models. It preserves roles
    in a lightweight way while avoiding the more verbose messages format.
    """
    parts: List[str] = []
    for m in messages:
        role = m.get("role", "user").upper()
        content = m.get("content", "")
        parts.append(f"{role}: {content}")
    return "\n\n".join(parts)


# ---- Public helpers -------------------------------------------------------


def call_llm_text(
    client: OpenAI,
    model: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
) -> str:
    """Call an LLM and return plain text output.

    This hides whether the underlying model is chat- or responses-based.
    """
    if _uses_responses_api(model):
        prompt = _flatten_messages_to_prompt(messages)
        # Try with temperature first, fall back without it if unsupported
        try:
            response = client.responses.create(
                model=model,
                input=prompt,
                temperature=temperature,
            )
        except Exception as e:
            if "temperature" in str(e).lower() and "not supported" in str(e).lower():
                # Retry without temperature
                response = client.responses.create(
                    model=model,
                    input=prompt,
                )
            else:
                raise
        
        # New Responses API exposes a convenience property `output_text`
        text = getattr(response, "output_text", None)
        if text is None:
            # Fallback: try to dig into the first output item
            try:
                text = response.output[0].content[0].text
            except Exception:
                text = str(response)
        return text.strip()

    # Default: chat.completions
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def call_llm_json(
    client: OpenAI,
    model: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.0,
) -> Dict[str, Any]:
    """Call an LLM that is instructed to return a JSON object.

    For chat-compatible models we use response_format='json_object'.
    For responses-only models we still rely on the model to emit JSON
    (optionally with response_format when supported) and then parse it.
    """
    raw_text: str

    if _uses_responses_api(model):
        prompt = _flatten_messages_to_prompt(messages)
        # Try with response_format and temperature first; fall back if not supported.
        try:
            response = client.responses.create(
                model=model,
                input=prompt,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            text = getattr(response, "output_text", None)
            if text is None:
                text = response.output[0].content[0].text
            raw_text = text
        except Exception as e:
            error_str = str(e).lower()
            # Try without temperature if that's the issue
            if "temperature" in error_str and "not supported" in error_str:
                try:
                    response = client.responses.create(
                        model=model,
                        input=prompt,
                        response_format={"type": "json_object"},
                    )
                    text = getattr(response, "output_text", None)
                    if text is None:
                        text = response.output[0].content[0].text
                    raw_text = text
                except Exception:
                    # Fallback: no response_format or temperature support
                    response = client.responses.create(
                        model=model,
                        input=prompt,
                    )
                    text = getattr(response, "output_text", None)
                    if text is None:
                        text = response.output[0].content[0].text
                    raw_text = text
            else:
                # Try without response_format
                try:
                    response = client.responses.create(
                        model=model,
                        input=prompt,
                        temperature=temperature,
                    )
                    text = getattr(response, "output_text", None)
                    if text is None:
                        text = response.output[0].content[0].text
                    raw_text = text
                except Exception:
                    # Last fallback: minimal parameters
                    response = client.responses.create(
                        model=model,
                        input=prompt,
                    )
                    text = getattr(response, "output_text", None)
                    if text is None:
                        text = response.output[0].content[0].text
                    raw_text = text
    else:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        raw_text = response.choices[0].message.content

    raw_text = raw_text.strip()

    # Robust JSON parsing: try direct, then strip code fences if present.
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Handle ```json ... ``` wrappers
        if raw_text.startswith("```"):
            stripped = raw_text.strip("`")
            # Remove optional leading 'json'
            if stripped.lower().startswith("json"):
                stripped = stripped[4:]
            try:
                return json.loads(stripped.strip())
            except json.JSONDecodeError:
                pass

        # Last resort: try to locate the first {...} block
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start != -1 and end != -1 and end > start:
            snippet = raw_text[start : end + 1]
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                pass

        raise
