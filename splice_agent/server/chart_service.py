"""
FastAPI service for Chart Agent - Generative visualization service.

Provides endpoints for:
- Generating chart code (plans) from natural language
- Critiquing and refining code via reflection
- Executing code to produce plots
- Generating insights/captions for plots
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import duckdb
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import tempfile
import subprocess
import io
import contextlib

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from chart_agent.server.schemas import (
    AnalysisRequest,
    PlanResponse,
    CritiqueRequest,
    CritiqueResponse,
    ExecutionRequest,
    ExecutionResponse,
    InsightRequest,
    InsightResponse
)
from chart_agent.server import config
from chart_agent.planning import generate_chart_code
from chart_agent.data_access import DuckDBDataset, DataFrameDataset
from chart_agent.llm_client import call_llm_text, call_llm_json

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
DATASETS: Dict[str, Any] = {}  # Cache loaded datasets
CLIENT: Optional[OpenAI] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    global CLIENT
    
    # Startup
    logger.info("Starting Chart Agent API...")
    
    # Initialize OpenAI client
    CLIENT = OpenAI()
    logger.info("✓ OpenAI client initialized")
    
    # Log configuration
    logger.info(f"✓ Project root: {config.PROJECT_ROOT}")
    logger.info(f"✓ Data directory: {config.DATA_DIR}")
    logger.info(f"✓ Output directory: {config.OUTPUT_DIR}")
    
    logger.info("Chart Agent API ready!")
    
    yield
    
    # Shutdown (cleanup if needed)
    logger.info("Shutting down Chart Agent API...")


# Initialize FastAPI with lifespan
app = FastAPI(
    title="Chart Agent API",
    description="Generative visualization service with reflection and insight generation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=config.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving generated charts
app.mount("/charts", StaticFiles(directory=str(config.OUTPUT_DIR)), name="charts")


# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Provide user-friendly validation error messages"""
    errors = exc.errors()
    
    # Extract readable error messages
    readable_errors = []
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        msg = error["msg"]
        error_type = error["type"]
        
        # Special handling for enum validation (model selection)
        if error_type == "enum" and "model" in field:
            allowed = error.get("ctx", {}).get("expected", "")
            readable_errors.append({
                "field": field,
                "message": f"Invalid model name. Allowed values: {allowed}",
                "provided": error.get("input", "")
            })
        else:
            readable_errors.append({
                "field": field,
                "message": msg,
                "type": error_type
            })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "The request contains invalid data. Please check the fields below.",
            "details": readable_errors
        }
    )


class ChartGenerator:
    """Handles chart code generation"""
    
    def __init__(self, client: OpenAI):
        self.client = client
    
    def generate_plan(self, request: AnalysisRequest) -> PlanResponse:
        """Generate chart code from natural language request"""
        # Load dataset
        dataset = self._load_dataset(request.dataset_path)
        
        # Build user request with context
        user_request = request.question
        if request.context:
            user_request = f"{request.question}\n\nAdditional Context: {request.context}"
        
        # Generate code using chart_agent's planning function
        result = generate_chart_code(
            dataset=dataset,
            user_request=user_request,
            client=self.client,
            model=request.model.value,
            preferred_library="matplotlib"
        )
        
        # Extract code and metadata from result
        # generate_chart_code returns: {"code": str, "library": str, "chart_type": str, "model": str}
        code = result.get("code", "")
        chart_type = result.get("chart_type", "unknown")
        library = result.get("library", "matplotlib")
        
        # Build explanation from metadata
        explanation = f"Generated {chart_type} using {library}"
        
        # Extract libraries from code
        libraries = self._extract_libraries(code)
        
        # Ensure all fields are proper types
        response = PlanResponse(
            code=str(code),
            explanation=str(explanation),
            libraries_used=list(libraries) if libraries else []
        )
        
        logger.info(f"Generated plan: {len(code)} chars, {len(libraries)} libraries")
        return response
    
    def _load_dataset(self, dataset_path: str):
        """Load dataset with caching"""
        if dataset_path in DATASETS:
            logger.info(f"Using cached dataset: {dataset_path}")
            return DATASETS[dataset_path]
        
        logger.info(f"Loading dataset: {dataset_path}")
        
        # Resolve path using config helper
        path = config.resolve_dataset_path(dataset_path)
        
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_path}")
        
        # Use DuckDB for efficient loading
        if path.suffix in config.SUPPORTED_FORMATS:
            dataset = DuckDBDataset(str(path))
            DATASETS[dataset_path] = dataset
            return dataset
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {path.suffix}")
    
    def _extract_explanation(self, code: str) -> str:
        """Extract explanation from code comments"""
        lines = code.split('\n')
        explanation_lines = []
        for line in lines[:10]:  # Check first 10 lines
            if line.strip().startswith('#'):
                explanation_lines.append(line.strip('# '))
        return '\n'.join(explanation_lines) if explanation_lines else "Chart code generated"
    
    def _extract_libraries(self, code: str) -> list:
        """Extract imported libraries from code"""
        import re
        imports = re.findall(r'^import (\w+)', code, re.MULTILINE)
        from_imports = re.findall(r'^from (\w+)', code, re.MULTILINE)
        return list(set(imports + from_imports))


