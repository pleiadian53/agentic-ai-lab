# Troubleshooting Guide: C1M2_Ungraded_Lab_2.ipynb (Retrieval Metrics)

## Summary

Two issues found:

1. **Cell 9 — `KeyError: 'MODELS'`**: The notebook hard-requires a `MODELS` environment
   variable pointing to a local model directory. This variable is not set in the local
   `.env` file. Fixed with a conditional fallback to the HuggingFace cache (the model
   `BAAI/bge-base-en-v1.5` is already cached at `~/.cache/huggingface/hub/`).

2. **Torch binary incompatibility with `conda activate`**: Importing `sentence_transformers`
   (which pulls in `torch`) fails when the environment is loaded via `conda activate` in a
   shell. Running via `conda run -n agentic-ai` works correctly. This is a PyTorch binary
   vs. Python version mismatch in the active shell environment.

All 13 test steps pass after the Cell 9 fix, using `conda run`.

---

## Error 1: `KeyError: 'MODELS'` in Cell 9

### Symptom

```
KeyError: 'MODELS'
  File "...", line 3, in <module>
    model = SentenceTransformer(os.path.join(os.environ['MODELS'], model_name))
```

The notebook fails immediately at model loading. All subsequent cells that use `model`
or `embedding_vectors` are blocked.

### Location

- **File**: `C1M2_Ungraded_Lab_2.ipynb`
- **Cell**: Cell 9

### Root Cause

The notebook was authored for a course Docker environment where `MODELS` was an environment
variable pointing to a directory of pre-downloaded models. In a local development setup, this
variable is not defined and `os.environ['MODELS']` raises `KeyError`.

The model `BAAI/bge-base-en-v1.5` is available locally at:
`~/.cache/huggingface/hub/models--BAAI--bge-base-en-v1.5`

`SentenceTransformer` resolves this cache automatically when given just the model name.

### Solution

**Before (Incorrect):**
```python
model = SentenceTransformer(os.path.join(os.environ['MODELS'], model_name))
```

**After (Correct):**
```python
if 'MODELS' in os.environ:
    model = SentenceTransformer(os.path.join(os.environ['MODELS'], model_name))
else:
    model = SentenceTransformer(model_name)
```

### Reference

- HuggingFace cache: `~/.cache/huggingface/hub/models--BAAI--bge-base-en-v1.5`
- `SentenceTransformer` automatically resolves model names via the HF hub cache

---

## Error 2: Torch binary incompatibility with `conda activate`

### Symptom

```
ImportError: dlopen(...torch/_C.cpython-311-darwin.so, 0x0002):
  symbol not found in flat namespace '_PyDict_AddWatcher'
```

Occurs when running `conda activate agentic-ai && python ...`.

### Location

- **Environment**: `agentic-ai` conda env
- **Trigger**: Any import of `sentence_transformers` (which imports `torch`)

### Root Cause

`_PyDict_AddWatcher` is a CPython internal symbol introduced in Python 3.12. The `torch`
binary installed in the `agentic-ai` env (v2.10.0) was compiled against Python 3.12, but
`conda activate` in the current shell resolves to a Python 3.11 runtime, causing a
symbol-not-found failure at `.so` load time.

`conda run -n agentic-ai` uses an isolated subprocess with the correct environment,
bypassing the shell-level Python version mismatch.

### Solution

Run the test script and notebook kernel via `conda run`, not `conda activate`:

**Instead of:**
```bash
source ~/miniforge3-new/etc/profile.d/conda.sh
conda activate agentic-ai
python test_C1M2_Lab2_e2e.py
```

**Use:**
```bash
source ~/miniforge3-new/etc/profile.d/conda.sh
conda run -n agentic-ai python test_C1M2_Lab2_e2e.py
```

For Jupyter, launch the kernel directly:
```bash
conda run -n agentic-ai jupyter lab
```

---

## Quick Fix Summary

- **Cell 9 (`C1M2_Ungraded_Lab_2.ipynb`)**: Wrap model load in `if 'MODELS' in os.environ` guard
- **Execution**: Always use `conda run -n agentic-ai` for this notebook, not `conda activate`

## End-to-End Test

```bash
source ~/miniforge3-new/etc/profile.d/conda.sh
conda run -n agentic-ai python test_C1M2_Lab2_e2e.py
```

Expected: `ALL STEPS PASSED ✓`

---

**Document created**: 2026-02-20  
**Last tested with**: `sentence-transformers` (agentic-ai env), `BAAI/bge-base-en-v1.5`,
`sklearn` 20 Newsgroups dataset  
**Avg Precision@5**: 0.92 · **Avg Recall@5**: 0.0078
