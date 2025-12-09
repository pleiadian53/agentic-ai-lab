# L4 Local Setup Notes

This document covers adjustments needed when running the L4 notebook locally (outside the DeepLearning.AI course platform).

## Quick Start (Local)

```bash
cd /Users/pleiadian53/work/agentic-ai-lab/mcp/L4/mcp_project
mamba activate agentic-ai
npx @modelcontextprotocol/inspector python research_server.py
```

---

## Differences from Course Platform

### 1. Terminal Cell (Cell 14)

The notebook contains:

```python
IFrame(f"{os.environ.get('DLAI_LOCAL_URL').format(port=8888)}terminals/1", 
       width=600, height=768)
```

**Problem**: `DLAI_LOCAL_URL` is not set locally → `AttributeError: 'NoneType' object has no attribute 'format'`

**Solution**: Skip this cell. Use your IDE's terminal directly.

---

### 2. Inspector Proxy Address (Cell 16 instructions)

The notebook says to specify an "Inspector Proxy Address" under Configuration.

**For local use**: Leave the field **empty** (or use `http://localhost:6277` if required).

This setting is only needed on the course platform where the Inspector runs on a remote server.

---

### 3. Using mamba Instead of uv

The notebook uses `uv` for environment setup. Since you already have `mamba` with dependencies installed:

| Notebook instruction | Local equivalent |
|---------------------|------------------|
| `uv init` | Skip (not needed) |
| `uv venv` | Skip (use existing env) |
| `source .venv/bin/activate` | `mamba activate agentic-ai` |
| `uv add mcp arxiv` | Skip (already installed) |
| `npx ... uv run research_server.py` | `npx ... python research_server.py` |

---

## Full Local Workflow

### Step 1: Generate the server file

Run the `%%writefile` cell in the notebook to create `mcp_project/research_server.py`.

### Step 2: Launch Inspector

```bash
cd /Users/pleiadian53/work/agentic-ai-lab/mcp/L4/mcp_project
mamba activate agentic-ai
npx @modelcontextprotocol/inspector python research_server.py
```

You'll see output like:

```
Starting MCP inspector...
⚙️ Proxy server listening on localhost:6277
🔑 Session token: <token>

🚀 MCP Inspector is up and running at:
   http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=<token>

🌐 Opening browser...
```

### Step 3: Connect in Inspector UI

1. The browser opens automatically to `http://localhost:6274`
2. Under **Server Entry**:
   - **Command**: `python`
   - **Arguments**: `research_server.py`
3. Under **Configuration**:
   - **Inspector Proxy Address**: Leave empty (or `http://localhost:6277`)
   - **Proxy Session Token**: Auto-filled from URL
4. Click **Connect**

### Step 4: Test Tools

1. Go to **Tools** tab
2. Click `search_papers`
3. Enter a topic (e.g., `"machine learning"`)
4. Click **Run Tool**
5. Check results and `papers/` directory

### Step 5: Stop Inspector

Press `Ctrl+C` in the terminal to stop the Inspector and server.

---

## Troubleshooting

### "Need to install the following packages"

When running `npx @modelcontextprotocol/inspector ...` for the first time:

```
Need to install the following packages:
@modelcontextprotocol/inspector@0.17.5
Ok to proceed? (y)
```

Type `y` to proceed. This is normal—npx downloads the package on first use.

### Connection Issues

If the Inspector can't connect to your server:

1. Ensure you're in the correct directory (`mcp_project/`)
2. Verify the server file exists: `ls research_server.py`
3. Test the server directly: `python research_server.py` (should hang waiting for stdio input)
4. Check that `mcp` and `arxiv` are installed: `python -c "import mcp; import arxiv; print('OK')"`

### Port Already in Use

If ports 6274 or 6277 are busy:

```bash
# Find what's using the port
lsof -i :6274

# Kill if needed
kill -9 <PID>
```
