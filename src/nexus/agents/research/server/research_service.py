"""
FastAPI service for Research Agent - Multi-agent research report generation.

Provides endpoints for:
- Generating research reports from topics
- Viewing generated reports in HTML
- Downloading reports as markdown
- Listing available reports
"""

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from queue import Queue
import asyncio
import json
import uuid
import markdown
import aisuite

from nexus.agents.research.server.schemas import (
    ResearchRequest,
    ResearchResponse,
    ReportListResponse,
    ReportViewResponse
)
from nexus.agents.research.server import config
from nexus.agents.research import pipeline
from nexus.agents.research import manifest as manifest_module
from nexus.agents.research import slug_utils
from nexus.agents.research import pdf_utils
from nexus.agents.research.progress import ProgressTracker, ProgressUpdate, ProgressStage

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
CLIENT: Optional[aisuite.Client] = None

# Progress tracking - stores queues for active generation sessions
progress_queues: Dict[str, Queue] = {}

# Generation results - stores completed generation results
generation_results: Dict[str, dict] = {}

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


@app.get("/api/progress/{session_id}")
async def progress_stream(session_id: str):
    """
    Server-Sent Events endpoint for real-time progress updates.
    
    Client connects to this endpoint and receives progress updates
    as they happen during report generation.
    """
    async def event_generator():
        queue = progress_queues.get(session_id)
        if not queue:
            yield f"data: {json.dumps({'error': 'Session not found', 'stage': 'error'})}\n\n"
            return
        
        try:
            while True:
                # Check for new progress updates
                if not queue.empty():
                    update: ProgressUpdate = queue.get()
                    yield f"data: {json.dumps(update.to_dict())}\n\n"
                    
                    # If complete or error, close stream
                    if update.stage in [ProgressStage.COMPLETE, ProgressStage.ERROR]:
                        break
                
                await asyncio.sleep(0.1)  # Poll every 100ms
        except asyncio.CancelledError:
            # Client disconnected
            logger.info(f"Client disconnected from progress stream: {session_id}")
        finally:
            # Cleanup
            if session_id in progress_queues:
                del progress_queues[session_id]
                logger.info(f"Cleaned up progress queue for session: {session_id}")
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


