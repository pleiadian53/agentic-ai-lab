# Streamlit Integration Tutorial - Chart Agent API

## What is Streamlit?

**Streamlit** is a Python framework for building data apps quickly. It's perfect for data scientists who want to create interactive web apps without learning HTML/CSS/JavaScript.

**Key Features:**
- **Pure Python** - No frontend code needed
- **Instant updates** - Auto-reloads on code changes
- **Built-in widgets** - Buttons, sliders, file uploads, etc.
- **Easy deployment** - One-click deploy to Streamlit Cloud
- **Data-focused** - Great for charts, tables, metrics

## Why Streamlit for Chart Agent?

- **Rapid prototyping** - Build UI in minutes
- **Python-native** - Use familiar libraries
- **Interactive charts** - Built-in charting support
- **Easy sharing** - Share link with colleagues
- **No DevOps** - Deploy without infrastructure setup

## Installation

```bash
pip install streamlit requests pandas
```

## Quick Start: Basic App

Create `chart_agent_app.py`:

```python
import streamlit as st
import requests
import pandas as pd

# Configure page
st.set_page_config(
    page_title="Chart Agent",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Chart Agent - AI-Powered Visualization")
st.markdown("Generate publication-ready charts from natural language")

# API configuration
API_BASE_URL = "http://localhost:8003"

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # Model selection
    model = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-5-mini", "gpt-5", "gpt-5.1-codex-mini"],
        index=0
    )
    
    # Output format
    output_format = st.selectbox(
        "Output Format",
        ["pdf", "png"],
        index=0
    )

# Main content
tab1, tab2, tab3 = st.tabs(["Generate", "Execute", "History"])

with tab1:
    st.header("Generate Chart Code")
    
    # Get available datasets
    try:
        response = requests.get(f"{API_BASE_URL}/datasets")
        datasets = response.json()["datasets"]
        dataset_options = {ds["name"]: ds["path"] for ds in datasets}
    except Exception as e:
        st.error(f"Failed to load datasets: {e}")
        dataset_options = {}
    
    # Dataset selection
    dataset_name = st.selectbox(
        "Select Dataset",
        options=list(dataset_options.keys())
    )
    dataset_path = dataset_options.get(dataset_name, "")
    
    # Question input
    question = st.text_area(
        "What chart do you want to create?",
        placeholder="e.g., Show the top 20 genes with the most splice sites",
        height=100
    )
    
    # Context input
    context = st.text_area(
        "Additional Context (optional)",
        placeholder="e.g., Focus on standard chromosomes only. Use publication-ready styling.",
        height=80
    )
    
    # Generate button
    if st.button("Generate Code", type="primary", use_container_width=True):
        if not question:
            st.warning("Please enter a question")
        else:
            with st.spinner("Generating code..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/analyze",
                        json={
                            "dataset_path": dataset_path,
                            "question": question,
                            "context": context if context else None,
                            "model": model
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Store in session state
                        st.session_state.generated_code = result["code"]
                        st.session_state.explanation = result["explanation"]
                        st.session_state.libraries = result["libraries_used"]
                        st.session_state.dataset_path = dataset_path
                        
                        st.success("Code generated successfully!")
                    else:
                        st.error(f"Generation failed: {response.text}")
                        
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # Display generated code
    if "generated_code" in st.session_state:
        st.subheader("Generated Code")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(st.session_state.explanation)
        with col2:
            st.metric("Libraries", len(st.session_state.libraries))
        
        st.code(st.session_state.generated_code, language="python")
        
        # Copy button (using download button as workaround)
        st.download_button(
            label="📋 Copy Code",
            data=st.session_state.generated_code,
            file_name="chart_code.py",
            mime="text/plain"
        )

with tab2:
    st.header("Execute Chart Code")
    
    if "generated_code" not in st.session_state:
        st.info("Generate code first in the 'Generate' tab")
    else:
        st.code(st.session_state.generated_code, language="python")
        
        if st.button("Execute & Generate Chart", type="primary", use_container_width=True):
            with st.spinner("Executing code and generating chart..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/execute",
                        json={
                            "code": st.session_state.generated_code,
                            "dataset_path": st.session_state.dataset_path,
                            "output_format": output_format
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if result["success"]:
                            # Get chart URL
                            image_path = result["image_path"]
                            chart_url = f"{API_BASE_URL}{image_path}"
                            
                            st.session_state.chart_url = chart_url
                            st.session_state.execution_logs = result.get("logs", "")
                            
                            st.success("Chart generated successfully!")
                        else:
                            st.error(f"Execution failed: {result.get('error', 'Unknown error')}")
                            st.text_area("Execution Logs", result.get("logs", ""), height=200)
                    else:
                        st.error(f"Request failed: {response.text}")
                        
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Display chart
        if "chart_url" in st.session_state:
            st.subheader("Generated Chart")
            
            # Download button
            try:
                chart_response = requests.get(st.session_state.chart_url)
                st.download_button(
                    label="📥 Download Chart",
                    data=chart_response.content,
                    file_name=f"chart.{output_format}",
                    mime=f"application/{output_format}"
                )
            except:
                pass
            
            # Display chart (if PDF, show link; if PNG, show image)
            if output_format == "png":
                st.image(st.session_state.chart_url, use_column_width=True)
            else:
                st.markdown(f"[View Chart]({st.session_state.chart_url})")
                # Embed PDF
                st.markdown(
                    f'<iframe src="{st.session_state.chart_url}" width="100%" height="600px"></iframe>',
                    unsafe_allow_html=True
                )

with tab3:
    st.header("Chart History")
    st.info("History feature coming soon!")
    st.markdown("This will show all previously generated charts with options to:")
    st.markdown("- View past charts")
    st.markdown("- Re-execute with different parameters")
    st.markdown("- Compare multiple charts")
    st.markdown("- Export chart collection")
```

