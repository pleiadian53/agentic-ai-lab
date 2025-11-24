"""
FastAPI service for Research Agent - Multi-agent research report generation.

Provides endpoints for:
- Generating research reports from topics
- Viewing generated reports in HTML
- Downloading reports as markdown
- Listing available reports
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import markdown
import aisuite

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from multiagent.research_agent.server.schemas import (
    ResearchRequest,
    ResearchResponse,
    ReportListResponse,
    ReportViewResponse
)
from multiagent.research_agent.server import config
from multiagent.research_agent import pipeline
from multiagent.research_agent import manifest as manifest_module
from multiagent.research_agent import slug_utils
from multiagent.research_agent import pdf_utils

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
CLIENT: Optional[aisuite.Client] = None

# Templates
templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))

# Add custom Jinja2 filter for timestamp formatting
def timestamp_to_date(timestamp: float) -> str:
    """Convert Unix timestamp to readable date string."""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')

templates.env.filters['timestamp_to_date'] = timestamp_to_date


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    global CLIENT
    
    # Startup
    logger.info("Starting Research Agent API...")
    
    # Initialize aisuite client
    CLIENT = aisuite.Client()
    logger.info("✓ AISuite client initialized")
    
    # Log configuration
    logger.info(f"✓ Project root: {config.PROJECT_ROOT}")
    logger.info(f"✓ Output directory: {config.OUTPUT_DIR}")
    logger.info(f"✓ Templates directory: {config.TEMPLATES_DIR}")
    
    logger.info("Research Agent API ready!")
    
    yield
    
    # Shutdown (cleanup if needed)
    logger.info("Shutting down Research Agent API...")


# Initialize FastAPI with lifespan
app = FastAPI(
    title="Research Agent API",
    description="Multi-agent research report generation service",
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

# Mount static files
app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - show available reports and generation form."""
    reports = config.get_available_reports()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "reports": reports,
            "total_reports": len(reports)
        }
    )


@app.post("/api/generate", response_model=ResearchResponse)
async def generate_report(request: ResearchRequest):
    """
    Generate a research report on the given topic.
    
    This endpoint:
    1. Creates a research plan using the Planner Agent
    2. Executes the plan using the Executor Agent (which routes to Research, Writer, Editor agents)
    3. Saves the final report to disk
    4. Returns the report content and metadata
    """
    try:
        logger.info(f"Generating research report for topic: {request.topic}")
        
        # Generate smart slug using LLM
        logger.info("Generating topic slug...")
        topic_slug = slug_utils.generate_topic_slug(request.topic, max_length=50)
        logger.info(f"Topic slug: {topic_slug}")
        
        # Track generation time
        import time
        start_time = time.time()
        
        # Generate report using pipeline
        result = pipeline.generate_research_report(
            topic=request.topic,
            model=request.model.value,
            report_length=request.report_length.value,
            context=request.context,
            client=CLIENT
        )
        
        generation_time = time.time() - start_time
        
        # Save report to file
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
        report_filename = f"report_{timestamp}.md"
        report_path = config.get_output_path(topic_slug, report_filename)
        
        with open(report_path, 'w') as f:
            f.write(result["final_report"])
        
        # Generate PDF if requested
        pdf_filename = None
        if request.generate_pdf:
            logger.info("Generating PDF...")
            pdf_path = report_path.with_suffix('.pdf')
            success, error = pdf_utils.markdown_to_pdf(
                result["final_report"],
                pdf_path,
                title=request.topic
            )
            if success:
                pdf_filename = pdf_path.name
                logger.info(f"✓ PDF saved to: {pdf_path}")
            else:
                logger.warning(f"⚠️  PDF generation failed: {error}")
        
        # Create manifest entry
        topic_dir = report_path.parent
        plan_steps = len(result.get("plan", []))
        manifest_module.create_manifest_entry(
            topic_dir=topic_dir,
            filename=report_filename,
            topic=request.topic,
            model=request.model.value,
            report_length=request.report_length.value,
            context=request.context,
            source="web",
            report_content=result["final_report"],
            generation_time_seconds=round(generation_time, 2),
            plan_steps=plan_steps,
            pdf_filename=pdf_filename
        )
        
        logger.info(f"✓ Report saved to: {report_path}")
        if pdf_filename:
            logger.info(f"✓ PDF saved: {pdf_path}")
        logger.info(f"✓ Manifest updated: {topic_dir / 'manifest.json'}")
        
        return ResearchResponse(
            success=True,
            topic=topic_slug,
            report_path=str(report_path),
            report_content=result["final_report"],
            execution_history=result.get("history", [])
        )
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports", response_model=ReportListResponse)
async def list_reports():
    """List all available research reports."""
    reports = config.get_available_reports()
    return ReportListResponse(
        reports=reports,
        total=len(reports)
    )


@app.get("/api/reports/{topic}/{filename}", response_model=ReportViewResponse)
async def get_report(topic: str, filename: str):
    """Get a specific report by topic and filename."""
    try:
        report_path = config.OUTPUT_DIR / topic / filename
        
        if not report_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        with open(report_path, 'r') as f:
            content = f.read()
        
        stat = report_path.stat()
        
        return ReportViewResponse(
            success=True,
            topic=topic,
            report_content=content,
            created=stat.st_mtime,
            size_kb=stat.st_size / 1024,
            download_url=f"/download/{topic}/{filename}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/view/{topic}/{filename}", response_class=HTMLResponse)
async def view_report(request: Request, topic: str, filename: str):
    """View a report in HTML format with nice styling."""
    try:
        report_path = config.OUTPUT_DIR / topic / filename
        
        if not report_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        with open(report_path, 'r') as f:
            markdown_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['extra', 'codehilite', 'toc']
        )
        
        stat = report_path.stat()
        created_date = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        
        return templates.TemplateResponse(
            "report.html",
            {
                "request": request,
                "topic": topic.replace("_", " ").title(),
                "filename": filename,
                "html_content": html_content,
                "created_date": created_date,
                "size_kb": f"{stat.st_size / 1024:.2f}",
                "download_url": f"/download/{topic}/{filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error viewing report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{topic}/{filename}")
async def download_report(topic: str, filename: str):
    """Download a report as a markdown file."""
    try:
        report_path = config.OUTPUT_DIR / topic / filename
        
        if not report_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        return FileResponse(
            path=report_path,
            media_type="text/markdown",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Research Agent API",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "research_service:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD
    )
