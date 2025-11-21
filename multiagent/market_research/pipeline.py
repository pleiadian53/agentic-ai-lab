"""Pipeline orchestration for market research campaign generation.

This module implements the linear/sequential communication pattern
where agents execute in a fixed order, each passing its output to
the next agent in the pipeline.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any

import aisuite

from .agents import (
    market_research_agent,
    graphic_designer_agent,
    copywriter_agent,
    packaging_agent,
)


def run_campaign_pipeline(
    client: aisuite.Client | None = None,
    model: str = "gpt-4o-mini",
    output_path: str | None = None,
    output_dir: str | None = None,
    topic: str = "sunglasses_campaign",
    verbose: bool = True
) -> dict[str, Any]:
    """Run the full summer sunglasses campaign pipeline.
    
    This function orchestrates a linear/sequential multi-agent workflow:
    1. Market Research Agent - Scans trends and matches products
    2. Graphic Designer Agent - Generates campaign visual
    3. Copywriter Agent - Creates marketing quote with multimodal analysis
    4. Packaging Agent - Assembles executive-ready markdown report
    
    Communication Pattern:
        Linear/Sequential - Each agent's output becomes the next agent's input
        
    Args:
        client: aisuite Client instance (creates new if None)
        model: Model to use for agents (default: gpt-4o-mini)
        output_path: Full path for final report (overrides output_dir/topic if provided)
        output_dir: Base output directory (default: output/)
        topic: Topic subdirectory name (default: sunglasses_campaign)
        verbose: If True, print progress updates
        
    Returns:
        Dictionary containing:
            - trend_summary: Market research analysis
            - visual: Dict with image_path, prompt, caption
            - quote_result: Dict with quote, justification
            - markdown_path: Path to final report
            - output_directory: Directory where outputs were saved
            
    Example:
        >>> import aisuite
        >>> from market_research import run_campaign_pipeline
        >>> 
        >>> client = aisuite.Client()
        >>> results = run_campaign_pipeline(client=client, topic="summer_2025")
        >>> print(f"Report: {results['markdown_path']}")
        >>> print(f"Output dir: {results['output_directory']}")
    """
    # Initialize client if not provided
    if client is None:
        client = aisuite.Client()
    
    # Set up output directory structure
    if output_path is None:
        # Use output_dir or default to 'output/'
        if output_dir is None:
            output_dir = "output"
        
        # Create topic subdirectory
        topic_dir = Path(output_dir) / topic
        topic_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
        output_path = str(topic_dir / f"campaign_summary_{timestamp}.md")
    else:
        # If full path provided, ensure parent directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path = str(output_path)
        topic_dir = output_path.parent
    
    if verbose:
        print("\n" + "=" * 60)
        print("🚀 STARTING CAMPAIGN PIPELINE")
        print("=" * 60)
        print(f"Model: {model}")
        print(f"Output: {output_path}")
    
    # Step 1: Market Research Agent
    if verbose:
        print("\n📍 Step 1/4: Market Research")
    
    trend_summary = market_research_agent(
        client=client,
        model=model,
        verbose=verbose
    )
    
    if verbose:
        print("✅ Market research completed")
    
    # Step 2: Graphic Designer Agent
    if verbose:
        print("\n📍 Step 2/4: Visual Generation")
    
    visual_result = graphic_designer_agent(
        client=client,
        trend_insights=trend_summary,
        model=model,
        output_dir=str(topic_dir),  # Save image in same directory
        verbose=verbose
    )
    image_path = visual_result["image_path"]
    
    if verbose:
        print("✅ Image generated")
    
    # Step 3: Copywriter Agent
    if verbose:
        print("\n📍 Step 3/4: Copywriting")
    
    quote_result = copywriter_agent(
        client=client,
        image_path=image_path,
        trend_summary=trend_summary,
        model=model,
        verbose=verbose
    )
    quote = quote_result.get("quote", "")
    justification = quote_result.get("justification", "")
    
    if verbose:
        print("✅ Quote created")
    
    # Step 4: Packaging Agent
    if verbose:
        print("\n📍 Step 4/4: Report Generation")
    
    md_path = packaging_agent(
        client=client,
        trend_summary=trend_summary,
        image_url=image_path,
        quote=quote,
        justification=justification,
        output_path=output_path,
        model=model,
        verbose=verbose
    )
    
    if verbose:
        print("\n" + "=" * 60)
        print("🎉 PIPELINE COMPLETE")
        print("=" * 60)
        print(f"📦 Report: {md_path}")
        print(f"🖼️  Image: {image_path}")
        print(f"💬 Quote: {quote}")
    
    return {
        "trend_summary": trend_summary,
        "visual": visual_result,
        "quote_result": quote_result,
        "markdown_path": md_path,
        "output_directory": str(topic_dir)
    }
