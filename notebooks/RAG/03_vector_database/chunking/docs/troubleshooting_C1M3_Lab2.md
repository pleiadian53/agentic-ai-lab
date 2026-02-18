# Troubleshooting Guide: C1M3_Ungraded_Lab_2.ipynb (Chunking)

This document describes the errors encountered when running the Chunking notebook and their solutions.

## Summary

The notebook had four main issues that prevented it from running successfully:

1. **Flask Content-Type Error**: Flask endpoints not handling Weaviate's requests without proper Content-Type headers
2. **Port Configuration**: Inconsistent port usage (5000 vs 9500)
3. **macOS Permission Error**: `psutil.net_connections()` requires elevated privileges on macOS
4. **Role Attribute Error**: `generate_with_single_input()` incorrectly handling role as enum vs string
5. **Token Length Warnings**: Some chunks exceed embedding model's 512-token limit (expected behavior)

All issues have been fixed in the updated `flask_app.py` and `utils.py`.

---

## Error 1: Flask Content-Type Handling

### Symptom

```
415 Unsupported Media Type: Did not attempt to load JSON data 
because the request Content-Type was not 'application/json'.
```

### Location

- **File**: `flask_app.py`
- **Endpoint**: `/vectors`

### Root Cause

Weaviate's `text2vec-transformers` module sends HTTP requests without the `Content-Type: application/json` header. Flask's `request.json` property requires this header and raises a 415 error if it's missing.

### Solution

Use `request.get_json(force=True)` instead of `request.json`:

**Before (Incorrect):**
```python
@app.route('/vectors', methods=['POST']) 
def vectorize():
    try:
        try:
            data = request.json.get('text')  # ← Fails without Content-Type header
        except Exception as e:
            try:
                data = request.data.decode("utf-8")
            except Exception as e:
                print(e)
        text = json.loads(data)
        # ...
```

**After (Correct):**
```python
@app.route('/vectors', methods=['POST']) 
def vectorize():
    """
    Weaviate text2vec-transformers sends:
        POST /vectors  {"text": "some text to embed", ...}
    and expects:
        {"text": "...", "vector": [0.1, 0.2, ...], "dim": 768}
    """
    try:
        # Use force=True to parse JSON regardless of Content-Type header
        data = request.get_json(force=True)
        if data is None:
            data = json.loads(request.data.decode("utf-8"))
        
        text = data.get('text', '')
        if isinstance(text, list):
            text = " ".join(text)
        # ...
```

### Reference

