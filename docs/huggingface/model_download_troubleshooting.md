# HuggingFace Model Download Troubleshooting

When using `sentence-transformers`, `transformers`, or `huggingface_hub` to download
models, the Python downloader can occasionally hang — especially on large files like
`model.safetensors`. This guide documents the issue and a reliable workaround.

## Symptoms

- Progress bar stuck at **0%** for `model.safetensors` (or any large blob)
- Download speed shows `?B/s`
- No error raised — the process simply hangs indefinitely
- Smaller files (config, tokenizer) download fine

This has been observed with `BAAI/bge-base-en-v1.5` (~438 MB) but can affect any
model download.

## Root Cause

The `huggingface_hub` Python downloader uses `requests` with chunked streaming. On
some networks/configurations, the connection stalls on large files while `curl`
(which uses `libcurl`) handles the same download without issues.

## Workaround: Download via `curl` and Place in HF Cache

### Step 1 — Identify the model and file

```bash
# Example: BAAI/bge-base-en-v1.5, file: model.safetensors
MODEL_ID="BAAI/bge-base-en-v1.5"
FILENAME="model.safetensors"
```

### Step 2 — Download with `curl`

```bash
curl -L --progress-bar \
  -o /tmp/${FILENAME} \
  "https://huggingface.co/${MODEL_ID}/resolve/main/${FILENAME}"
```

This typically completes in seconds (e.g., 438 MB at ~40 MB/s).

### Step 3 — Compute the SHA256 hash

HuggingFace uses content-addressed storage. The blob filename is the file's SHA256:

```bash
shasum -a 256 /tmp/${FILENAME}
# Output: c7c1988aae201f80cf91a5dbbd5866409503b89dcaba877ca6dba7dd0a5167d7  /tmp/model.safetensors
```

### Step 4 — Place the blob in the HF cache

The cache structure is:

```text
~/.cache/huggingface/hub/
└── models--BAAI--bge-base-en-v1.5/
    ├── blobs/
    │   ├── <sha256_hash>          ← raw file content
    │   └── <sha256_hash>.incomplete  ← delete if present
    ├── refs/
    │   └── main                   ← contains the commit hash
    └── snapshots/
        └── <commit_hash>/
            ├── config.json → ../../blobs/<hash>
            ├── model.safetensors → ../../blobs/<hash>   ← symlink to blob
            └── ...
```

Copy the downloaded file into the blobs directory:

```bash
# Derive the cache path
CACHE_DIR=~/.cache/huggingface/hub
MODEL_CACHE="${CACHE_DIR}/models--$(echo ${MODEL_ID} | tr '/' '--')"
SHA256="<paste_sha256_from_step_3>"

# Remove any stale .incomplete marker
rm -f "${MODEL_CACHE}/blobs/${SHA256}.incomplete"

# Copy the blob
cp /tmp/${FILENAME} "${MODEL_CACHE}/blobs/${SHA256}"
```

### Step 5 — Create the snapshot symlink

Find the commit hash (stored in `refs/main`):

```bash
COMMIT=$(cat "${MODEL_CACHE}/refs/main")
echo "Commit: ${COMMIT}"
```

Create the symlink:

```bash
ln -s "../../blobs/${SHA256}" "${MODEL_CACHE}/snapshots/${COMMIT}/${FILENAME}"
```

### Step 6 — Verify

```bash
mamba run -n agentic-ai python -c "
from sentence_transformers import SentenceTransformer
m = SentenceTransformer('${MODEL_ID}')
print('Model loaded successfully')
"
```

### Step 7 — Clean up

```bash
rm /tmp/${FILENAME}
```

## Prevention

- **Set `HF_TOKEN`** in your `.env` file for authenticated downloads (higher rate
  limits). Get a token from <https://huggingface.co/settings/tokens> (Read access is
  sufficient).

  ```bash
  HF_TOKEN=hf_your-token-here
  ```

- **Pre-download models from terminal** before running notebooks, where you can
  monitor progress and retry more easily:

  ```bash
  mamba run -n agentic-ai python -c "
  from sentence_transformers import SentenceTransformer
  SentenceTransformer('BAAI/bge-base-en-v1.5')
  "
  ```

## Cache Inspection

Use the project's HuggingFace cache monitor to check what's downloaded:

```bash
# Full report
mamba run -n agentic-ai python rag/utils/huggingface.py

# Detailed (file counts, revisions, dates)
mamba run -n agentic-ai python rag/utils/huggingface.py --detail

# One-liner summary
mamba run -n agentic-ai python rag/utils/huggingface.py --summary
```

Or programmatically:

```python
from rag.utils.huggingface import cache_report, cache_summary
print(cache_summary())
print(cache_report(detail=True))
```

## HuggingFace Cache Location

| Environment Variable      | Default                            | Purpose                    |
|---------------------------|------------------------------------|----------------------------|
| `HF_HOME`                 | `~/.cache/huggingface`             | HF root directory          |
| `HUGGINGFACE_HUB_CACHE`   | `~/.cache/huggingface/hub`         | Model/dataset blob storage |

To redirect the cache (must be set **before** importing HF libraries):

```python
from rag.utils.huggingface import configure_cache
configure_cache("/path/to/custom/cache")
```

Or via environment variable:

```bash
export HF_HOME=/path/to/custom/cache
```

## Related

- `rag/utils/huggingface.py` — Cache monitor and environment configuration utility
- `.env.example` — Template showing `HF_TOKEN` configuration
- `notebooks/RAG/C1M3/utils.py` — Example of `SentenceTransformer` usage with
  fallback for missing `MODEL_PATH`