## Running the App

### Step 1: Start Chart Agent API

```bash
cd chart_agent/server
mamba run -n agentic-ai python manage.py start
```

### Step 2: Run Streamlit App

```bash
streamlit run chart_agent_app.py
```

Opens at: http://localhost:8501

## Advanced Features

### Add Critique Workflow

```python
# In tab1, after generating code
if st.button("Critique Code"):
    with st.spinner("Critiquing code..."):
        try:
            response = requests.post(
                f"{API_BASE_URL}/critique",
                json={
                    "code": st.session_state.generated_code,
                    "domain_context": "Genomics research on splice sites",
                    "model": model
                }
            )
            
            if response.status_code == 200:
                critique = response.json()
                
                st.subheader("Code Critique")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Quality", critique["quality"])
                with col2:
                    st.metric("Issues", len(critique["issues"]))
                with col3:
                    st.metric("Suggestions", len(critique["suggestions"]))
                
                if critique["issues"]:
                    st.warning("Issues Found:")
                    for issue in critique["issues"]:
                        st.markdown(f"- {issue}")
                
                if critique["suggestions"]:
                    st.success("Suggestions:")
                    for suggestion in critique["suggestions"]:
                        st.markdown(f"- {suggestion}")
        except Exception as e:
            st.error(f"Critique failed: {e}")
```

### Add Chart Comparison

```python
# Store multiple charts
if "chart_history" not in st.session_state:
    st.session_state.chart_history = []

# After successful execution
st.session_state.chart_history.append({
    "question": question,
    "url": chart_url,
    "timestamp": datetime.now()
})

# In history tab
for i, chart in enumerate(st.session_state.chart_history):
    with st.expander(f"Chart {i+1}: {chart['question'][:50]}..."):
        st.image(chart["url"])
        st.caption(f"Generated: {chart['timestamp']}")
```

### Add File Upload

```python
# Allow users to upload their own datasets
uploaded_file = st.file_uploader("Upload Dataset", type=["csv", "tsv"])

if uploaded_file:
    # Save temporarily
    with open(f"/tmp/{uploaded_file.name}", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    dataset_path = f"/tmp/{uploaded_file.name}"
    st.success(f"Uploaded: {uploaded_file.name}")
```

### Add Caching

