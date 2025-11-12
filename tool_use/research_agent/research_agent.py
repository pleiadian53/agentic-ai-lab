"""
Research Agent - Modular implementation with parallel tool execution and robust error handling.

This module provides the core research agent functionality including:
- Research report generation with tool use
- Reflection and rewriting
- HTML conversion
- Parallel tool execution
"""

import json
from typing import Optional, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

import research_tools
from parallel_tools import execute_tools_parallel

# Load environment variables
load_dotenv()

# Initialize OpenAI client
CLIENT = OpenAI()

# Tool mapping for parallel execution
TOOL_MAPPING = {
    "arxiv_search_tool": research_tools.arxiv_search_tool,
    "tavily_search_tool": research_tools.tavily_search_tool,
}


def generate_research_report_with_tools(
    prompt: str, 
    model: str = "gpt-4o",
    max_turns: int = 10,
    parallel: bool = True,
    verbose: bool = True
) -> str:
    """
    Generates a research report using OpenAI's tool-calling with arXiv and Tavily tools.
    
    Args:
        prompt: The user prompt/research question
        model: OpenAI model name (default: "gpt-4o")
        max_turns: Maximum number of conversation turns (default: 10)
        parallel: Whether to execute tools in parallel (default: True)
        verbose: Whether to print progress (default: True)
    
    Returns:
        str: Final assistant research report text
        
    Raises:
        Exception: If max_turns is reached without completion
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a research assistant that can search the web and arXiv to write detailed, "
                "accurate, and properly sourced research reports.\n\n"
                "🔍 Use tools when appropriate (e.g., to find scientific papers or web content).\n"
                "📚 Cite sources whenever relevant. Do NOT omit citations for brevity.\n"
                "🌐 When possible, include full URLs (arXiv links, web sources, etc.).\n"
                "✍️ Use an academic tone, organize output into clearly labeled sections, and include "
                "inline citations or footnotes as needed.\n"
                "🚫 Do not include placeholder text such as '(citation needed)' or '(citations omitted)'."
            )
        },
        {"role": "user", "content": prompt}
    ]
    
    tools = [research_tools.arxiv_tool_def, research_tools.tavily_tool_def]
    
    for turn in range(max_turns):
        if verbose:
            print(f"\n{'='*80}")
            print(f"Turn {turn + 1}/{max_turns}")
            print(f"{'='*80}")
        
        try:
            response = CLIENT.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=1,
            )
        except Exception as e:
            raise Exception(f"OpenAI API error on turn {turn + 1}: {str(e)}")
        
        msg = response.choices[0].message
        messages.append(msg)
        
        # Check if we have a final answer
        if not msg.tool_calls:
            final_text = msg.content
            if verbose:
                print("\n✅ Final answer received")
                print(f"Length: {len(final_text)} characters")
            return final_text
        
        # Execute tool calls (parallel or sequential)
        if parallel:
            tool_messages = execute_tools_parallel(msg.tool_calls, TOOL_MAPPING, verbose=verbose)
            messages.extend(tool_messages)
        else:
            # Sequential execution (original implementation)
            for call in msg.tool_calls:
                tool_name = call.function.name
                args = json.loads(call.function.arguments)
                if verbose:
                    print(f"🛠️ {tool_name}({args})")
                
                try:
                    tool_func = TOOL_MAPPING[tool_name]
                    result = tool_func(**args)
                except Exception as e:
                    result = {"error": str(e)}
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": tool_name,
                    "content": json.dumps(result)
                })
    
    # Max turns reached
    raise Exception(f"Max turns ({max_turns}) reached without final answer. Consider increasing max_turns.")


def reflection_and_rewrite(
    report, 
    model: str = "gpt-4o-mini", 
    temperature: float = 0.3,
    max_retries: int = 3
) -> Dict[str, str]:
    """
    Generates a structured reflection AND a revised research report.
    Accepts raw text OR the messages list returned by generate_research_report_with_tools.
    
    Args:
        report: Plain text report or messages list
        model: OpenAI model name (default: "gpt-4o-mini")
        temperature: Temperature for generation (default: 0.3)
        max_retries: Maximum retries for JSON parsing errors (default: 3)
    
    Returns:
        dict with keys:
          - "reflection": structured reflection text
          - "revised_report": improved version of the input report
          
    Raises:
        Exception: If LLM fails to produce valid JSON after max_retries
    """
    # Parse input
    report = research_tools.parse_input(report)
    
    system_prompt = "You are an academic reviewer and editor."
    
    user_prompt = f"""Please review the following research report and provide:

