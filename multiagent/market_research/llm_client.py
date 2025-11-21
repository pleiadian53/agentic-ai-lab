"""Unified LLM client helpers for chat + responses API.

This module provides wrappers to transparently work with either:
- Chat Completions API models (gpt-4o, gpt-4o-mini, gpt-4.1, etc.)
- Responses API-only models (gpt-5.x, gpt-5.1-codex-mini, etc.)

Adapted from chart_agent/llm_client.py for market_research package.

Usage:
    from .llm_client import call_llm_text, call_llm_json
    
    # Works with both chat and responses API models
    text = call_llm_text(client, model, messages=[...])
    obj = call_llm_json(client, model, messages=[...])
"""

from __future__ import annotations

import json
from typing import Any

import aisuite


# Model Routing

def _uses_responses_api(model: str) -> bool:
    """Return True if the model should be called via the Responses API.
    
    Heuristic:
    - All gpt-5* models
    - Codex mini variants that are responses-only
    - Image models (for completeness)
    
    Args:
        model: Model identifier (e.g., "openai:gpt-5.1")
        
    Returns:
        True if model requires responses API
    """
    if not model:
        return False

    # Strip provider prefix if present (e.g., "openai:gpt-5.1" -> "gpt-5.1")
    model_name = model.split(":")[-1].lower()
    
    if model_name.startswith("gpt-5"):
        return True
    if "codex-mini" in model_name:
        return True
    if model_name.startswith("gpt-image-"):
        return True

    return False


def _flatten_messages_to_prompt(messages: list[dict[str, Any]]) -> str:
    """Convert chat-style messages list into a single prompt string.
    
    Used when talking to Responses-only models. Preserves roles
    in a lightweight way.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        
    Returns:
        Flattened prompt string
    """
    parts: list[str] = []
    for m in messages:
        role = m.get("role", "user").upper()
        content = m.get("content", "")
        
        # Handle multimodal content (list of content items)
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            content = "\n".join(text_parts)
        
        parts.append(f"{role}: {content}")
    
    return "\n\n".join(parts)


# Public Helpers

def _detect_model_provider(model_name: str) -> str | None:
    """Detect which provider a model belongs to based on naming conventions.
    
    Args:
        model_name: Model name without provider prefix
        
    Returns:
        Provider name ("openai", "anthropic", etc.) or None if unknown
    """
    model_lower = model_name.lower()
    
    # OpenAI models
    if any(model_lower.startswith(prefix) for prefix in [
        "gpt-", "o1-", "o3-", "text-", "davinci", "curie", "babbage", "ada",
        "dall-e", "whisper", "tts", "chatgpt"
    ]):
        return "openai"
    
    # Anthropic models
    if any(model_lower.startswith(prefix) for prefix in [
        "claude-", "claude"
    ]):
        return "anthropic"
    
    # Google models
    if any(model_lower.startswith(prefix) for prefix in [
        "gemini-", "palm-", "bard"
    ]):
        return "google"
    
    # Cohere models
    if any(model_lower.startswith(prefix) for prefix in [
        "command-", "embed-"
    ]):
        return "cohere"
    
    # Mistral models
    if any(model_lower.startswith(prefix) for prefix in [
        "mistral-", "mixtral-", "codestral-"
    ]):
        return "mistral"
    
    # Default to OpenAI for backward compatibility
    return "openai"


def _normalize_model_name(model: str) -> tuple[str, str]:
    """Normalize model name to (aisuite_format, provider_model_format).
    
    Accepts formats:
    - "gpt-5.1" → ("openai:gpt-5.1", "gpt-5.1")
    - "openai:gpt-5.1" → ("openai:gpt-5.1", "gpt-5.1")
    - "claude-3-opus" → ("anthropic:claude-3-opus", "claude-3-opus")
    
    Args:
        model: Model name with or without provider prefix
        
    Returns:
        Tuple of (aisuite_format, model_name_only)
        e.g., ("openai:gpt-5.1", "gpt-5.1")
    """
    if ":" in model:
        # Already has provider prefix
        provider, model_name = model.split(":", 1)
        return model, model_name
    else:
        # Detect provider from model name
        provider = _detect_model_provider(model)
        if provider:
            return f"{provider}:{model}", model
        else:
            # Fallback: assume OpenAI
            return f"openai:{model}", model


