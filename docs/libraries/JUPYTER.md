# Jupyter Notebook Environment

Documentation for Jupyter and interactive notebook libraries.

## Overview

These libraries provide an interactive development environment for experimenting with agents, analyzing data, and running course notebooks.

---

## Core Jupyter

### jupyter

**Jupyter Metapackage**

The `jupyter` package is a metapackage that installs the complete Jupyter ecosystem.

**Includes:**
- jupyter_core: Core functionality
- jupyter_client: Kernel communication
- jupyter_server: Backend server
- notebook: Classic notebook interface
- ipykernel: Python kernel

**Installation:**
```bash
# Already included in environment.yml
mamba env create -f environment.yml
conda activate agentic-ai
```

**Starting Jupyter:**
```bash
# Classic notebook
jupyter notebook

# Specific port
jupyter notebook --port=8888

# No browser
jupyter notebook --no-browser

# Specific directory
jupyter notebook /path/to/notebooks
```

---

### jupyter_server

**Jupyter Server Backend**

The backend server that powers Jupyter web applications.

**Features:**
- REST API for notebooks
- Kernel management
- File operations
- WebSocket support
- Extension system

**Configuration:**
```python
# jupyter_server_config.py
c.ServerApp.ip = '0.0.0.0'  # Listen on all interfaces
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.token = ''  # Disable token (dev only!)
c.ServerApp.password = ''  # Or set password
```

**Programmatic Usage:**
```python
from jupyter_server.serverapp import ServerApp

app = ServerApp()
app.initialize(argv=[])
app.start()
```

---

### notebook

**Classic Jupyter Notebook Interface**

The traditional notebook interface for `.ipynb` files.

**Key Features:**
- Cell-based execution
- Markdown support
- Rich output (plots, tables, HTML)
- Magic commands
- Extensions

**Cell Types:**
- **Code**: Execute Python code
- **Markdown**: Documentation, equations (LaTeX)
- **Raw**: Unformatted text

**Magic Commands:**
```python
# Line magics (single line)
%time result = expensive_function()  # Time execution
%timeit fast_function()  # Multiple runs, average time
%load script.py  # Load code from file
%run script.py  # Execute Python file
%matplotlib inline  # Display plots inline
%pwd  # Print working directory
%ls  # List files

# Cell magics (entire cell)
%%time
# Code block
result = process_data()

%%writefile script.py
# Write cell contents to file
def my_function():
    pass

%%bash
# Run bash commands
ls -la
echo "Hello"

%%html
<h1>HTML Content</h1>

%%javascript
console.log("JavaScript code");
```

**Keyboard Shortcuts:**
- `Shift+Enter`: Run cell, move to next
- `Ctrl+Enter`: Run cell, stay
- `Alt+Enter`: Run cell, insert below
- `A`: Insert cell above
- `B`: Insert cell below
- `DD`: Delete cell
- `M`: Change to markdown
- `Y`: Change to code
- `L`: Toggle line numbers

---

### nbclassic

**Classic Notebook Interface for Jupyter**

Provides the classic notebook interface as a Jupyter Server extension.

**Why Needed:**
- Compatibility with older notebooks
- Familiar interface
- Extension support
- Transition from classic to JupyterLab

**Usage:**
```bash
# Start nbclassic
jupyter nbclassic

# Or use regular notebook command
jupyter notebook
```

---

## Interactive Widgets

### ipywidgets

**Interactive Widgets for Jupyter**

Create interactive UI elements in notebooks.

**Basic Widgets:**
```python
import ipywidgets as widgets
from IPython.display import display

# Slider
slider = widgets.IntSlider(
    value=50,
    min=0,
    max=100,
    step=1,
    description='Value:',
    continuous_update=False
)
display(slider)

# Text input
text = widgets.Text(
    value='',
    placeholder='Enter prompt',
    description='Prompt:',
)
display(text)

# Dropdown
dropdown = widgets.Dropdown(
    options=['gpt-4', 'claude-3', 'mistral'],
    value='gpt-4',
    description='Model:',
)
display(dropdown)

# Button
button = widgets.Button(
    description='Generate',
    button_style='success',
    icon='check'
)

def on_button_click(b):
    print(f"Generating with {dropdown.value}")
    print(f"Prompt: {text.value}")

button.on_click(on_button_click)
display(button)
```

