"""
Pydantic schemas for Research Agent API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum


class ModelType(str, Enum):
    """Supported LLM models."""
    # Development/Testing (Fast & Economical)
    GPT_4O_MINI = "openai:gpt-4o-mini"
    GPT_5_CODEX_MINI = "openai:gpt-5.1-codex-mini"
    
    # Production (Balanced Quality)
    GPT_4O = "openai:gpt-4o"
    GPT_5 = "openai:gpt-5"
    O4_MINI = "openai:o4-mini"
    
    # Premium (Publication Quality)
    GPT_5_1 = "openai:gpt-5.1"
    GPT_5_1_CODEX = "openai:gpt-5.1-codex"
    GPT_5_PRO = "openai:gpt-5-pro"
    GPT_5_CODEX = "openai:gpt-5-codex"


class ReportLength(str, Enum):
    """Target report length options."""
    BRIEF = "brief"  # 2-3 pages
    STANDARD = "standard"  # 5-10 pages
    COMPREHENSIVE = "comprehensive"  # 15-25 pages
    TECHNICAL_PAPER = "technical-paper"  # 25-40 pages


class ModelChoice(str, Enum):
    """Available AI models for research report generation.
    
    Note: Ensure the model is configured in your aisuite setup.
    As of November 2025, the following models are available:
    """
    # OpenAI Models
    GPT4O = "openai:gpt-4o"
    GPT5 = "openai:gpt-5"
    O4_MINI = "openai:o4-mini"
    GPT_5_1 = "openai:gpt-5.1"
    GPT_5_1_CODEX = "openai:gpt-5.1-codex"
    GPT_5_PRO = "openai:gpt-5-pro"
    GPT_5_CODEX = "openai:gpt-5-codex"
    
    # Anthropic Claude Models (November 2025)
    # Latest: Claude Sonnet 4.5 (most intelligent, best for coding)
    # CLAUDE_SONNET_4_5 = "anthropic:claude-sonnet-4-5"
    # CLAUDE_OPUS_4_1 = "anthropic:claude-opus-4-1"
    # CLAUDE_SONNET_4 = "anthropic:claude-sonnet-4"
    # CLAUDE_OPUS_4 = "anthropic:claude-opus-4"
    # CLAUDE_SONNET_3_7 = "anthropic:claude-sonnet-3-7"  # Hybrid reasoning model
    
    # Google Gemini Models (November 2025)
    # Latest: Gemini 2.5 Flash (improved quality and efficiency)
    # GEMINI_2_5_FLASH = "google:gemini-2.5-flash"
    # GEMINI_2_5_FLASH_LITE = "google:gemini-2.5-flash-lite"
    # GEMINI_2_0_FLASH = "google:gemini-2.0-flash"
    # GEMINI_PRO_2_0 = "google:gemini-pro-2.0"


class ResearchRequest(BaseModel):
    """Request to generate a research report."""
    topic: str = Field(
        ...,
        min_length=5,
        description="Research topic to investigate"
    )
    model: ModelChoice = Field(
        default=ModelChoice.GPT4O,
        description="AI model to use"
    )
    report_length: ReportLength = Field(
        default=ReportLength.STANDARD,
        description="Target report length"
    )
    context: Optional[str] = Field(
        None,
        description="Additional context, style template, or constraints (e.g., 'Follow Nature Methods style', 'Focus on clinical applications'). Date ranges are auto-added if not specified."
    )
    generate_pdf: bool = Field(
        default=False,
        description="Also generate PDF version of the report"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "topic": "Recent advances in quantum error correction",
                    "model": "openai:gpt-4o-mini",
                    "context": "Focus on papers from 2024-2025"
                }
            ]
        }
    }


class ResearchResponse(BaseModel):
    """Response containing the generated research report."""
    success: bool
    topic: str
    report_path: str = Field(..., description="Path to the generated markdown report")
    pdf_path: Optional[str] = Field(None, description="Path to the generated PDF report (if requested)")
    report_content: str = Field(..., description="Full markdown content of the report")
    execution_history: List = Field(
        default_factory=list,
        description="History of agent executions - list of [step, output] tuples"
    )
    session_id: Optional[str] = Field(None, description="Session ID for progress tracking via SSE")
    error: Optional[str] = Field(None, description="Error message if generation failed")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "topic": "quantum_error_correction",
                    "report_path": "output/research_reports/quantum_error_correction/report_2025-11-21.md",
                    "report_content": "# Research Report: Quantum Error Correction\n\n## Introduction\n...",
                    "execution_history": [
                        {"step": "Search arXiv for papers", "agent": "research_agent", "result": "Found 15 papers..."}
                    ]
                }
            ]
        }
    }


class ReportListResponse(BaseModel):
    """Response containing list of available reports."""
    reports: List[Dict] = Field(
        default_factory=list,
        description="List of available research reports"
    )
    total: int = Field(..., description="Total number of reports")


class ReportViewResponse(BaseModel):
    """Response for viewing a specific report."""
    success: bool
    topic: str
    report_content: str
    created: float = Field(..., description="Creation timestamp")
    size_kb: float = Field(..., description="File size in kilobytes")
    download_url: str = Field(..., description="URL to download the markdown file")
    error: Optional[str] = None