def call_llm_text(
    client: aisuite.Client,
    model: str,
    messages: list[dict[str, Any]],
    temperature: float = 0.2,
) -> str:
    """Call an LLM and return plain text output.
    
    Automatically routes to chat or responses API based on model.
    
    Args:
        client: aisuite Client instance
        model: Model identifier (e.g., "gpt-5.1" or "openai:gpt-5.1")
        messages: List of message dicts
        temperature: Sampling temperature
        
    Returns:
        Text response from model
    """
    # Normalize model name
    aisuite_model, openai_model = _normalize_model_name(model)
    
    # For aisuite, we need to extract the actual OpenAI client
    # and handle responses API directly
    if _uses_responses_api(openai_model):
        # Get OpenAI client from aisuite
        import openai
        openai_client = openai.OpenAI()
        
        prompt = _flatten_messages_to_prompt(messages)
        
        # Try with temperature first, fall back without it if unsupported
        try:
            response = openai_client.responses.create(
                model=openai_model,
                input=prompt,
                temperature=temperature,
            )
        except Exception as e:
            if "temperature" in str(e).lower() and "not supported" in str(e).lower():
                # Retry without temperature
                response = openai_client.responses.create(
                    model=openai_model,
                    input=prompt,
                )
            else:
                raise
        
        # Extract text from response
        text = getattr(response, "output_text", None)
        if text is None:
            try:
                text = response.output[0].content[0].text
            except Exception:
                text = str(response)
        return text.strip()

    # Default: use aisuite's chat.completions (works for chat API models)
    response = client.chat.completions.create(
        model=aisuite_model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def call_llm_json(
    client: aisuite.Client,
    model: str,
    messages: list[dict[str, Any]],
    temperature: float = 0.0,
) -> dict[str, Any]:
    """Call an LLM that is instructed to return a JSON object.
    
    For chat-compatible models uses response_format='json_object'.
    For responses-only models relies on the model to emit JSON.
    
    Args:
        client: aisuite Client instance
        model: Model identifier (e.g., "gpt-5.1" or "openai:gpt-5.1")
        messages: List of message dicts
        temperature: Sampling temperature
        
    Returns:
        Parsed JSON object
    """
    # Normalize model name
    aisuite_model, openai_model = _normalize_model_name(model)
    
    raw_text: str

    if _uses_responses_api(openai_model):
        # Get OpenAI client from aisuite
        import openai
        openai_client = openai.OpenAI()
        
        prompt = _flatten_messages_to_prompt(messages)
        
        # Try with response_format and temperature first
        try:
            response = openai_client.responses.create(
                model=openai_model,
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
                    response = openai_client.responses.create(
                        model=openai_model,
                        input=prompt,
                        response_format={"type": "json_object"},
                    )
                    text = getattr(response, "output_text", None)
                    if text is None:
                        text = response.output[0].content[0].text
                    raw_text = text
                except Exception:
                    # Fallback: no response_format or temperature support
                    response = openai_client.responses.create(
                        model=openai_model,
                        input=prompt,
                    )
                    text = getattr(response, "output_text", None)
                    if text is None:
                        text = response.output[0].content[0].text
                    raw_text = text
            else:
                # Try without response_format
                try:
                    response = openai_client.responses.create(
                        model=openai_model,
                        input=prompt,
                        temperature=temperature,
                    )
                    text = getattr(response, "output_text", None)
                    if text is None:
                        text = response.output[0].content[0].text
                    raw_text = text
                except Exception:
                    # Last fallback: minimal parameters
                    response = openai_client.responses.create(
                        model=openai_model,
                        input=prompt,
                    )
                    text = getattr(response, "output_text", None)
                    if text is None:
                        text = response.output[0].content[0].text
                    raw_text = text
    else:
        # Use aisuite for chat API models
        response = client.chat.completions.create(
            model=aisuite_model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        raw_text = response.choices[0].message.content

    raw_text = raw_text.strip()

    # Robust JSON parsing: try direct, then strip code fences if present
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
