from . import agents
from . import context_utils
from . import format_decision

def generate_research_report(topic: str, model: str = "openai:gpt-4o", report_length: str = "standard", context: str = None, client=None, user_format: str = None) -> dict:
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
        
    Returns:
        Dictionary containing the plan, execution history, and format decision.
    """
    print(f"\n🚀 Starting Research Workflow for: '{topic}'")
    print(f"Using model: {model}")
    print(f"Target length: {report_length}")
    
    # Step 0: Decide output format
    format_info = format_decision.decide_output_format(
        topic=topic,
        model=model,
        user_preference=user_format
    )
    print(f"\n📄 Output Format: {format_info['format'].upper()}")
    print(f"💭 Reason: {format_info['reasoning']}")
    
    # Enhance context with smart date ranges if not specified
    enhanced_context = context_utils.enhance_context_with_dates(context)
    if enhanced_context != context:
        print(f"📅 Auto-added date range: {context_utils.get_smart_date_range()}")
    
    # 1. Plan
    # Note: Planner typically uses reasoning model (o4-mini), but we can allow override or default.
    # The notebook used o4-mini for planning.
    planner_model = "openai:o4-mini" if model.startswith("openai") else model
    
    steps = agents.planner_agent(topic, model=planner_model, report_length=report_length, context=enhanced_context)
    print(f"\n📋 Plan generated ({len(steps)} steps)")
    for i, step in enumerate(steps):
        print(f"  {i+1}. {step}")
        
    if not steps:
        return {"error": "Failed to generate plan"}
        
    # 2. Execute
    # Get format-specific instructions for writer agent
    format_instructions = format_decision.get_writer_instructions(format_info)
    history = agents.executor_agent(steps, model=model, format_instructions=format_instructions)
    
    # Extract final report if possible (usually the last step)
    final_output = history[-1][-1] if history else ""
    
    return {
        "topic": topic,
        "plan": steps,
        "history": history,
        "final_report": final_output,
        "format_decision": format_info  # Track format decision in output
    }
