import json
import ast
from datetime import datetime
from aisuite import Client

from . import tools
from . import utils
from . import llm_client

# Shared client for aisuite calls
client = Client()

def planner_agent(topic: str, model: str = "openai:o4-mini") -> list[str]:
    """
    Generates a plan as a Python list of steps.
    """
    print("==================================")
    print("🧠 Planner Agent")
    print("==================================")
    
    prompt = f"""
You are a senior research strategist orchestrating a team of specialized agents.

🎯 Your task:
Generate a valid Python list of strings, where each string is one atomic step in a multi-agent research workflow on the topic:
"{topic}"

No commentary, no markdown, no surrounding backticks — only a plain Python list.

---

🧠 Available agents and what they can do:

1. **Research Agent**
   - Tools: arXiv, PubMed/Europe PMC, Tavily web search, Wikipedia
   - Capabilities: Search for papers, collect data, extract findings, compare sources, review literature, synthesize insights
   - Example verbs: "Search", "Find", "Investigate", "Collect", "Extract", "Compare", "Review", "Synthesize", "Analyze"

2. **Writer Agent**
   - Produces structured academic text: introduction, background, findings, analysis, conclusion
   - Capabilities: Draft sections, compose narratives, outline structure, expand ideas
   - Example verbs: "Draft", "Write", "Compose", "Outline", "Expand", "Develop", "Articulate"

3. **Editor Agent**
   - Improves clarity, tone, structure, correctness
   - Capabilities: Refine prose, improve clarity, restructure content, ensure accuracy
   - Example verbs: "Edit", "Refine", "Polish", "Revise", "Improve", "Enhance", "Clarify"

---

📌 Requirements for each step:
- **Atomic** → one action, one verb, one agent
- **Executable** → must clearly map to one of the above agents
- **Concrete** → specify the source or output ("Search arXiv for X", "Draft introduction section")
- **Sequenced** → broad → focused → synthesis → writing → editing
- **Complete** → include all phases: literature search, filtering, synthesis, drafting, editing, final report

📌 Step formatting:
- Each element is a **string** describing one action
- Each string should start with an action verb (see examples above)
- No compound steps with connectors ("and", "then", "followed by")
- Avoid infrastructure tasks (code, repos, datasets)
- Avoid meta instructions ("think about", "consider", "reflect on")

---

📌 Recommended structure:
1. Broad literature search (multiple sources)
2. Narrowed academic search (specific aspects)
3. Complementary web/encyclopedic search (context, definitions)
4. Extraction/summarization steps (key findings)
5. Synthesis/insights (cross-reference, compare)
6. Writing steps (multiple sections: intro, findings, analysis, conclusion)
7. Editing/refinement (clarity, structure, accuracy)
8. Final Markdown report generation

---

� Output:
Return ONLY a Python list of strings.

Example format (do NOT repeat this example, just follow the structure):
[
  "Search arXiv for foundational papers on quantum computing",
  "Search Europe PMC for clinical applications of quantum computing",
  "Extract key findings from collected papers",
  "Draft introduction section",
  "Edit introduction for clarity",
  "Generate final Markdown research report"
]

Now generate the plan for: "{topic}"
"""
    messages = [{"role": "user", "content": prompt}]
    
    # Use unified client (supports Responses API)
    content = llm_client.call_llm_text(client, model, messages, temperature=1.0)
    
    try:
        # Clean markdown blocks if present
        content = utils.clean_json_block(content)
        
        # Parse list safely
        steps = ast.literal_eval(content)
        if not isinstance(steps, list):
            raise ValueError("Output is not a list")
            
        return steps
    except Exception as e:
        print(f"❌ Planner Error: {e}")
        return []

def research_agent(task: str, model: str = "openai:gpt-4o", return_messages: bool = False) -> str | tuple[str, list]:
    """
    Executes a research task using tools.
    Delegates to llm_client.call_llm_with_tools for API compatibility.
    """
    print("==================================")
    print("🔍 Research Agent")
    print("==================================")

    prompt = f"""
You are an expert research analyst with access to cutting-edge academic and web search tools.

🔬 Your capabilities:
- **arxiv_search_tool**: Access to 2M+ papers in physics, CS, math, and related fields
- **europe_pmc_search_tool**: Comprehensive biomedical literature (PubMed, bioRxiv, medRxiv, preprints)
- **tavily_search_tool**: Real-time web search for current events, news, and general information
- **wikipedia_search_tool**: Encyclopedic knowledge for background context and definitions

🎯 Your mission:
{task}

📋 Best practices:
- Use multiple tools to cross-reference and validate findings
- Prioritize recent publications (especially for fast-moving fields)
- Cite specific papers with titles, authors, and publication years
- Synthesize findings into coherent insights, not just lists
- Be critical: note limitations, controversies, or gaps in the literature

📅 Today's date: {datetime.now().strftime('%Y-%m-%d')}

🚀 Begin your research now. Use tools strategically and provide a comprehensive, well-sourced response.
"""
    messages = [{"role": "user", "content": prompt.strip()}]
    
    # Delegate to unified client
    content = llm_client.call_llm_with_tools(
        client=client,
        model=model,
        messages=messages,
        aisuite_tools=tools.aisuite_tools,
        responses_tool_defs=tools.responses_tool_defs,
        tool_mapping=tools.tool_mapping
    )
    
    print("✅ Output:\n", content)
    return (content, messages) if return_messages else content