```python
# Cache dataset list
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_datasets():
    response = requests.get(f"{API_BASE_URL}/datasets")
    return response.json()["datasets"]

# Cache generated code
@st.cache_data
def generate_code(dataset_path, question, context, model):
    response = requests.post(
        f"{API_BASE_URL}/analyze",
        json={
            "dataset_path": dataset_path,
            "question": question,
            "context": context,
            "model": model
        }
    )
    return response.json()
```

## Deployment

### Deploy to Streamlit Cloud

1. **Push to GitHub**:
   ```bash
   git add chart_agent_app.py
   git commit -m "Add Streamlit app"
   git push
   ```

2. **Create `requirements.txt`**:
   ```
   streamlit
   requests
   pandas
   ```

3. **Deploy**:
   - Go to https://share.streamlit.io/
   - Connect GitHub repo
   - Select `chart_agent_app.py`
   - Click "Deploy"

4. **Configure secrets** (for API URL):
   - In Streamlit Cloud dashboard
   - Add secret: `API_BASE_URL = "https://your-api.com"`
   - Update code:
     ```python
     API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8003")
     ```

### Deploy to Heroku

Create `Procfile`:
```
web: streamlit run chart_agent_app.py --server.port=$PORT
```

Deploy:
```bash
heroku create chart-agent-app
git push heroku main
```

## Styling and Customization

### Custom Theme

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1976d2"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
```

### Custom CSS

```python
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #1976d2;
        color: white;
    }
    .stTextArea>div>div>textarea {
        font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)
```

## Best Practices

1. **Session State** - Use `st.session_state` for data persistence
2. **Caching** - Cache expensive operations with `@st.cache_data`
3. **Error Handling** - Always wrap API calls in try-except
4. **Loading States** - Use `st.spinner()` for async operations
5. **Input Validation** - Validate before sending to API
6. **Responsive Layout** - Use columns for better organization
7. **Clear Feedback** - Use st.success/error/warning/info
8. **Secrets Management** - Use `st.secrets` for sensitive data

## Comparison: Streamlit vs React

| Feature | Streamlit | React |
|---------|-----------|-------|
| Language | Python | JavaScript |
| Learning Curve | Easy | Moderate |
| Development Speed | Very Fast | Moderate |
| Customization | Limited | Unlimited |
| Deployment | Simple | Complex |
| Best For | Data apps, prototypes | Production apps |
| State Management | Built-in | Manual (Redux, etc.) |
| UI Components | Limited but sufficient | Unlimited |

**Use Streamlit when:**
- Rapid prototyping needed
- Team is Python-focused
- Simple data app requirements
- Quick internal tools

**Use React when:**
- Complex UI interactions needed
- Custom branding required
- Large-scale production app
- Frontend team available

## Troubleshooting

### App Won't Start

```bash
# Check Streamlit version
streamlit --version

# Reinstall if needed
pip install --upgrade streamlit
```

### API Connection Failed

```python
# Add connection test
try:
    response = requests.get(f"{API_BASE_URL}/health", timeout=5)
    st.success("✅ API Connected")
except:
    st.error("❌ API Not Reachable - Start the Chart Agent service")
```

### Slow Performance

```python
# Add caching
@st.cache_data(ttl=600)
def expensive_operation():
    # Your code here
    pass

# Use st.spinner for feedback
with st.spinner("Processing..."):
    result = expensive_operation()
```

### Session State Issues

```python
# Initialize session state properly
if "key" not in st.session_state:
    st.session_state.key = default_value

# Clear session state
if st.button("Reset"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
```

## Next Steps

1. **Add authentication** - Use `streamlit-authenticator`
2. **Add database** - Store chart history in SQLite/PostgreSQL
3. **Add export** - Batch export charts to PDF report
4. **Add scheduling** - Auto-generate charts on schedule
5. **Add sharing** - Share charts via email/Slack

## Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **Streamlit Gallery**: https://streamlit.io/gallery
- **Streamlit Components**: https://streamlit.io/components
- **Chart Agent API**: [../../server/QUICKSTART.md](../../server/QUICKSTART.md)
