from . import agents

def generate_research_report(topic: str, model: str = "openai:gpt-4o") -> dict:
    """
    Orchestrates the full research workflow:
    1. Planner creates a plan.
    2. Executor runs the plan (delegating to sub-agents).
    
    Args:
        topic: Research topic.
        model: Model to use for agents (default gpt-4o).
        
    Returns:
        Dictionary containing the plan and the execution history.
    """
    print(f"\n🚀 Starting Research Workflow for: '{topic}'")
    print(f"Using model: {model}")
    
    # 1. Plan
    # Note: Planner typically uses reasoning model (o4-mini), but we can allow override or default.
    # The notebook used o4-mini for planning.
    planner_model = "openai:o4-mini" if model.startswith("openai") else model
    
    steps = agents.planner_agent(topic, model=planner_model)
    print(f"\n📋 Plan generated ({len(steps)} steps)")
    for i, step in enumerate(steps):
        print(f"  {i+1}. {step}")
        
    if not steps:
        return {"error": "Failed to generate plan"}
        
    # 2. Execute
    history = agents.executor_agent(steps, model=model)
    
    # Extract final report if possible (usually the last step)
    final_output = history[-1][-1] if history else ""
    
    return {
        "topic": topic,
        "plan": steps,
        "history": history,
        "final_report": final_output
    }
