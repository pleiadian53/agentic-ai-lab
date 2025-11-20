"""Splice Agent API - FastAPI service for splice site analysis.

This service extends the Chart Agent API with splice-specific endpoints and analysis templates.
It provides:
- Predefined splice site analysis templates
- Custom exploratory analysis
- Domain-specific visualizations
- Biological insight generation

Built on FastAPI with OpenAI integration for code generation.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field

from splice_agent.data_access import create_dataset
from splice_agent.splice_analysis import (
    ANALYSIS_TEMPLATES,
    generate_analysis_insight,
    generate_exploratory_insight,
    get_all_analysis_descriptions,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output" / "splice_charts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Dataset cache
dataset_cache: Dict = {}


# =========================
# Pydantic Schemas
# =========================

class AnalysisType(BaseModel):
    """Available analysis type."""
    type: str
    title: str
    description: str


class TemplateAnalysisRequest(BaseModel):
    """Request for template-based analysis."""
    dataset_path: str = Field(
        ...,
        description="Path to splice site dataset",
        examples=["data/splice_sites_enhanced.tsv"]
    )
    analysis_type: str = Field(
        ...,
        description="Type of analysis template to use",
        examples=["high_alternative_splicing", "splice_site_genomic_view"]
    )
    model: str = Field(
        "gpt-4o-mini",
        description="LLM model to use"
    )
    standard_only: bool = Field(
        True,
        description="Filter to standard chromosomes only"
    )


class ExploratoryAnalysisRequest(BaseModel):
    """Request for exploratory analysis."""
    dataset_path: str = Field(
        ...,
        description="Path to splice site dataset",
        examples=["data/splice_sites_enhanced.tsv"]
    )
    research_question: str = Field(
        ...,
        description="Custom research question",
        examples=["What is the relationship between gene length and splice site density?"]
    )
    model: str = Field(
        "gpt-4o-mini",
        description="LLM model to use"
    )


class AnalysisResponse(BaseModel):
    """Response from analysis."""
    title: str
    description: str
    code: str
    library: str
    chart_type: str
    model_used: str


class ExploratoryResponse(BaseModel):
    """Response from exploratory analysis."""
    code: str
    reasoning: str
    key_insights: List[str]
    library: str
    chart_type: str
    model_used: str


# =========================
# Lifespan Management
# =========================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup/shutdown)."""
    # Startup
    logger.info("Starting Splice Agent API...")
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    
    # Verify OpenAI API key
    import os
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not set - API calls will fail")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Splice Agent API...")
    # Close any cached datasets
    for dataset in dataset_cache.values():
        try:
            dataset.close()
        except:
            pass
    dataset_cache.clear()


# =========================
# FastAPI App
# =========================

app = FastAPI(
    title="Splice Agent API",
    description="AI-powered splice site analysis and visualization",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated charts
app.mount("/charts", StaticFiles(directory=str(OUTPUT_DIR)), name="charts")


# =========================
# Helper Functions
# =========================

def get_dataset(dataset_path: str):
    """Get dataset from cache or load it."""
    if dataset_path not in dataset_cache:
        full_path = PROJECT_ROOT / dataset_path
        if not full_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Dataset not found: {dataset_path}"
            )
        dataset_cache[dataset_path] = create_dataset(str(full_path))
    return dataset_cache[dataset_path]


def get_openai_client() -> OpenAI:
    """Get OpenAI client."""
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY not configured"
        )
    return OpenAI(api_key=api_key)


# =========================
# Endpoints
# =========================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Splice Agent API",
        "version": "0.1.0",
        "description": "AI-powered splice site analysis",
        "docs": "/docs",
        "endpoints": {
            "analyses": "/analyses",
            "analyze_template": "/analyze/template",
            "analyze_exploratory": "/analyze/exploratory",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "data_dir": str(DATA_DIR),
        "output_dir": str(OUTPUT_DIR),
        "cached_datasets": len(dataset_cache)
    }


@app.get("/analyses", response_model=List[AnalysisType])
async def list_analyses():
    """List available analysis templates."""
    return get_all_analysis_descriptions()


@app.post("/analyze/template", response_model=AnalysisResponse)
async def analyze_template(request: TemplateAnalysisRequest):
    """Generate analysis using predefined template.
    
    This endpoint uses domain-specific analysis templates optimized for
    splice site biology. Templates include:
    - high_alternative_splicing: Genes with most splice sites
    - splice_site_genomic_view: Chromosome distribution
    - exon_complexity: Transcript structure analysis
    - strand_bias: Strand distribution analysis
    - gene_transcript_diversity: Transcript isoform analysis
    """
    try:
        # Validate analysis type
        if request.analysis_type not in ANALYSIS_TEMPLATES:
            available = list(ANALYSIS_TEMPLATES.keys())
            raise HTTPException(
                status_code=400,
                detail=f"Invalid analysis type. Available: {available}"
            )
        
        # Get dataset
        dataset = get_dataset(request.dataset_path)
        
        # Get OpenAI client
        client = get_openai_client()
        
        # Generate analysis
        logger.info(f"Generating {request.analysis_type} analysis...")
        result = generate_analysis_insight(
            dataset=dataset,
            analysis_type=request.analysis_type,
            client=client,
            model=request.model,
            standard_only=request.standard_only
        )
        
        return AnalysisResponse(
            title=result["title"],
            description=result["description"],
            code=result["chart_code"],
            library=result["library"],
            chart_type=result["chart_type"],
            model_used=result["model_used"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/analyze/exploratory", response_model=ExploratoryResponse)
async def analyze_exploratory(request: ExploratoryAnalysisRequest):
    """Generate exploratory analysis for custom research questions.
    
    This endpoint allows you to ask custom research questions about splice sites.
    The LLM will generate appropriate visualizations based on domain context.
    
    Example questions:
    - "What is the relationship between gene length and splice site density?"
    - "How do splice sites distribute across different gene biotypes?"
    - "Which chromosomes have the highest alternative splicing rates?"
    """
    try:
        # Get dataset
        dataset = get_dataset(request.dataset_path)
        
        # Get OpenAI client
        client = get_openai_client()
        
        # Generate exploratory analysis
        logger.info(f"Generating exploratory analysis: {request.research_question[:50]}...")
        result = generate_exploratory_insight(
            dataset=dataset,
            research_question=request.research_question,
            client=client,
            model=request.model
        )
        
        return ExploratoryResponse(
            code=result["chart_code"],
            reasoning=result["reasoning"],
            key_insights=result["key_insights"],
            library=result["library"],
            chart_type=result["chart_type"],
            model_used=result["model_used"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exploratory analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


# =========================
# Main
# =========================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "splice_service:app",
        host="0.0.0.0",
        port=8004,  # Different port from chart_agent
        reload=True
    )