def writer_agent(task: str, model: str = "openai:gpt-4o") -> str:
    """
    Executes writing tasks.
    """
    print("==================================")
    print("✍️ Writer Agent")
    print("==================================")
    messages = [
        {"role": "system", "content": """You are an award-winning technical writer with expertise in academic publications, grant proposals, whitepapers, and research reports.

Your writing is characterized by:
- Clear, precise language that balances accessibility with technical rigor
- Logical flow with smooth transitions between ideas
- Evidence-based arguments supported by citations
- Well-structured sections with informative headings
- Engaging introductions that establish context and significance
- Insightful conclusions that synthesize findings and suggest future directions
- Compelling narratives that make science interesting and attractive to readers
- Concrete examples and analogies that illuminate abstract concepts
- Real-world applications that demonstrate practical relevance

Your writing philosophy:
- Make complex ideas accessible through clear explanations and relatable examples
- Use storytelling techniques to maintain reader engagement
- Provide intuitive analogies when introducing technical concepts
- Include illustrative examples that readers can visualize
- Balance depth with readability—never sacrifice clarity for jargon
- Motivate the "why" before diving into the "how"
- Connect abstract theory to tangible applications

Your output formats include:
- Scientific publications (Nature, Science, IEEE style)
- Grant proposals (NSF, NIH, industry RFPs)
- Technical whitepapers and reports
- Research summaries and literature reviews

Write with authority, clarity, and intellectual depth. Make science come alive—avoid dry, lifeless prose. Your goal is to inform, engage, and inspire."""},
        {"role": "user", "content": task}
    ]

    content = llm_client.call_llm_text(client, model, messages, temperature=1.0)
    return content

def editor_agent(task: str, model: str = "openai:gpt-4o") -> str:
    """
    Executes editorial tasks.
    """
    print("==================================")
    print("🧠 Editor Agent")
    print("==================================")
    messages = [
        {"role": "system", "content": """You are a senior editor with decades of experience in academic peer review, technical editing, and content refinement.

Your editorial expertise covers:
- Structural coherence: Ensure logical flow and clear argumentation
- Clarity and precision: Eliminate ambiguity, jargon, and verbosity
- Evidence quality: Verify claims are well-supported and citations are appropriate
- Technical accuracy: Catch errors, inconsistencies, or unsupported assertions
- Readability: Balance technical depth with accessibility for the target audience
- Style consistency: Maintain professional tone and formatting standards

Your editorial approach:
1. Identify strengths to preserve
2. Diagnose weaknesses (structure, clarity, evidence, style)
3. Provide specific, actionable improvements
4. Rewrite sections that need substantial revision
5. Ensure the final product meets publication standards

Be constructive but rigorous. Your goal is to elevate good writing to excellence."""},
        {"role": "user", "content": task}
    ]

    content = llm_client.call_llm_text(client, model, messages, temperature=0.7)
    return content

# Agent registry for executor
agent_registry = {
    "research_agent": research_agent,
    "editor_agent": editor_agent,
    "writer_agent": writer_agent,
}

def executor_agent(plan_steps: list[str], model: str = "openai:gpt-4o"):
    """
    Routes each task to the correct sub-agent.
    """
    history = []

    print("==================================")
    print("🎯 Executor Agent")
    print("==================================")

    for i, step in enumerate(plan_steps):
        agent_decision_prompt = f"""
You are an execution manager for a multi-agent research team.

Given the following instruction, identify which agent should perform it and extract the clean task.

Return only a valid JSON object with two keys:
- "agent": one of ["research_agent", "editor_agent", "writer_agent"]
- "task": a string with the instruction that the agent should follow

Only respond with a valid JSON object. Do not include explanations or markdown formatting.

Instruction: "{step}"
"""
        messages = [{"role": "user", "content": agent_decision_prompt}]
        content = llm_client.call_llm_text(client, model, messages, temperature=0.0)

        try:
            cleaned_json = utils.clean_json_block(content)
            agent_info = json.loads(cleaned_json)

            agent_name = agent_info["agent"]
            task = agent_info["task"]

            # Build context
            context = "\n".join([
                f"Step {j+1} executed by {a}:\n{r}" 
                for j, (s, a, r) in enumerate(history)
            ])
            enriched_task = f"""You are {agent_name}.

Here is the context of what has been done so far:
{context}

Your next task is:
{task}
"""

            print(f"\n🛠️ Executing with agent: `{agent_name}` on task: {task}")

            if agent_name in agent_registry:
                output = agent_registry[agent_name](enriched_task)
                history.append((step, agent_name, output))
            else:
                output = f"⚠️ Unknown agent: {agent_name}"
                history.append((step, agent_name, output))

            print(f"✅ Output:\n{output}")
            
        except Exception as e:
            print(f"❌ Execution Error at step {i}: {e}")
            history.append((step, "error", str(e)))

    return history
