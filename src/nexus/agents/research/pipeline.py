from . import agents
from . import context_utils
from . import format_decision
from .progress import ProgressTracker, ProgressStage, AgentType
from typing import Optional

def generate_research_report(
    topic: str, 
    model: str = "openai:gpt-4o", 
    report_length: str = "standard", 
    context: str = None, 
    client=None, 
    user_format: str = None, 
    verbose: bool = True,
    progress_tracker: Optional[ProgressTracker] = None
) -> dict:
    """
    Orchestrates the full research workflow:
    1. Decide output format (PDF/LaTeX/Markdown)
    2. Planner creates a plan.
    3. Executor runs the plan (delegating to sub-agents).
    
    Args:
        topic: Research topic.
        model: Model to use for agents (default gpt-4o).
        report_length: Target report length - "brief", "standard", "comprehensive", or "technical-paper"
        context: Additional context or style template guidance
        client: Optional aisuite client (for web service compatibility)
        user_format: Optional user override for format ("pdf_direct", "latex", "markdown")
        verbose: Show detailed progress (default True)
        
    Returns:
        Dictionary containing the plan, execution history, and format decision.
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"🚀 NEXUS RESEARCH AGENT")
        print(f"{'='*70}")
        print(f"📌 Topic: {topic}")
        print(f"🤖 Model: {model}")
        print(f"📏 Length: {report_length}")
        if context:
            print(f"📝 Context: {context[:100]}..." if len(context) > 100 else f"📝 Context: {context}")
        print(f"{'='*70}\n")
    
    # Progress tracking
    if progress_tracker:
        progress_tracker.update(ProgressStage.INITIALIZING, "Starting research workflow...")
    
    # Step 0: Decide output format
    format_info = format_decision.decide_output_format(
        topic=topic,
        model=model,
        user_preference=user_format
    )
    if progress_tracker:
        progress_tracker.update(ProgressStage.FORMAT_DECISION, "Deciding output format...")
    
    if verbose:
        print(f"\n{'─'*70}")
        print(f"📄 STEP 1: FORMAT DECISION")
        print(f"{'─'*70}")
        print(f"Format: {format_info['format'].upper()}")
        print(f"Reason: {format_info['reasoning']}\n")
    
    # Enhance context with smart date ranges if not specified
    enhanced_context = context_utils.enhance_context_with_dates(context)
    if enhanced_context != context and verbose:
        print(f"📅 Auto-added date range: {context_utils.get_smart_date_range()}")
    
    # 1. Plan
    if progress_tracker:
        progress_tracker.update(ProgressStage.PLANNING, "Creating research plan...")
    
    if verbose:
        print(f"\n{'─'*70}")
        print(f"📋 STEP 2: PLANNING")
        print(f"{'─'*70}")
    
    # Note: Planner typically uses reasoning model (o4-mini), but we can allow override or default.
    # The notebook used o4-mini for planning.
    planner_model = "openai:o4-mini" if model.startswith("openai") else model
    
    if verbose:
        print(f"🤖 Using planner model: {planner_model}")
        print(f"⏳ Generating research plan...\n")
    
    steps = agents.planner_agent(topic, model=planner_model, report_length=report_length, context=enhanced_context)
    
    if verbose:
        print(f"\n✅ Plan generated ({len(steps)} steps):")
        for i, step in enumerate(steps):
            print(f"  {i+1}. {step}")
        
    if not steps:
        return {"error": "Failed to generate plan"}
        
    # 2. Execute
    if progress_tracker:
        progress_tracker.update(ProgressStage.EXECUTING, f"Executing {len(steps)} research steps...")
    
    if verbose:
        print(f"\n{'─'*70}")
        print(f"⚙️  STEP 3: EXECUTION")
        print(f"{'─'*70}")
        print(f"⏳ Executing {len(steps)} research steps...")
        print(f"💡 This may take 5-10 minutes depending on complexity\n")
    
    # Get format-specific instructions for writer agent
    format_instructions = format_decision.get_writer_instructions(format_info)
    history = agents.executor_agent(
        steps, 
        model=model, 
        format_instructions=format_instructions, 
        verbose=verbose,
        progress_tracker=progress_tracker
    )
    
    # Extract final report if possible (usually the last step)
    final_output = history[-1][-1] if history else ""
    
    # Validate and fix output if needed
    from . import output_validator
    validated_output, warnings = output_validator.validate_and_fix_report(
        final_output, 
        topic, 
        auto_fix=True
    )
    
    # Log any warnings
    if warnings:
        if verbose:
            print(f"\n{'─'*70}")
            print("⚠️  OUTPUT VALIDATION")
            print(f"{'─'*70}")
            for warning in warnings:
                print(f"   {warning}")
            print()
    
    return {
        "topic": topic,
        "plan": steps,
        "history": history,
        "final_report": validated_output,
        "validation_warnings": warnings,  # Track validation issues
        "format_decision": format_info  # Track format decision in output
    }