**Interactive Functions:**
```python
from ipywidgets import interact, interactive

@interact(x=(0, 10), y=(0, 10))
def plot_function(x=5, y=5):
    import matplotlib.pyplot as plt
    plt.plot([0, x], [0, y])
    plt.show()

# Or use interactive
def f(model, temperature):
    print(f"Model: {model}, Temp: {temperature}")

interactive_plot = interactive(
    f,
    model=['gpt-4', 'claude-3'],
    temperature=(0.0, 2.0, 0.1)
)
display(interactive_plot)
```

**Layout Widgets:**
```python
# HBox (horizontal)
hbox = widgets.HBox([slider, button])
display(hbox)

# VBox (vertical)
vbox = widgets.VBox([text, dropdown, button])
display(vbox)

# Tab
tab = widgets.Tab()
tab.children = [widgets.Label('Tab 1'), widgets.Label('Tab 2')]
tab.set_title(0, 'First')
tab.set_title(1, 'Second')
display(tab)

# Accordion
accordion = widgets.Accordion(children=[
    widgets.Label('Content 1'),
    widgets.Label('Content 2')
])
accordion.set_title(0, 'Section 1')
accordion.set_title(1, 'Section 2')
display(accordion)
```

**Progress Bars:**
```python
from ipywidgets import IntProgress
from IPython.display import display
import time

# Progress bar
progress = IntProgress(
    value=0,
    min=0,
    max=100,
    description='Processing:',
    bar_style='info'
)
display(progress)

# Update progress
for i in range(100):
    time.sleep(0.1)
    progress.value = i + 1
```

**Use Cases:**
- Interactive parameter tuning
- Model selection UI
- Progress tracking
- Data exploration
- Dashboards

---

### ipykernel

**IPython Kernel for Jupyter**

The Python kernel that executes code in Jupyter notebooks.

**Features:**
- Code execution
- Rich display system
- Magic commands
- Variable inspection
- Debugging support

**Installation as Kernel:**
```bash
# Install kernel for environment
python -m ipykernel install --user --name=agentic-ai --display-name="Python (agentic-ai)"

# List installed kernels
jupyter kernelspec list

# Remove kernel
jupyter kernelspec uninstall agentic-ai
```

**Rich Display:**
```python
from IPython.display import display, HTML, Markdown, Image, JSON

# Display HTML
display(HTML('<h1>Title</h1><p>Content</p>'))

# Display Markdown
display(Markdown('# Header\n**Bold** text'))

# Display image
display(Image('plot.png'))

# Display JSON
display(JSON({'key': 'value', 'nested': {'data': [1, 2, 3]}}))

# Display DataFrame (automatically formatted)
import pandas as pd
df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
display(df)
```

**Variable Inspection:**
```python
# In notebook
?function_name  # Show docstring
??function_name  # Show source code
%whos  # List all variables
%who  # List variable names only
```

---

## Notebook Best Practices

### Project Structure

```
notebooks/
├── 01_exploration.ipynb       # Data exploration
├── 02_agent_development.ipynb # Agent prototyping
├── 03_evaluation.ipynb        # Testing and evaluation
├── 04_visualization.ipynb     # Results visualization
└── utils/
    ├── __init__.py
    └── helpers.py              # Shared functions
```

### Code Organization

```python
# Cell 1: Imports and setup
import pandas as pd
import matplotlib.pyplot as plt
from src.agents import ResearchAgent

%matplotlib inline
%load_ext autoreload
%autoreload 2  # Auto-reload modules

# Cell 2: Configuration
CONFIG = {
    'model': 'gpt-4',
    'max_steps': 10,
    'temperature': 0.7
}

# Cell 3: Load data
df = pd.read_csv('data.csv')
df.head()

# Cell 4: Analysis
# ... analysis code ...

# Cell 5: Visualization
plt.figure(figsize=(10, 6))
plt.plot(df['x'], df['y'])
plt.show()
```

