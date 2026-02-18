# Troubleshooting Guide: C1M3_Ungraded_Lab_1.ipynb

This document describes the errors encountered when running the Weaviate vector database notebook and their solutions.

## Summary

The notebook had two major issues that prevented it from running successfully:

1. **Reranker Configuration Error**: Incorrect parameter passed to `Configure.Reranker.transformers()`
2. **Flask Content-Type Error**: Flask endpoints not handling Weaviate's requests without `Content-Type: application/json` header

Both issues have been fixed in the updated `flask_app.py`.

---

## Error 1: Reranker Configuration

### Symptom

```
TypeError: _Reranker.transformers() got an unexpected keyword argument 'inference_url'
```

### Location

- **Notebook Cell 17**: Collection creation
- **Code**: 
  ```python
  reranker_config=Configure.Reranker.transformers(
      inference_url="http://127.0.0.1:5000"
  )
  ```

### Root Cause

The `Configure.Reranker.transformers()` method does not accept an `inference_url` parameter. The reranker inference URL is configured at the **Weaviate client level** via environment variables, not at the collection level.

### Solution

Remove the `inference_url` parameter from the reranker configuration:

**Before (Incorrect):**
```python
reranker_config=Configure.Reranker.transformers(
    inference_url="http://127.0.0.1:5000"
)
```

**After (Correct):**
```python
reranker_config=Configure.Reranker.transformers()
```

### How It Works

When creating the embedded Weaviate client (Cell 8), the `RERANKER_INFERENCE_API` environment variable is set:

```python
client = weaviate.connect_to_embedded(
    persistence_data_path="./.collections",
    environment_variables={
        "ENABLE_API_BASED_MODULES": "true",
        "ENABLE_MODULES": 'text2vec-transformers, reranker-transformers',
        "TRANSFORMERS_INFERENCE_API": "http://127.0.0.1:5000/",
        "RERANKER_INFERENCE_API": "http://127.0.0.1:5000/"  # ← Used here
    }
)
```

The reranker module automatically uses the URL specified in `RERANKER_INFERENCE_API` for all reranking operations.

### Reference

