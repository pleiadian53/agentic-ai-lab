import re
import json

def clean_json_block(raw: str) -> str:
    """
    Clean the contents of a JSON block that may come wrapped with Markdown backticks.
    """
    raw = raw.strip()
    # Quitar bloque tipo ```json ... ```
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
    return raw.strip()

def is_responses_model(model: str) -> bool:
    """Check if model requires OpenAI Responses API (e.g. gpt-5.1)."""
    return "gpt-5" in model or "codex" in model

def normalize_model_name(model: str) -> tuple[str, str]:
    """
    Normalize model string to (aisuite_name, openai_name).
    Example: "openai:gpt-4o" -> ("openai:gpt-4o", "gpt-4o")
    """
    if model.startswith("openai:"):
        return model, model.split(":", 1)[1]
    return f"openai:{model}", model