class CodeCritic:
    """Handles code critique and reflection"""
    
    def __init__(self, client: OpenAI):
        self.client = client
    
    def critique(self, request: CritiqueRequest) -> CritiqueResponse:
        """Critique generated code"""
        prompt = f"""Review this visualization code and provide structured critique.

Domain Context:
{request.domain_context}

Code:
```python
{request.code}
```

Analyze for:
1. Biological/domain relevance
2. Visual clarity and publication quality
3. Code quality and error handling
4. Best practices

Return JSON with:
{{
  "quality": "excellent|good|fair|poor",
  "strengths": ["strength1", "strength2"],
  "issues": [
    {{"severity": "critical|major|minor", "issue": "description", "suggestion": "fix"}}
  ],
  "needs_refinement": true|false
}}
"""
        
        critique = call_llm_json(
            client=self.client,
            model=request.model.value,
            messages=[
                {"role": "system", "content": "You are an expert in data visualization and code review."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return CritiqueResponse(**critique)


class CodeExecutor:
    """Handles safe code execution"""
    
    def execute(self, request: ExecutionRequest) -> ExecutionResponse:
        """Execute chart code and return image path"""
        try:
            # Load dataset using config helper
            dataset_path = config.resolve_dataset_path(request.dataset_path)
            
            if not dataset_path.exists():
                raise HTTPException(status_code=404, detail="Dataset not found")
            
            # Load data into DataFrame
            if dataset_path.suffix == '.tsv':
                df = pd.read_csv(dataset_path, sep='\t')
            elif dataset_path.suffix == '.csv':
                df = pd.read_csv(dataset_path)
            else:
                raise HTTPException(status_code=400, detail="Unsupported format")
            
            # Prepare execution environment
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            import matplotlib.pyplot as plt
            
            # Create output path using config helper
            output_file = config.get_output_path(f"chart_{hash(request.code) % 10000}.{request.output_format}")
            
            # Capture stdout/stderr
            logs_buffer = io.StringIO()
            
            with contextlib.redirect_stdout(logs_buffer), contextlib.redirect_stderr(logs_buffer):
                # Execute code in isolated namespace
                namespace = {
                    'df': df,
                    'pd': pd,
                    'plt': plt,
                    'np': __import__('numpy'),
                    'sns': __import__('seaborn')
                }
                
                exec(request.code, namespace)
                
                # Save figure
                if request.output_format == 'pdf':
                    plt.savefig(output_file, format='pdf', bbox_inches='tight')
                else:
                    plt.savefig(output_file, dpi=300, bbox_inches='tight')
                
                plt.close('all')
            
            logs = logs_buffer.getvalue()
            
            return ExecutionResponse(
                success=True,
                image_path=f"/charts/{output_file.name}",
                logs=logs or "Execution completed successfully"
            )
        
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return ExecutionResponse(
                success=False,
                image_path=None,
                logs=str(e),
                error=str(e)
            )


class InsightGenerator:
    """Generates insights and captions for plots"""
    
    def __init__(self, client: OpenAI):
        self.client = client
    
    def generate_insight(self, request: InsightRequest) -> InsightResponse:
        """Generate caption and insights for a plot"""
        prompt = f"""Generate a publication-ready caption and key insights for this visualization.

Title: {request.analysis_title}
Dataset Context: {request.dataset_context}

The caption should:
1. Describe what the figure shows (1-2 sentences)
2. Highlight key biological/scientific insights (1-2 sentences)
3. Mention any filtering or methods applied
4. Be suitable for a research paper

Also provide 3-5 key insights as bullet points.

Return JSON:
{{
  "caption": "Figure caption text...",
  "key_insights": ["insight1", "insight2", "insight3"]
}}
"""
        
        result = call_llm_json(
            client=self.client,
            model=request.model.value,
            messages=[
                {"role": "system", "content": "You are a scientific writer specializing in data visualization."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return InsightResponse(**result)


# API Endpoints
@app.get("/")
def root():
    """API info"""
    return {
        "service": "Chart Agent API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": [
            "POST /analyze - Generate chart code",
            "POST /critique - Review code quality",
            "POST /execute - Execute code and generate plot",
            "POST /insight - Generate caption for plot",
            "GET /datasets - List available datasets",
            "GET /health - Health check"
        ]
    }


@app.get("/health")
def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "openai_client": CLIENT is not None,
        "cached_datasets": len(DATASETS),
        "output_dir": str(config.OUTPUT_DIR)
    }


@app.post("/analyze", response_model=PlanResponse)
def analyze(request: AnalysisRequest):
    """
    Generate chart code from natural language question.
    
    This is the "planning" step - returns code without executing it.
    Enables human-in-the-loop review before execution.
    """
    if CLIENT is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        generator = ChartGenerator(CLIENT)
        plan = generator.generate_plan(request)
        
        logger.info(f"Generated plan for: {request.question}")
        return plan
    
    except ValidationError as e:
        logger.error(f"Response validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Response validation failed: {str(e)}")
    
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/critique", response_model=CritiqueResponse)
def critique(request: CritiqueRequest):
    """
    Critique generated code using reflection pattern.
    
    Provides structured feedback on code quality, domain relevance,
    and publication readiness.
    """
    if CLIENT is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        critic = CodeCritic(CLIENT)
        critique_result = critic.critique(request)
        
        logger.info(f"Critique quality: {critique_result.quality}")
        return critique_result
    
    except Exception as e:
        logger.error(f"Critique error: {e}")
        raise HTTPException(status_code=500, detail=f"Critique failed: {str(e)}")


@app.post("/execute", response_model=ExecutionResponse)
def execute(request: ExecutionRequest):
    """
    Execute chart code and generate plot.
    
    Returns path to generated image (PDF or PNG).
    Captures execution logs for debugging.
    """
    try:
        executor = CodeExecutor()
        result = executor.execute(request)
        
        if result.success:
            logger.info(f"Chart generated: {result.image_path}")
        else:
            logger.error(f"Execution failed: {result.error}")
        
        return result
    
    except Exception as e:
        logger.error(f"Execution error: {e}")
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@app.post("/insight", response_model=InsightResponse)
def generate_insight(request: InsightRequest):
    """
    Generate caption and insights for a plot.
    
    Uses LLM to describe the visualization and extract key findings.
    Suitable for publication-ready figure captions.
    """
    if CLIENT is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        generator = InsightGenerator(CLIENT)
        insight = generator.generate_insight(request)
        
        logger.info(f"Generated insight for: {request.analysis_title}")
        return insight
    
    except Exception as e:
        logger.error(f"Insight generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")


@app.get("/datasets")
def list_datasets():
    """List available datasets"""
    # Use config helper to get datasets
    datasets = config.get_available_datasets()
    
    # Add cache status
    for ds in datasets:
        ds["cached"] = ds["path"] in DATASETS
    
    return {
        "datasets": datasets,
        "total": len(datasets),
        "cached": len(DATASETS)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "chart_service:app",  # Import string for reload support
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD
    )