1. A structured reflection analyzing:
   - **Strengths**: What the report does well
   - **Limitations**: What could be improved
   - **Suggestions**: Specific recommendations for enhancement
   - **Opportunities**: Areas for deeper exploration

2. A revised version of the report that addresses the identified issues.

**IMPORTANT**: Output ONLY valid JSON with this exact structure:
{{
  "reflection": "<your structured reflection here>",
  "revised_report": "<your improved report here>"
}}

Original Report:
{report}
"""
    
    for attempt in range(max_retries):
        try:
            response = CLIENT.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature
            )
            
            llm_output = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            data = json.loads(llm_output)
            
            # Validate required keys
            if "reflection" not in data or "revised_report" not in data:
                raise ValueError("Missing required keys in JSON output")
            
            return {
                "reflection": str(data.get("reflection", "")).strip(),
                "revised_report": str(data.get("revised_report", "")).strip(),
            }
            
        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                print(f"⚠️  JSON parsing failed (attempt {attempt + 1}/{max_retries}). Retrying...")
                # Adjust prompt for retry
                user_prompt += "\n\n**CRITICAL**: Your previous response was not valid JSON. Please output ONLY the JSON object, with no additional text before or after."
            else:
                raise Exception(
                    f"The LLM failed to produce valid JSON after {max_retries} attempts. "
                    f"Last output: {llm_output[:200]}..."
                )
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️  Error: {str(e)} (attempt {attempt + 1}/{max_retries}). Retrying...")
            else:
                raise Exception(f"Error after {max_retries} attempts: {str(e)}")


def _clean_html_output(html: str) -> str:
    """
    Remove markdown code fences and other artifacts from LLM HTML output.
    
    Args:
        html: Raw HTML output from LLM
        
    Returns:
        Cleaned HTML string
    """
    import re
    
    # Remove markdown code fences at start and end
    # Pattern: ```html or ``` at the beginning
    html = re.sub(r'^```html\s*\n?', '', html, flags=re.IGNORECASE)
    html = re.sub(r'^```\s*\n?', '', html)
    
    # Pattern: ``` at the end
    html = re.sub(r'\n?```\s*$', '', html)
    
    # Strip any remaining whitespace
    html = html.strip()
    
    return html


def convert_report_to_html(
    report, 
    model: str = "gpt-4o", 
    temperature: float = 0.5
) -> str:
    """
    Converts a plaintext research report into a styled HTML page using OpenAI.
    Accepts raw text OR the messages list from the tool-calling step.
    
    Args:
        report: Plain text report or messages list
        model: OpenAI model name (default: "gpt-4o")
        temperature: Temperature for generation (default: 0.5)
    
    Returns:
        str: Complete HTML document
    """
    # Parse input
    report = research_tools.parse_input(report)
    
    system_prompt = "You convert plaintext reports into full clean HTML documents."
    
    user_prompt = f"""Convert the research report below into a professional HTML webpage.

Instructions:
- Return ONLY the HTML code (no markdown code fences, no explanations, no extra text)
- Do NOT wrap the output in ```html or ``` markers
- Start directly with <!DOCTYPE html> or <html>
- Make it look clean and professional
- Organize content with headings
- Make URLs clickable
- Keep citations intact
- Add nice styling

Report:
{report}
"""
    
    response = CLIENT.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature
    )
    
    html = response.choices[0].message.content.strip()
    
    # Clean any markdown artifacts
    html = _clean_html_output(html)
    
    return html
