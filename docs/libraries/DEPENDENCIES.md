# Complete Dependencies Reference

This document explains every library used in the Agentic AI project, organized by category.

## Table of Contents

- [Core Runtime](#core-runtime)
- [Agent & LLM Tools](#agent--llm-tools)
- [Web Framework & API](#web-framework--api)
- [Notebook Experience](#notebook-experience)
- [Data Analysis & Visualization](#data-analysis--visualization)
- [Machine Learning & NLP](#machine-learning--nlp)
- [Additional Tools](#additional-tools)

---

## Core Runtime

### python=3.11
- **Purpose**: Programming language runtime
- **Why 3.11**: Modern features, performance improvements, better error messages
- **Used for**: Everything - the foundation of the project
- **Docs**: https://docs.python.org/3.11/

### pip
- **Purpose**: Python package installer
- **Why needed**: Install packages not available in conda-forge
- **Used for**: Installing aisuite, anthropic, mistralai, etc.
- **Docs**: https://pip.pypa.io/

---

## Agent & LLM Tools

### aisuite==0.1.11
- **Purpose**: Unified interface for multiple LLM providers
- **Why needed**: Simplifies switching between OpenAI, Anthropic, Mistral, etc.
- **Used for**: Agent orchestration, multi-model support
- **Key features**: Provider abstraction, consistent API
- **Docs**: https://github.com/andrewyng/aisuite

### openai
- **Purpose**: Official OpenAI API client
- **Why needed**: Access GPT-4, GPT-3.5, embeddings, etc.
- **Used for**: Primary LLM for agent reasoning and generation
- **Key features**: Chat completions, embeddings, function calling
- **Docs**: https://platform.openai.com/docs

### anthropic
- **Purpose**: Official Anthropic API client
- **Why needed**: Access Claude models
- **Used for**: Alternative LLM provider, longer context windows
- **Key features**: Claude 3 models, extended context
- **Docs**: https://docs.anthropic.com/

### mistralai
- **Purpose**: Official Mistral AI API client
- **Why needed**: Access Mistral models
- **Used for**: Open-source friendly LLM option
- **Key features**: Mistral 7B, Mixtral models
- **Docs**: https://docs.mistral.ai/

### vertexai
- **Purpose**: Google Cloud Vertex AI client
- **Why needed**: Access Google's AI models (PaLM, Gemini)
- **Used for**: Google's LLM offerings
- **Key features**: Gemini models, enterprise features
- **Docs**: https://cloud.google.com/vertex-ai/docs

### tavily-python>=0.7.12
- **Purpose**: Web search API for AI agents
- **Why needed**: Real-time web search for research agents
- **Used for**: Gathering current information from the web
- **Key features**: AI-optimized search, source citations
- **Docs**: https://tavily.com/

### docstring-parser
- **Purpose**: Parse Python docstrings
- **Why needed**: Extract function documentation for agent tool descriptions
- **Used for**: Automatic tool documentation for LLMs
- **Key features**: Multiple docstring formats (Google, NumPy, etc.)
- **Docs**: https://github.com/rr-/docstring_parser

### textstat
- **Purpose**: Text statistics and readability metrics
- **Why needed**: Analyze generated text quality
- **Used for**: Readability scoring, text complexity analysis
- **Key features**: Flesch-Kincaid, SMOG, etc.
- **Docs**: https://github.com/textstat/textstat

### qrcode
- **Purpose**: QR code generation
- **Why needed**: Generate QR codes for sharing/linking
- **Used for**: Creating shareable links, mobile access
- **Key features**: PNG/SVG output, customizable
- **Docs**: https://github.com/lincolnloop/python-qrcode

---

## Web Framework & API

### fastapi
- **Purpose**: Modern web framework for building APIs
- **Why needed**: Core framework for the application
- **Used for**: REST API endpoints, request handling
- **Key features**: Async support, automatic docs, type validation
- **Docs**: https://fastapi.tiangolo.com/

### uvicorn
- **Purpose**: ASGI server for FastAPI
- **Why needed**: Run the FastAPI application
- **Used for**: Development and production server
- **Key features**: Hot reload, async support, WebSockets
- **Docs**: https://www.uvicorn.org/

### pydantic
- **Purpose**: Data validation using Python type hints
- **Why needed**: Request/response validation, settings management
- **Used for**: API models, configuration, data validation
- **Key features**: Type safety, JSON schema, validation
- **Docs**: https://docs.pydantic.dev/

### pydantic[email]
- **Purpose**: Email validation extension for pydantic
- **Why needed**: Validate email addresses in API requests
- **Used for**: User input validation
- **Key features**: RFC-compliant email validation
- **Docs**: https://docs.pydantic.dev/

### python-dotenv
- **Purpose**: Load environment variables from .env files
- **Why needed**: Manage API keys and configuration
- **Used for**: Loading OPENAI_API_KEY, TAVILY_API_KEY, etc.
- **Key features**: .env file parsing, environment management
- **Docs**: https://github.com/theskumar/python-dotenv

### python-multipart
- **Purpose**: Parse multipart/form-data requests
- **Why needed**: Handle file uploads in FastAPI
- **Used for**: File upload endpoints
- **Key features**: Streaming uploads, form data parsing
- **Docs**: https://github.com/andrew-d/python-multipart

### requests
- **Purpose**: HTTP library for making requests
- **Why needed**: Call external APIs (arXiv, PubMed, etc.)
- **Used for**: Research tools, external data fetching
- **Key features**: Simple API, session management, retries
- **Docs**: https://requests.readthedocs.io/

### sqlalchemy
- **Purpose**: SQL toolkit and ORM
- **Why needed**: Database operations, task persistence
- **Used for**: Storing tasks, results, agent state
- **Key features**: ORM, migrations, multiple DB support
- **Docs**: https://www.sqlalchemy.org/

### markdown
- **Purpose**: Markdown to HTML conversion
- **Why needed**: Render markdown reports
- **Used for**: Converting agent-generated markdown to HTML
- **Key features**: Extensions, safe HTML
- **Docs**: https://python-markdown.github.io/

---

## Notebook Experience

### jupyter
- **Purpose**: Jupyter notebook metapackage
- **Why needed**: Interactive development and experimentation
- **Used for**: Running course notebooks, prototyping agents
- **Key features**: Interactive cells, rich output
- **Docs**: https://jupyter.org/

### jupyter_server
- **Purpose**: Backend for Jupyter web applications
- **Why needed**: Powers Jupyter notebook interface
- **Used for**: Notebook server infrastructure
- **Key features**: REST API, kernel management
- **Docs**: https://jupyter-server.readthedocs.io/

### notebook
- **Purpose**: Classic Jupyter notebook interface
- **Why needed**: Traditional notebook UI
- **Used for**: Running .ipynb files
- **Key features**: Cell execution, markdown support
- **Docs**: https://jupyter-notebook.readthedocs.io/

### nbclassic
- **Purpose**: Classic notebook interface for Jupyter
- **Why needed**: Compatibility with older notebooks
- **Used for**: Legacy notebook support
- **Key features**: Classic UI, extensions
- **Docs**: https://github.com/jupyterlab/nbclassic

### ipywidgets
- **Purpose**: Interactive widgets for Jupyter
- **Why needed**: Create interactive UI elements in notebooks
- **Used for**: Progress bars, sliders, interactive visualizations
- **Key features**: Rich widgets, event handling
- **Docs**: https://ipywidgets.readthedocs.io/

### ipykernel
- **Purpose**: IPython kernel for Jupyter
- **Why needed**: Execute Python code in notebooks
- **Used for**: Code execution, variable inspection
- **Key features**: Magic commands, rich display
- **Docs**: https://ipykernel.readthedocs.io/

---

## Data Analysis & Visualization

### pandas
- **Purpose**: Data manipulation and analysis
- **Why needed**: Process research data, results analysis
- **Used for**: DataFrames, data cleaning, aggregation
- **Key features**: DataFrame API, time series, I/O
- **Docs**: https://pandas.pydata.org/

### matplotlib
- **Purpose**: Plotting and visualization library
- **Why needed**: Create charts and graphs
- **Used for**: Visualizing agent performance, data trends
- **Key features**: Publication-quality plots, customizable
- **Docs**: https://matplotlib.org/

### seaborn
- **Purpose**: Statistical data visualization
- **Why needed**: High-level plotting interface
- **Used for**: Statistical plots, beautiful defaults
- **Key features**: Built on matplotlib, statistical functions
- **Docs**: https://seaborn.pydata.org/

### duckdb
- **Purpose**: In-process SQL database
- **Why needed**: Fast analytical queries on data
- **Used for**: Data analysis, aggregations
- **Key features**: SQL interface, fast analytics, Parquet support
- **Docs**: https://duckdb.org/

### tabulate
- **Purpose**: Pretty-print tabular data
- **Why needed**: Format tables for display
- **Used for**: Console output, reports
- **Key features**: Multiple formats (markdown, HTML, etc.)
- **Docs**: https://github.com/astanin/python-tabulate

---

## Machine Learning & NLP

### scikit-learn
- **Purpose**: Machine learning library
- **Why needed**: ML algorithms, preprocessing, evaluation
- **Used for**: Classification, clustering, feature extraction
- **Key features**: Consistent API, many algorithms
- **Docs**: https://scikit-learn.org/

### jinja2
- **Purpose**: Template engine
- **Why needed**: Generate HTML, prompts from templates
- **Used for**: Web templates, dynamic prompt generation
- **Key features**: Template inheritance, filters
- **Docs**: https://jinja.palletsprojects.com/

---

## Additional Tools

### tinydb
- **Purpose**: Lightweight document database
- **Why needed**: Simple JSON-based storage
- **Used for**: Caching, lightweight persistence
- **Key features**: No server, pure Python, JSON storage
- **Docs**: https://tinydb.readthedocs.io/

### wikipedia
- **Purpose**: Wikipedia API wrapper
- **Why needed**: Search and retrieve Wikipedia content
- **Used for**: Research agent knowledge source
- **Key features**: Search, page content, summaries
- **Docs**: https://wikipedia.readthedocs.io/

### pdfminer.six
- **Purpose**: PDF text extraction
- **Why needed**: Extract text from PDF research papers
- **Used for**: Processing academic papers
- **Key features**: Layout analysis, text extraction
- **Docs**: https://pdfminersix.readthedocs.io/

### pymupdf
- **Purpose**: PDF processing library (PyMuPDF/fitz)
- **Why needed**: Fast PDF text extraction, alternative to pdfminer
- **Used for**: PDF parsing, text extraction
- **Key features**: Fast, comprehensive PDF support
- **Docs**: https://pymupdf.readthedocs.io/

### psycopg2
- **Purpose**: PostgreSQL adapter for Python
- **Why needed**: Connect to PostgreSQL databases
- **Used for**: Production database connections
- **Key features**: Full PostgreSQL support, connection pooling
- **Docs**: https://www.psycopg.org/

---

## Dependency Tree

### Core Dependencies
```
python 3.11
├── pip (package management)
├── fastapi (web framework)
│   ├── pydantic (validation)
│   ├── uvicorn (server)
│   └── starlette (ASGI framework)
├── sqlalchemy (database ORM)
└── jupyter (notebooks)
    ├── ipykernel (Python kernel)
    └── ipywidgets (interactive widgets)
```

### Agent Stack
```
aisuite (unified LLM interface)
├── openai (GPT models)
├── anthropic (Claude models)
├── mistralai (Mistral models)
└── vertexai (Google models)

tavily-python (web search)
wikipedia (knowledge base)
```

### Data Stack
```
pandas (data manipulation)
├── matplotlib (plotting)
├── seaborn (statistical viz)
└── duckdb (analytics)
```

---

## Version Pinning Strategy

### Exact Versions (==)
- **aisuite==0.1.11**: Specific version for API compatibility

### Minimum Versions (>=)
- **tavily-python>=0.7.12**: Minimum version for required features

### Flexible Versions (no constraint)
- Most packages: Use latest compatible versions from conda-forge

---

## Installation Sources

### From Conda-forge
- Python, FastAPI, pandas, scikit-learn, jupyter, etc.
- **Why**: Pre-compiled binaries, optimized builds, better dependency resolution

### From PyPI (via pip)
- aisuite, anthropic, mistralai, tavily-python, etc.
- **Why**: Not available in conda-forge, or newer versions needed

---

## See Also

- [Agent & LLM Tools Details](AGENT_LLM_TOOLS.md)
- [Web Framework Details](WEB_FRAMEWORK.md)
- [Data Science Tools](DATA_SCIENCE.md)
- [Jupyter Environment](JUPYTER.md)
- [Environment Setup](../ENVIRONMENT_SETUP.md)