- See [Troubleshooting Guide for Lab 1](../../weaviate_demo/docs/troubleshooting_C1M3_Lab1.md#error-2-flask-content-type-handling) for detailed explanation

---

## Error 2: Port Configuration

### Symptom

Notebook references port 5000 but `flask_app.py` should use port 9500 to avoid conflicts with macOS system services.

### Location

- **Notebook Cell 5**: `kill_processes_on_ports([5000, ...])`
- **Notebook Cell 40**: `"TRANSFORMERS_INFERENCE_API":"http://127.0.0.1:5000/"`
- **Notebook Cell 41**: `inference_url="http://127.0.0.1:5000"`
- **File**: `flask_app.py` line 51: `app.run(port=5000)`

### Root Cause

Port 5000 is used by macOS AirPlay Receiver (since macOS Monterey) and other development servers.

### Solution

Update all port references to use **9500**:

**flask_app.py:**
```python
def run_app():
    app.run(host='0.0.0.0', port=9500, debug=False)  # Changed from 5000
```

**Notebook Cell 5:**
```python
kill_processes_on_ports([9500, 8080, 8097, 50050, 50051])  # Added 9500
```

**Notebook Cell 40:**
```python
"TRANSFORMERS_INFERENCE_API": "http://127.0.0.1:9500/",  # Changed from 5000
```

**Notebook Cell 41:**
```python
inference_url="http://127.0.0.1:9500",  # Changed from 5000
```

---

## Error 3: macOS psutil Permission Error

### Symptom

```
PermissionError: [Errno 1] Operation not permitted (originated from proc_pidinfo(PROC_PIDLISTFDS))
...
psutil.AccessDenied: (pid=25066)
RuntimeError: Failed to enumerate network connections
```

### Location

- **File**: `utils.py`
- **Function**: `kill_processes_on_ports()`
- **Line**: `conns = psutil.net_connections(kind='inet')`

### Root Cause

On macOS, `psutil.net_connections()` requires elevated privileges (sudo) to enumerate network connections across all processes. Without these privileges, it raises a `PermissionError` or `AccessDenied` exception.

### Solution

Add a fallback to use `lsof` (which doesn't require sudo for basic port queries):

**Before (Fails on macOS):**
```python
try:
    conns = psutil.net_connections(kind='inet')
except Exception as e:
    raise RuntimeError(f"Failed to enumerate network connections: {e}")
```

**After (macOS-compatible):**
```python
try:
    conns = psutil.net_connections(kind='inet')
except (psutil.AccessDenied, PermissionError) as e:
    # macOS often blocks this without sudo; fall back to lsof
    print(f"  Warning: Cannot enumerate connections ({e}), using lsof fallback...")
    import subprocess
    conns = []
    for port in target_ports:
        try:
            result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and result.stdout.strip():
                for pid_str in result.stdout.strip().split('\n'):
                    try:
                        pid = int(pid_str)
                        # Create a minimal connection-like object
                        class FakeConn:
                            def __init__(self, p):
                                self.pid = p
                                self.laddr = type('obj', (), {'port': port})()
                                self.type = socket.SOCK_STREAM
                                self.status = psutil.CONN_LISTEN
                        conns.append(FakeConn(pid))
                    except ValueError:
                        pass
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
except Exception as e:
    print(f"  Warning: Failed to enumerate network connections: {e}")
    conns = []
```

### Why This Works

- `lsof` (list open files) is a standard Unix utility that can list processes listening on specific ports
- It doesn't require sudo for basic queries like `-ti :PORT` (show PIDs for port)
- The fallback creates minimal "connection-like" objects that work with the rest of the function's logic

---

## Error 4: Role Attribute Error in RAG Integration

### Symptom

```
AttributeError: 'str' object has no attribute 'name'
```

Occurred in Cell 51 during RAG system integration when calling `generate_with_single_input()`.

### Location

- **File**: `utils.py`
- **Function**: `generate_with_single_input()`
- **Line 282**: `json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()`

### Root Cause

The function attempts to call `.name.lower()` on the role attribute, assuming it's an enum. However, the Together AI API returns roles as strings, not enums. The OpenAI library returns enums with a `.name` attribute, but Together returns plain strings.

### Solution

Handle both enum and string cases:

**Before (Fails with Together API):**
```python
client = Together(api_key=together_api_key)
json_dict = client.chat.completions.create(**payload).model_dump()
json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
```

**After (Works with both APIs):**
```python
client = Together(api_key=together_api_key)
json_dict = client.chat.completions.create(**payload).model_dump()
# Handle role - could be string or enum
role = json_dict['choices'][-1]['message']['role']
json_dict['choices'][-1]['message']['role'] = (
    role.name.lower() if hasattr(role, 'name') 
    else role.lower() if isinstance(role, str) 
    else str(role).lower()
)
```

### Technical Details

- **OpenAI SDK**: Returns `ChatCompletionMessage` with `role` as an enum (e.g., `MessageRole.ASSISTANT`)
- **Together SDK**: Returns role as a plain string (e.g., `"assistant"`)
- **Solution**: Check for `.name` attribute first, fall back to string handling

---

## Issue 5: Token Length Warnings (Expected Behavior)

### Symptom

Many warnings during data insertion:

```
Failed to send all objects in a batch of 1
Error: "This model's maximum context length is 512 tokens. 
However, you requested 523 tokens in the input for embedding generation."
```

### Location

- **Cell 42**: Batch insertion of chunks into vector database

### Root Cause

The embedding model (`BAAI/bge-base-en-v1.5` or similar) has a **512-token context window limit**. Some chunks in the dataset exceed this limit, especially:
- `fixed_size_100` chunks (some paragraphs are very long)
- `para_chunks` (natural paragraphs can be very long)
- `para_chunks_min_25` (merged paragraphs)

### Is This a Problem?

**No, this is expected behavior for a chunking demonstration**:

1. **Purpose of the Lab**: The notebook demonstrates different chunking strategies and their trade-offs
2. **Real-World Scenario**: In production, you'd either:
   - Use a model with a larger context window
   - Implement chunk size validation before insertion
   - Split oversized chunks automatically
3. **Still Functional**: The chunks that do fit (1470 out of 1487) are enough to demonstrate the concepts

### Statistics from Test Run

- **Total chunks attempted**: 1487 (672 + 173 + 549 + 93)
- **Successfully inserted**: 1470
- **Failed due to token limit**: 17 (about 1.1%)
- **Strategies affected**: Mostly `fixed_size_100`, `para_chunks`, and `para_chunks_min_25`

### Solutions for Production Use

If you need to handle all chunks in production:

**Option 1: Use a larger model**
```python
# Use a model with larger context window
vectorizer_config=[Configure.NamedVectors.text2vec_transformers(
    name="vector",
    model_name="sentence-transformers/all-mpnet-base-v2",  # 384 tokens → 768
    # ...
)]
```

**Option 2: Pre-validate chunk sizes**
```python
def tokenize_and_validate(text, max_tokens=512):
    # Simple word-count heuristic (actual tokenization would be better)
    approx_tokens = len(text.split()) * 1.3
    if approx_tokens > max_tokens:
        return None  # Skip this chunk
    return text

# Filter chunks before insertion
filtered_chunks = [c for c in chunks if tokenize_and_validate(c['chunk'])]
```

**Option 3: Auto-split oversized chunks**
```python
def split_if_needed(chunk_obj, max_tokens=512):
    text = chunk_obj['chunk']
    words = text.split()
    approx_tokens = len(words) * 1.3
    
    if approx_tokens <= max_tokens:
        return [chunk_obj]
    
    # Split into smaller sub-chunks
    max_words = int(max_tokens / 1.3)
    sub_chunks = []
    for i in range(0, len(words), max_words):
        sub_text = " ".join(words[i:i+max_words])
        sub_chunk = chunk_obj.copy()
        sub_chunk['chunk'] = sub_text
        sub_chunk['chunk_index'] = f"{chunk_obj['chunk_index']}.{i//max_words}"
        sub_chunks.append(sub_chunk)
    return sub_chunks
```

---

## Additional Notes

### Deprecation Warning

You may see this warning:

```
DeprecationWarning: Dep024: You are using the `vectorizer_config` argument 
in `collection.config.create()`, which is deprecated.
Use the `vector_config` argument instead.
```

**What it means**: Weaviate is transitioning from `vectorizer_config` to `vector_config` parameter name.

**Action required**: Update the notebook to use `vector_config`:

```python
collection = client.collections.create(
    name='chunking_example',
    vector_config=[...],  # Changed from vectorizer_config
    properties=[...]
)
```

### Thread Safety Warnings

You may see gRPC fork warnings:

```
I0000 ... fork_posix.cc:71] Other threads are currently calling into gRPC, 
skipping fork() handlers
```

**What it means**: Python's multiprocessing fork() happens while gRPC connections are active.

**Action required**: None. These are informational warnings that don't affect functionality. If concerned, you can set `daemon=True` on the Flask thread to prevent fork issues.

---

## Testing Checklist

Before running the notebook:

1. ✅ **Environment activated**: `conda activate agentic-ai`
2. ✅ **Environment variables set**: `TOGETHER_API_KEY` in `.env`
3. ✅ **Flask app updated**: Using `request.get_json(force=True)`
4. ✅ **Port configuration consistent**: All references use port 9500
5. ✅ **utils.py fixed**: Role handling for Together API
6. ✅ **utils.py fixed**: lsof fallback for macOS permissions
7. ✅ **No port conflicts**: Flask runs on port 9500
8. ✅ **Internet connection**: Required for downloading book text from GitHub

---

## Quick Fix Summary

### flask_app.py

```python
# Line ~22: Change request handling
data = request.json.get('text')  # WRONG
data = request.get_json(force=True)  # CORRECT

# Line ~51: Change port
app.run(port=5000)  # WRONG
app.run(port=9500, daemon=True)  # CORRECT
```

### utils.py

```python
# Line ~52: Add macOS fallback
try:
    conns = psutil.net_connections(kind='inet')
except Exception as e:
    raise RuntimeError(...)  # WRONG
    
try:
    conns = psutil.net_connections(kind='inet')
except (psutil.AccessDenied, PermissionError) as e:
    # Use lsof fallback  # CORRECT
    ...
except Exception as e:
    conns = []  # CORRECT

# Line ~282: Fix role handling
json_dict['choices'][-1]['message']['role'] = role.name.lower()  # WRONG

role = json_dict['choices'][-1]['message']['role']
json_dict['choices'][-1]['message']['role'] = (
    role.name.lower() if hasattr(role, 'name') 
    else role.lower() if isinstance(role, str) 
    else str(role).lower()
)  # CORRECT
```

### Notebook Cell 5

```python
kill_processes_on_ports([5000, 8080, 8097, 50050, 50051])  # WRONG
kill_processes_on_ports([9500, 8080, 8097, 50050, 50051])  # CORRECT
```

### Notebook Cell 40

```python
"TRANSFORMERS_INFERENCE_API":"http://127.0.0.1:5000/",  # WRONG
"TRANSFORMERS_INFERENCE_API":"http://127.0.0.1:9500/",  # CORRECT
```

### Notebook Cell 41

```python
inference_url="http://127.0.0.1:5000",  # WRONG
inference_url="http://127.0.0.1:9500",  # CORRECT
```

---

## End-to-End Test

A full end-to-end test script is available at:
- `test_C1M3_Lab2_e2e.py`

Run it with:
```bash
conda activate agentic-ai
python test_C1M3_Lab2_e2e.py
```

Expected output:
```
============================================================
  SUMMARY
============================================================

  ALL STEPS PASSED ✓
```

**Note**: First run will take 10-15 minutes to:
1. Download Pro Git book sections from GitHub
2. Generate chunks using 4 different strategies
3. Embed and insert ~1,470 chunks into Weaviate

Subsequent runs will be much faster (~1 minute) as the collection is persisted.

---

## Related Files

- **Notebook**: `C1M3_Ungraded_Lab_2.ipynb`
- **Flask App**: `flask_app.py` (fixed)
- **Utilities**: `utils.py` (fixed)
- **Test Script**: `test_C1M3_Lab2_e2e.py`
- **Similar Issues**: See `../weaviate_demo/docs/troubleshooting_C1M3_Lab1.md`

---

## Questions?

If you encounter additional issues:

1. **Flask not responding**: `curl http://127.0.0.1:9500/.well-known/ready`
2. **Port conflicts**: `lsof -i :9500`
3. **Verify environment**: `conda env list | grep agentic`
4. **Check API key**: `echo $TOGETHER_API_KEY`
5. **View test output**: Check terminal for detailed error messages
6. **Clear persisted data**: Delete `.collections/ungraded_lab_2/` folder and re-run

---

**Document created**: 2026-02-09  
**Last tested with**: `weaviate-client==4.9.3`, `flask==3.1.0`, `sentence-transformers==3.3.1`, `together==1.3.1`
