# Troubleshooting Guide: C1M4_Ungraded_Lab_2.ipynb (Prompt Engineering)

## Summary

One bug found in `utils.py`: the Together SDK response `role` field changed from an Enum
to a plain string in a newer SDK version. The code called `.name.lower()` on it unconditionally,
which raises `AttributeError: 'str' object has no attribute 'name'`. Fixed with a `hasattr` guard.
All 13 test steps pass after the fix.

---

## Error 1: `'str' object has no attribute 'name'` in `utils.py`

### Symptom

```
AttributeError: 'str' object has no attribute 'name'
  File "utils.py", line 103, in generate_with_single_input
    json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
  File "utils.py", line 154, in generate_with_multiple_input
    json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
```

Every LLM call in the notebook raises this error — classification, parameter-setting, JSON output,
and structured output all fail.

### Location

- **File**: `utils.py`
- **Lines**: 103 (`generate_with_single_input`) and 154 (`generate_with_multiple_input`)

### Root Cause

The Together Python SDK used to return the `role` field in the chat completion response
as an Enum object (e.g., `ChoiceMessageRole.ASSISTANT`), so calling `.name.lower()` yielded
the string `"assistant"`. In the current SDK version, `role` is returned as a plain string
already (e.g., `"assistant"`), so `.name` fails with `AttributeError`.

### Solution

**Before (Incorrect):**
```python
json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
```

**After (Correct):**
```python
role_val = json_dict['choices'][-1]['message']['role']
json_dict['choices'][-1]['message']['role'] = role_val.name.lower() if hasattr(role_val, 'name') else role_val
```

Apply this in **both** `generate_with_single_input` (line ~103) and `generate_with_multiple_input` (line ~154).

### Reference

- Together AI Python SDK changelog: https://docs.together.ai/changelog
- Root cause category: **SDK version drift** — API return types changed between SDK releases

---

## Quick Fix Summary

- `utils.py` line ~103: Replace `.name.lower()` call with `hasattr` guard in `generate_with_single_input`
- `utils.py` line ~154: Same fix in `generate_with_multiple_input`

## End-to-End Test

```bash
source ~/miniforge3-new/etc/profile.d/conda.sh
conda activate agentic-ai
python test_C1M4_Lab2_e2e.py
```

Expected output: `ALL STEPS PASSED ✓`

---

**Document created**: 2026-02-20  
**Last tested with**: `together` SDK (current in `agentic-ai` conda env), `pydantic>=2.0`  
**Model**: `meta-llama/Llama-3.2-3B-Instruct-Turbo`

---

## Prompt Engineering Patterns (new reference for `reference_LLM_text_gen.md`)

Patterns specific to LLM text generation / prompt engineering notebooks:

| Pattern | What to watch for |
|---|---|
| SDK role field type | Together SDK may return `role` as Enum or str depending on version — always use `hasattr(role_val, 'name')` guard |
| `response_format={"type": "json_schema", ...}` | Together SDK supports this for structured output; pass as `**kwargs` to `generate_with_multiple_input` |
| `pydantic.BaseModel.model_json_schema()` | Requires Pydantic v2; `schema()` is the v1 equivalent |
| `max_tokens=2` for classifier calls | Very small token budget; LLM must produce exactly one word — prompt must be precise |