- [Weaviate Reranker Documentation](https://docs.weaviate.io/weaviate/model-providers/transformers/reranker)

---

## Error 2: Flask Content-Type Handling

### Symptom

```
Query call with protocol GRPC search failed with message ... 
415 Unsupported Media Type: Did not attempt to load JSON data 
because the request Content-Type was not 'application/json'.
```

This error occurred during:
- Cell 42: Semantic search (`near_text`)
- Cell 45: Semantic search with filter
- Cell 48: Semantic search with `contains_any` filter
- Cell 54: Hybrid search
- Cell 57: Reranking

### Location

- **File**: `flask_app.py`
- **Endpoints**: `/vectors` and `/rerank`

### Root Cause

Weaviate's `text2vec-transformers` module sends HTTP requests to the Flask inference API, but these requests may not include the `Content-Type: application/json` header (or may use a different content type).

Flask's `request.json` property **requires** the Content-Type header to be set to `application/json`. If it's missing or different, Flask raises a `415 Unsupported Media Type` error **before** the Python exception handling code can catch it.

### Solution

Use `request.get_json(force=True)` instead of `request.json`. The `force=True` parameter tells Flask to parse the request body as JSON **regardless** of the Content-Type header.

**Before (Incorrect):**
```python
@app.route('/vectors', methods=['POST'])
def vectorize():
    try:
        data = request.json  # ← Fails if Content-Type is not application/json
        if data is None:
            data = json.loads(request.data.decode("utf-8"))
        # ...
```

**After (Correct):**
```python
@app.route('/vectors', methods=['POST'])
def vectorize():
    try:
        data = request.get_json(force=True)  # ← Parses JSON regardless of Content-Type
        if data is None:
            data = json.loads(request.data.decode("utf-8"))
        # ...
```

The same fix was applied to the `/rerank` endpoint.

### Technical Details

Flask's `request.json` behavior:
- Checks the `Content-Type` header
- If it's not `application/json` (or a variant like `application/*+json`), returns `None`
- If you try to access it when it's `None`, Flask raises a 415 error

Flask's `request.get_json(force=True)` behavior:
- **Ignores** the `Content-Type` header
- Always attempts to parse the request body as JSON
- Returns the parsed JSON data or `None` if parsing fails
- Does **not** raise a 415 error

### Why This Matters

Vector databases and ML inference services often use custom protocols or simplified HTTP clients that may not set all standard headers. By using `force=True`, we make our Flask API more robust and compatible with Weaviate's inference module expectations.

### Reference

- [Flask Request.get_json() documentation](https://flask.palletsprojects.com/en/2.3.x/api/#flask.Request.get_json)

---

## Error 3: Port Configuration

### Symptom

Not an error, but a configuration inconsistency:

- Original `flask_app_v0.py` uses **port 5000**
- Modified `flask_app.py` uses **port 9500**
- Notebook Cell 8 references **port 5000** in comments and environment variables

### Location

- **Notebook Cell 5**: Imports and starts Flask app
- **Notebook Cell 8**: Weaviate client configuration
- **Notebook Cell 14**: Vectorizer configuration

### Solution

Ensure all port references are consistent. The current implementation uses **port 9500** throughout:

**Cell 5 (kill_processes_on_ports):**
```python
kill_processes_on_ports([5000, 8080, 8097, 50050, 50051])
# Should include 9500 if that's the port Flask uses
```

**Cell 8 (Weaviate environment variables):**
```python
"TRANSFORMERS_INFERENCE_API": "http://127.0.0.1:9500/",
"RERANKER_INFERENCE_API": "http://127.0.0.1:9500/"
```

**Cell 14 (Vectorizer config):**
```python
inference_url="http://127.0.0.1:9500"
```

**flask_app.py:**
```python
app.run(host='0.0.0.0', port=9500, debug=False)
```

### Why Port 9500?

Port 5000 is often used by:
- macOS AirPlay Receiver (since macOS Monterey)
- Other development servers (e.g., Flask defaults)

Using port 9500 avoids conflicts with system services and other common development tools.

---

## Additional Notes

### Typo in Cell 16

```python
if client.collections.exists("example_collectiom"):  # ← Typo: "collectiom"
    client.collections.delete("example_collection")   # ← Correct: "collection"
```

This typo causes the delete to never execute because the check looks for a collection with the wrong name. The correct check should be:

```python
if client.collections.exists("example_collection"):
    client.collections.delete("example_collection")
```

### Data Insertion Performance

The notebook uses `batch_size=1` and `concurrent_requests=1`, which means each document is processed sequentially:

```python
with collection.batch.fixed_size(batch_size=1, concurrent_requests=1) as batch:
    for document in tqdm(data):
        uuid = generate_uuid5(document)
        batch.add_object(properties=document, uuid=uuid)
```

For the 20 documents in this demo, this is fine. For larger datasets, consider:
- Increasing `batch_size` (e.g., 100)
- Increasing `concurrent_requests` (e.g., 4)

Example:
```python
with collection.batch.fixed_size(batch_size=100, concurrent_requests=4) as batch:
    # ... same loop
```

### Cell Execution Order

Some cells in the notebook (like Cell 57 - Reranking) use the variable `result` from previous cells, but then Cell 58 also references `result.objects`. If cells are run out of order, this can cause confusion. The reranking cell should store its result in `response`, which it does, but Cell 58 should use `response.objects` instead of `result.objects`:

**Cell 57:**
```python
response = collection.query.near_text(...)  # ← stored in 'response'
```

**Cell 58 (current - incorrect):**
```python
for obj in result.objects:  # ← should be 'response.objects'
    print_object_properties(obj.properties)
```

**Cell 58 (corrected):**
```python
for obj in response.objects:
    print_object_properties(obj.properties)
```

---

## Testing Checklist

Before running the notebook, ensure:

1. ✅ **Environment activated**: `conda activate agentic-ai`
2. ✅ **Environment variables set**: `VECTORDB_MODEL_CACHE` in `.env`
3. ✅ **Flask app updated**: Using `request.get_json(force=True)`
4. ✅ **Port configuration consistent**: All references use port 9500
5. ✅ **No port conflicts**: Run `lsof -ti :9500 | xargs kill -9` if needed
6. ✅ **Weaviate embedded dependencies**: Included in `weaviate-client>=4.0`

---

## Quick Fix Summary

### flask_app.py

```python
# Change both /vectors and /rerank endpoints:
data = request.json  # WRONG
data = request.get_json(force=True)  # CORRECT
```

### Notebook Cell 16

```python
if client.collections.exists("example_collectiom"):  # WRONG
if client.collections.exists("example_collection"):  # CORRECT
```

### Notebook Cell 17

```python
reranker_config=Configure.Reranker.transformers(
    inference_url="http://127.0.0.1:9500"  # WRONG - parameter not accepted
)

reranker_config=Configure.Reranker.transformers()  # CORRECT
```

### Notebook Cell 58

```python
for obj in result.objects:  # WRONG - uses stale variable
for obj in response.objects:  # CORRECT
```

---

## End-to-End Test

A full end-to-end test script is available at:
- `test_C1M3_Lab1_e2e.py`

Run it with:
```bash
conda activate agentic-ai
python test_C1M3_Lab1_e2e.py
```

Expected output:
```
============================================================
  SUMMARY
============================================================

  ALL STEPS PASSED ✓
```

---

## Related Files

- **Notebook**: `C1M3_Ungraded_Lab_1.ipynb`
- **Flask App**: `flask_app.py` (fixed)
- **Original Flask App**: `flask_app_v0.py` (for reference)
- **Test Script**: `test_C1M3_Lab1_e2e.py`
- **Example Test**: `test_notebook_e2e.py`
- **Utilities**: `utils.py`
- **Data**: `data.joblib`

---

## Questions?

If you encounter additional issues:

1. Check Flask server is running: `curl http://127.0.0.1:9500/.well-known/ready`
2. Check for port conflicts: `lsof -i :9500`
3. Verify environment: `conda env list | grep agentic`
4. Check environment variables: `echo $VECTORDB_MODEL_CACHE`
5. Review Weaviate logs in the test output

---

**Document created**: 2026-02-09  
**Last tested with**: `weaviate-client==4.9.3`, `flask==3.1.0`, `sentence-transformers==3.3.1`
