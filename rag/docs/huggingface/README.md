# HuggingFace — RAG Sub-project Notes

This sub-project uses HuggingFace models extensively for embeddings and retrieval.

## Project-Level Documentation

For comprehensive HuggingFace guides (cache management, download troubleshooting,
environment configuration), see the **project-level docs**:

- [Model Download Troubleshooting](../../../docs/huggingface/model_download_troubleshooting.md)
  — Fixing hung downloads, `curl` workaround, cache structure explained

## RAG-Specific Utilities

- [`rag/utils/huggingface.py`](../../utils/huggingface.py) — Cache monitor and
  environment configuration module

  ```bash
  # Check what's cached and disk usage
  mamba run -n agentic-ai python rag/utils/huggingface.py --detail
  ```

## Models Used in RAG Notebooks

| Model | Size | Used In | Purpose |
|-------|------|---------|---------|
| `BAAI/bge-base-en-v1.5` | ~438 MB | C1M3 (Assignment) | Document embeddings for retrieval |
| `sentence-transformers/all-MiniLM-L6-v2` | ~92 MB | C1M2 | Embedding visualizations |