### Markdown Documentation

```markdown
# Research Agent Notebook

## Objective
Test the research agent with different prompts and models.

## Setup
- Model: GPT-4
- Max steps: 10
- Temperature: 0.7

## Results

### Experiment 1
Prompt: "Explain quantum computing"

**Observations:**
- Generated 5 sources
- Response time: 12.3s
- Cost: $0.045

### Conclusions
The agent performed well on technical topics.
```

### Saving Outputs

```python
# Save figures
plt.savefig('results/plot.png', dpi=300, bbox_inches='tight')

# Save data
df.to_csv('results/analysis.csv', index=False)
df.to_parquet('results/analysis.parquet')

# Save models
import pickle
with open('models/agent_state.pkl', 'wb') as f:
    pickle.dump(agent_state, f)
```

---

## Course Notebook Example

```python
# Cell 1: Setup
"""
# Module 2: Agentic Workflow

This notebook demonstrates building a research agent.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
import ipywidgets as widgets

load_dotenv()
client = OpenAI()

# Cell 2: Define Agent
def research_agent(prompt, model="gpt-4"):
    """Simple research agent"""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a research assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Cell 3: Interactive UI
prompt_widget = widgets.Textarea(
    value='',
    placeholder='Enter research topic',
    description='Topic:',
    layout=widgets.Layout(width='100%', height='100px')
)

model_widget = widgets.Dropdown(
    options=['gpt-4', 'gpt-3.5-turbo'],
    value='gpt-4',
    description='Model:'
)

button = widgets.Button(description='Research', button_style='primary')
output = widgets.Output()

def on_click(b):
    with output:
        output.clear_output()
        print("Researching...")
        result = research_agent(prompt_widget.value, model_widget.value)
        print("\n" + "="*50)
        print(result)

button.on_click(on_click)

display(widgets.VBox([prompt_widget, model_widget, button, output]))

# Cell 4: Test
# Run the cell above and try different prompts!
```

---

## Debugging in Notebooks

```python
# Enable debugging
%pdb on  # Auto-start debugger on exception

# Manual breakpoint
import pdb; pdb.set_trace()

# IPython debugger (better)
from IPython.core.debugger import set_trace
set_trace()

# Debug cell
%%debug
# Code to debug

# Post-mortem debugging
%debug  # After exception, inspect state
```

---

## Extensions and Customization

### Useful Extensions

```bash
# Install extensions
pip install jupyter_contrib_nbextensions
jupyter contrib nbextension install --user

# Enable extensions
jupyter nbextension enable codefolding/main
jupyter nbextension enable execute_time/ExecuteTime
jupyter nbextension enable toc2/main
```

### Custom CSS

```python
# In notebook
from IPython.display import HTML

HTML('''
<style>
    .output_png {
        display: flex;
        justify-content: center;
    }
    div.cell {
        max-width: 1200px;
    }
</style>
''')
```

---

## Converting Notebooks

```bash
# To Python script
jupyter nbconvert --to script notebook.ipynb

# To HTML
jupyter nbconvert --to html notebook.ipynb

# To PDF (requires LaTeX)
jupyter nbconvert --to pdf notebook.ipynb

# To slides
jupyter nbconvert --to slides notebook.ipynb --post serve

# Execute and convert
jupyter nbconvert --to html --execute notebook.ipynb
```

---

## See Also

- [Complete Dependencies](DEPENDENCIES.md)
- [Data Science Tools](DATA_SCIENCE.md)
- [Environment Setup](../ENVIRONMENT_SETUP.md)
- [IPyWidgets Documentation](https://ipywidgets.readthedocs.io/)
- [Jupyter Documentation](https://jupyter.org/documentation)
