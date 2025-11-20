"""
Enhanced Research Agent with Integrated Component-Wise Evaluation

This module extends the base research agent with evaluation capabilities to
improve source quality and provide feedback during the research process.
"""

import json
from typing import Optional, Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

# Import production research tools from eval package
import sys
from pathlib import Path
eval_path = Path(__file__).parent.parent
sys.path.insert(0, str(eval_path))

from research_tools import (
    arxiv_search_tool,
    tavily_search_tool,
    wikipedia_search_tool,
    TOOL_METADATA
)
from domain_evaluator import DomainEvaluator, evaluate_sources
from metrics import EvaluationResult
from config import ACADEMIC_DOMAINS

# Load environment variables
load_dotenv()


class EvaluatedResearchAgent:
    """
    Research agent with integrated component-wise evaluation.
    
    This agent extends the base research workflow with:
    1. Source quality evaluation after each search
    2. Automatic retry with improved prompts if sources are poor
    3. Comprehensive evaluation metrics in the final output
    4. Optional reflection with evaluation feedback
    
    Example:
        >>> agent = EvaluatedResearchAgent(
        ...     preferred_domains=ACADEMIC_DOMAINS,
        ...     min_source_ratio=0.5
        ... )
        >>> results = agent.generate_report("quantum computing")
        >>> print(f"Source quality: {results['evaluation'].status}")
    """
    
    def __init__(
        self,
        preferred_domains: Optional[List[str]] = None,
        min_source_ratio: float = 0.4,
        model: str = "gpt-4o",
        reflection_model: str = "gpt-4o-mini",
        max_retries: int = 2,
        verbose: bool = True
    ):
        """
        Initialize the evaluated research agent.
        
        Args:
            preferred_domains: List of preferred domains for evaluation.
                             If None, uses ACADEMIC_DOMAINS.
            min_source_ratio: Minimum ratio of preferred sources (0.0-1.0)
            model: OpenAI model for research generation
            reflection_model: OpenAI model for reflection
            max_retries: Maximum retries if source quality is poor
            verbose: Print progress messages
        """
        self.client = OpenAI()
        self.preferred_domains = preferred_domains or ACADEMIC_DOMAINS
        self.min_source_ratio = min_source_ratio
        self.model = model
        self.reflection_model = reflection_model
        self.max_retries = max_retries
        self.verbose = verbose
        
        # Initialize evaluator
        self.evaluator = DomainEvaluator(
            preferred_domains=self.preferred_domains,
            min_ratio=self.min_source_ratio
        )
        
        # Tool definitions for OpenAI API
        self.tool_defs = self._create_tool_definitions()
        
        # Tool mapping for execution
        self.tool_mapping = {
            "arxiv_search_tool": arxiv_search_tool,
            "tavily_search_tool": tavily_search_tool,
            "wikipedia_search_tool": wikipedia_search_tool,
        }
    
    def _create_tool_definitions(self) -> List[Dict[str, Any]]:
        """Create OpenAI tool definitions from production tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "arxiv_search_tool",
                    "description": "Search arXiv for academic papers. Use for scientific research, papers, and academic literature.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for papers"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 5)",
                                "default": 5
                            },
                            "search_field": {
                                "type": "string",
                                "description": "Field to search: 'all', 'ti' (title), 'au' (author), 'abs' (abstract)",
                                "enum": ["all", "ti", "au", "abs", "cat"],
                                "default": "all"
                            },
                            "sort_by": {
                                "type": "string",
                                "description": "Sort order: 'relevance' or 'submittedDate'",
                                "enum": ["relevance", "submittedDate"],
                                "default": "relevance"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "tavily_search_tool",
                    "description": "Search the web for current information. Use for recent news, general information, and web content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 5)",
                                "default": 5
                            },
                            "search_depth": {
                                "type": "string",
                                "description": "Search depth: 'basic' or 'advanced'",
                                "enum": ["basic", "advanced"],
                                "default": "basic"
                            },
                            "topic": {
                                "type": "string",
                                "description": "Topic filter: 'general' or 'news'",
                                "enum": ["general", "news"],
                                "default": "general"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "wikipedia_search_tool",
                    "description": "Search Wikipedia for encyclopedic summaries. Use for background information and definitions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Wikipedia search query"
                            },
                            "sentences": {
                                "type": "integer",
                                "description": "Number of sentences in summary (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    
    def generate_report(
        self,
        prompt: str,
        max_turns: int = 10,
        evaluate_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a research report with integrated evaluation.
        
        Args:
            prompt: Research question or topic
            max_turns: Maximum conversation turns
            evaluate_sources: Whether to evaluate source quality
        
        Returns:
            dict with keys:
                - report: Final research report text
                - evaluation: EvaluationResult object (if evaluate_sources=True)
                - tool_calls: List of tool calls made
                - messages: Full conversation history
                - retry_count: Number of retries due to poor sources
        """
        attempt = 0
        best_result = None
        best_evaluation = None
        
        while attempt <= self.max_retries:
            if self.verbose and attempt > 0:
                print(f"\n🔄 Retry attempt {attempt}/{self.max_retries}")
                print("   Reason: Source quality below threshold")
            
            # Generate report
            result = self._generate_single_report(
                prompt,
                max_turns=max_turns,
                attempt=attempt
            )
            
            # Evaluate sources if enabled
            if evaluate_sources:
                evaluation = self.evaluator.evaluate_text(result["report"])
                result["evaluation"] = evaluation
                
                if self.verbose:
                    print(f"\n📊 Source Evaluation:")
                    print(f"   Status: {evaluation.status}")
                    print(f"   Preferred: {evaluation.preferred_count}/{evaluation.total_sources}")
                    print(f"   Ratio: {evaluation.preferred_ratio:.1%}")
                
                # Check if quality is acceptable
                if evaluation.status == "PASS" or attempt >= self.max_retries:
                    result["retry_count"] = attempt
                    return result
                
                # Store best result so far
                if best_result is None or evaluation.preferred_ratio > best_evaluation.preferred_ratio:
                    best_result = result
                    best_evaluation = evaluation
                
                # Prepare for retry with improved prompt
                prompt = self._create_retry_prompt(prompt, evaluation)
            else:
                result["retry_count"] = 0
                return result
            
            attempt += 1
        
        # Return best result if all retries failed
        if best_result:
            best_result["retry_count"] = self.max_retries
            return best_result
        
        raise Exception("Failed to generate report after all retries")
    
    def _generate_single_report(
        self,
        prompt: str,
        max_turns: int,
        attempt: int = 0
    ) -> Dict[str, Any]:
        """Generate a single research report."""
        # Build system prompt with evaluation awareness
        system_content = self._build_system_prompt(attempt)
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ]
        
        tool_calls_made = []
        
        for turn in range(max_turns):
            if self.verbose:
                print(f"\n{'='*80}")
                print(f"Turn {turn + 1}/{max_turns}")
                print(f"{'='*80}")
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tool_defs,
                    tool_choice="auto",
                    temperature=1,
                )
            except Exception as e:
                raise Exception(f"OpenAI API error on turn {turn + 1}: {str(e)}")
            
            msg = response.choices[0].message
            messages.append(msg)
            
            # Check if we have a final answer
            if not msg.tool_calls:
                return {
                    "report": msg.content,
                    "tool_calls": tool_calls_made,
                    "messages": messages
                }
            
            # Execute tool calls
            for call in msg.tool_calls:
                tool_name = call.function.name
                args = json.loads(call.function.arguments)
                
                if self.verbose:
                    print(f"🛠️  {tool_name}({args})")
                
                tool_calls_made.append({
                    "tool": tool_name,
                    "args": args
                })
                
                try:
                    tool_func = self.tool_mapping[tool_name]
                    result = tool_func(**args)
                except Exception as e:
                    result = [{"error": str(e)}]
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": tool_name,
                    "content": json.dumps(result)
                })
        
        raise Exception(f"Max turns ({max_turns}) reached without final answer")
    
    def _build_system_prompt(self, attempt: int = 0) -> str:
        """Build system prompt with evaluation awareness."""
        base_prompt = """You are a research assistant that can search the web and arXiv to write detailed, accurate, and properly sourced research reports.

🔍 Use tools when appropriate (e.g., to find scientific papers or web content).
📚 Cite sources whenever relevant. Do NOT omit citations for brevity.
🌐 When possible, include full URLs (arXiv links, web sources, etc.).
✍️ Use an academic tone, organize output into clearly labeled sections, and include inline citations or footnotes as needed.
🚫 Do not include placeholder text such as '(citation needed)' or '(citations omitted)'."""
        
        if attempt > 0:
            base_prompt += f"""

⚠️ IMPORTANT: Previous attempt had insufficient high-quality sources.
Focus on finding sources from:
- Academic journals and papers (arxiv.org, nature.com, science.org)
- University and research institution websites (.edu, .gov)
- Reputable scientific publishers

Prioritize peer-reviewed and authoritative sources."""
        
        return base_prompt
    
    def _create_retry_prompt(self, original_prompt: str, evaluation: EvaluationResult) -> str:
        """Create an improved prompt for retry based on evaluation."""
        feedback = f"""
Previous attempt found {evaluation.total_sources} sources, but only {evaluation.preferred_count} were from preferred domains ({evaluation.preferred_ratio:.1%}).

Please retry with focus on finding HIGH-QUALITY ACADEMIC sources from:
- arXiv papers
- Academic journals (Nature, Science, etc.)
- University research (.edu domains)
- Government research (.gov domains)

Original request: {original_prompt}
"""
        return feedback
    
    def reflect_and_rewrite(
        self,
        report: str,
        evaluation: Optional[EvaluationResult] = None,
        max_retries: int = 3
    ) -> Dict[str, str]:
        """
        Generate reflection and revised report with evaluation feedback.
        
        Args:
            report: Original research report
            evaluation: Optional evaluation result to include in reflection
            max_retries: Maximum retries for JSON parsing
        
        Returns:
            dict with keys:
                - reflection: Structured reflection text
                - revised_report: Improved version of the report
        """
        system_prompt = "You are an academic reviewer and editor."
        
        eval_context = ""
        if evaluation:
            eval_context = f"""

**Source Quality Evaluation:**
- Total sources: {evaluation.total_sources}
- Preferred sources: {evaluation.preferred_count} ({evaluation.preferred_ratio:.1%})
- Status: {evaluation.status}
- Preferred domains used: {', '.join([s.domain for s in evaluation.preferred_sources[:5]])}
"""
        
        user_prompt = f"""Please review the following research report and provide:

1. A structured reflection analyzing:
   - **Strengths**: What the report does well
   - **Source Quality**: Assessment of sources used{' (see evaluation below)' if evaluation else ''}
   - **Limitations**: What could be improved
   - **Suggestions**: Specific recommendations for enhancement
   - **Opportunities**: Areas for deeper exploration

2. A revised version of the report that addresses the identified issues.
{eval_context}

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
                response = self.client.chat.completions.create(
                    model=self.reflection_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3
                )
                
                llm_output = response.choices[0].message.content.strip()
                data = json.loads(llm_output)
                
                if "reflection" not in data or "revised_report" not in data:
                    raise ValueError("Missing required keys in JSON output")
                
                return {
                    "reflection": str(data.get("reflection", "")).strip(),
                    "revised_report": str(data.get("revised_report", "")).strip(),
                }
                
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    if self.verbose:
                        print(f"⚠️  JSON parsing failed (attempt {attempt + 1}/{max_retries}). Retrying...")
                    user_prompt += "\n\n**CRITICAL**: Your previous response was not valid JSON. Please output ONLY the JSON object."
                else:
                    raise Exception(f"Failed to produce valid JSON after {max_retries} attempts")
            except Exception as e:
                if attempt < max_retries - 1:
                    if self.verbose:
                        print(f"⚠️  Error: {str(e)} (attempt {attempt + 1}/{max_retries}). Retrying...")
                else:
                    raise Exception(f"Error after {max_retries} attempts: {str(e)}")
    
    def convert_to_html(self, report: str, temperature: float = 0.5) -> str:
        """
        Convert research report to HTML.
        
        Args:
            report: Plain text report
            temperature: Temperature for generation
        
        Returns:
            Complete HTML document
        """
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
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        
        html = response.choices[0].message.content.strip()
        
        # Clean markdown artifacts
        import re
        html = re.sub(r'^```html\s*\n?', '', html, flags=re.IGNORECASE)
        html = re.sub(r'^```\s*\n?', '', html)
        html = re.sub(r'\n?```\s*$', '', html)
        
        return html.strip()