def run_generation_task(session_id: str, request: ResearchRequest):
    """
    Background task to generate a research report.
    Runs in a separate thread to allow SSE streaming.
    """
    try:
        logger.info(f"Starting background generation for session: {session_id}")
        
        # Get the progress queue
        progress_queue = progress_queues[session_id]
        
        def progress_callback(update: ProgressUpdate):
            """Callback to push progress updates to the queue."""
            progress_queue.put(update)
        
        tracker = ProgressTracker(callback=progress_callback)
        
        # Track generation time
        import time
        start_time = time.time()
        
        # Generate report using pipeline with progress tracking
        result = pipeline.generate_research_report(
            topic=request.topic,
            model=request.model.value,
            report_length=request.report_length.value,
            context=request.context,
            client=CLIENT,
            verbose=False,  # Disable console output for web
            progress_tracker=tracker
        )
        
        generation_time = time.time() - start_time
        
        # Generate smart slug using LLM
        tracker.update(ProgressStage.GENERATING_SLUG, "Generating topic slug...")
        logger.info("Generating topic slug...")
        topic_slug = slug_utils.generate_topic_slug(request.topic, max_length=50)
        logger.info(f"Topic slug:")
        
        # Save report to file
        tracker.update(ProgressStage.SAVING, "Saving report...")
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
        
        # Use appropriate file extension based on format
        format_info = result.get("format_decision", {})
        output_format = format_info.get("format", "markdown")
        file_extension = ".tex" if output_format == "latex" else ".md"
        report_filename = f"report_{timestamp}{file_extension}"
        report_path = config.get_output_path(topic_slug, report_filename)
        
        with open(report_path, 'w') as f:
            f.write(result["final_report"])
        
        # Generate PDF if requested
        pdf_filename = None
        markdown_preview_filename = None
        if request.generate_pdf:
            logger.info("Generating PDF...")
            pdf_path = report_path.with_suffix('.pdf')
            
            # Check if content is LaTeX or Markdown
            content = result["final_report"]
            is_latex = '\\documentclass' in content or '\\begin{document}' in content
            
            if is_latex:
                logger.info("Detected LaTeX format, using LaTeX compiler...")
                success, error = pdf_utils.latex_to_pdf(
                    content,
                    pdf_path,
                    title=request.topic
                )
                
                # Also generate Markdown preview for GitHub
                if success:
                    logger.info("Generating Markdown preview for GitHub...")
                    from .. import pandoc_converter
                    md_preview_path = report_path.with_suffix('.md')
                    
                    # Try Pandoc first, fallback to custom converter
                    success_md, method = pandoc_converter.generate_markdown_preview(
                        content, md_preview_path, prefer_pandoc=True
                    )
                    
                    if success_md:
                        markdown_preview_filename = md_preview_path.name
                        converter_name = "Pandoc" if method == "pandoc" else "custom converter"
                        logger.info(f"✓ Markdown preview saved: {md_preview_path} (using {converter_name})")
                    else:
                        logger.warning("⚠️  Markdown preview generation failed")
            else:
                logger.info("Detected Markdown format, using markdown converter...")
                success, error = pdf_utils.markdown_to_pdf(
                    content,
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
            pdf_filename=pdf_filename,
            format_decision=format_info  # Track format decision
        )
        
        logger.info(f"✓ Report saved to: {report_path}")
        if pdf_filename:
            logger.info(f"✓ PDF saved: {pdf_path}")
        logger.info(f"✓ Manifest updated: {topic_dir / 'manifest.json'}")
        
        # Mark as complete
        tracker.complete(f"Report generation complete! Saved to {topic_slug}")
        
        # Store result for later retrieval
        generation_results[session_id] = {
            "success": True,
            "topic": topic_slug,
            "report_path": str(report_path),
            "pdf_path": str(pdf_path) if pdf_filename else None,
            "report_content": result["final_report"],
            "execution_history": result.get("history", [])
        }
        
        logger.info(f"✓ Generation complete for session: {session_id}")
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        # Report error to progress tracker
        if session_id in progress_queues:
            tracker = ProgressTracker(callback=lambda u: progress_queues[session_id].put(u))
            tracker.error(str(e))
        # Store error result
        generation_results[session_id] = {
            "success": False,
            "error": str(e)
        }


@app.post("/api/generate", response_model=ResearchResponse)
async def generate_report(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    Start a research report generation in the background.
    Returns immediately with a session_id for progress tracking via SSE.
    """
    # Generate session ID for progress tracking
    session_id = str(uuid.uuid4())
    
    logger.info(f"Starting research report generation for topic: {request.topic} (session: {session_id})")
    
    # Create progress queue
    progress_queue = Queue()
    progress_queues[session_id] = progress_queue
    
    # Start background task
    background_tasks.add_task(run_generation_task, session_id, request)
    
    # Return immediately with session_id
    return ResearchResponse(
        success=True,
        topic=request.topic,
        report_path="",  # Will be filled when complete
        pdf_path=None,
        report_content="",  # Will be filled when complete
        execution_history=[],
        session_id=session_id
    )


@app.get("/api/result/{session_id}")
async def get_result(session_id: str):
    """Get the final result of a generation session."""
    if session_id not in generation_results:
        raise HTTPException(status_code=404, detail="Session not found or still in progress")
    
    result = generation_results[session_id]
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Generation failed"))
    
    return result


@app.get("/download/{topic}/{filename}")
async def download_report(topic: str, filename: str):
    """Download a report file (forces download instead of inline view)."""
    try:
        report_path = config.OUTPUT_DIR / topic / filename
        
        if not report_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Force download with attachment disposition
        return FileResponse(
            report_path,
            media_type="application/pdf" if filename.endswith('.pdf') else "text/markdown",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
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


@app.get("/view/{topic}/{filename}")
async def view_report(request: Request, topic: str, filename: str):
    """View a report - serves PDF directly or renders markdown as HTML."""
    try:
        report_path = config.OUTPUT_DIR / topic / filename
        
        if not report_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        # If it's a PDF, serve it for inline viewing (not download)
        if filename.endswith('.pdf'):
            return FileResponse(
                report_path,
                media_type="application/pdf",
                headers={"Content-Disposition": f"inline; filename={filename}"}
            )
        
        # For markdown files, render as HTML
        with open(report_path, 'r', encoding='utf-8') as f:
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
