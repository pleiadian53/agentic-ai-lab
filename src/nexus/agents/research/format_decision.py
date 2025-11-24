"""
Format Decision Agent - Intelligent document format selection.

This module implements a multi-layer decision system for determining
the optimal document generation strategy based on:
1. Topic analysis (does it need equations?)
2. LLM capability detection (can it generate PDF directly?)
3. Fallback chain (PDF → LaTeX → Markdown)
"""

import json
from typing import Dict, Literal
from aisuite import Client

from . import llm_client

# Shared client
client = Client()

OutputFormat = Literal["pdf_direct", "latex", "markdown"]


def analyze_topic_requirements(topic: str, model: str = "openai:gpt-4o") -> Dict:
    """
    Analyze if the topic requires mathematical equations or technical symbols.
    
    Args:
        topic: Research topic to analyze
        model: LLM model to use for analysis
        
    Returns:
        dict with:
            - needs_equations: bool
            - reasoning: str
            - complexity: str ("simple", "moderate", "complex")
    """
    print("==================================")
    print("🔍 Topic Analysis Agent")
    print("==================================")
    
    prompt = f"""Analyze this research topic and determine if it requires mathematical equations, formulas, or technical symbols:

Topic: "{topic}"

Consider:
- Does this field typically use mathematical notation? (Physics, Math, CS theory, Engineering, Computational Biology, etc.)
- Would equations improve clarity and precision?
- Are there likely to be formulas, algorithms, or mathematical models?

Respond with ONLY a JSON object (no markdown, no code blocks):
{{
  "needs_equations": true or false,
  "reasoning": "Brief explanation of why equations are/aren't needed",
  "complexity": "simple" or "moderate" or "complex",
  "example_symbols": ["list of likely mathematical symbols/notation if applicable"]
}}
"""
    
    messages = [{"role": "user", "content": prompt}]
    response = llm_client.call_llm_text(client, model, messages, temperature=0.3)
    
    try:
        # Clean and parse JSON
        response = response.strip()
        if response.startswith('```'):
            # Remove markdown code blocks
            lines = response.split('\n')
            response = '\n'.join([l for l in lines if not l.strip().startswith('```')])
        
        result = json.loads(response)
        print(f"📊 Needs equations: {result.get('needs_equations', False)}")
        print(f"💭 Reasoning: {result.get('reasoning', 'N/A')}")
        return result
    except Exception as e:
        print(f"⚠️  Failed to parse response, defaulting to markdown: {e}")
        return {
            "needs_equations": False,
            "reasoning": "Failed to analyze, defaulting to safe option",
            "complexity": "simple"
        }


def check_llm_pdf_capability(model: str) -> Dict:
    """
    Check if the LLM can generate PDF files directly.
    
    Args:
        model: LLM model identifier
        
    Returns:
        dict with:
            - can_generate_pdf: bool
            - method: str (description of how it generates PDFs)
    """
    print("==================================")
    print("🤖 LLM Capability Detection")
    print("==================================")
    
    # Known capabilities based on model
    # Note: As of Nov 2024, most LLMs cannot generate binary PDFs
    # Gemini 2.0 Flash and some future models may support this
    
    pdf_capable_models = {
        "google:gemini-2.0-flash": True,
        "google:gemini-2.0-flash-exp": True,
        # Add more as they become available
    }
    
    can_generate = pdf_capable_models.get(model, False)
    
    if can_generate:
        print(f"✅ {model} can generate PDF directly")
        return {
            "can_generate_pdf": True,
            "method": "Native PDF generation via model API"
        }
    else:
        print(f"❌ {model} cannot generate PDF directly")
        return {
            "can_generate_pdf": False,
            "method": "Will use LaTeX compilation or markdown conversion"
        }


def decide_output_format(
    topic: str,
    model: str = "openai:gpt-4o",
    user_preference: str = None
) -> Dict:
    """
    Multi-layer decision system for optimal document format.
    
    Decision tree:
    1. Does topic need equations? → No → Markdown
    2. Can LLM generate PDF? → Yes → Direct PDF
    3. Otherwise → LaTeX (compile to PDF)
    
    Args:
        topic: Research topic
        model: LLM model to use
        user_preference: Optional user override ("pdf", "latex", "markdown")
        
    Returns:
        dict with:
            - format: OutputFormat
            - reasoning: str
            - needs_equations: bool
            - llm_can_pdf: bool
    """
    print("\n" + "="*60)
    print("📋 FORMAT DECISION SYSTEM")
    print("="*60)
    
    # User override
    if user_preference:
        print(f"👤 User preference: {user_preference}")
        return {
            "format": user_preference,
            "reasoning": "User explicitly requested this format",
            "needs_equations": True,  # Assume yes if user cares about format
            "llm_can_pdf": False
        }
    
    # Step 1: Analyze topic
    topic_analysis = analyze_topic_requirements(topic, model)
    needs_equations = topic_analysis.get("needs_equations", False)
    
    # Step 2: If no equations needed, use markdown
    if not needs_equations:
        print("\n✅ Decision: MARKDOWN (no equations needed)")
        return {
            "format": "markdown",
            "reasoning": topic_analysis.get("reasoning", "Topic doesn't require mathematical notation"),
            "needs_equations": False,
            "llm_can_pdf": False
        }
    
    # Step 3: Check if LLM can generate PDF directly
    pdf_capability = check_llm_pdf_capability(model)
    llm_can_pdf = pdf_capability.get("can_generate_pdf", False)
    
    # Step 4: Decide based on capabilities
    if llm_can_pdf:
        print("\n✅ Decision: DIRECT PDF (LLM supports native PDF generation)")
        return {
            "format": "pdf_direct",
            "reasoning": f"Topic needs equations and {model} can generate PDF directly",
            "needs_equations": True,
            "llm_can_pdf": True
        }
    else:
        print("\n✅ Decision: LATEX (will compile to PDF with XeLaTeX)")
        return {
            "format": "latex",
            "reasoning": f"Topic needs equations but {model} cannot generate PDF directly. Will use LaTeX compilation.",
            "needs_equations": True,
            "llm_can_pdf": False
        }


def get_writer_instructions(format_decision: Dict) -> str:
    """
    Generate specific instructions for the writer agent based on format decision.
    
    Args:
        format_decision: Output from decide_output_format()
        
    Returns:
        str: Instructions to append to writer agent prompt
    """
    format_type = format_decision.get("format", "markdown")
    
    if format_type == "pdf_direct":
        return """
📄 OUTPUT FORMAT: Direct PDF Generation

Generate a complete, well-formatted PDF document. Include:
- Professional typography and layout
- Properly rendered mathematical equations
- Clear section headings and structure
- Citations and references
"""
    
    elif format_type == "latex":
        return """
📄 OUTPUT FORMAT: Pure LaTeX (NO MARKDOWN!)

Generate a complete LaTeX document that will be compiled with XeLaTeX.

🔬 CRITICAL REQUIREMENT: INCLUDE MATHEMATICAL EQUATIONS!

This is a MATHEMATICAL/SCIENTIFIC topic. You MUST:
1. Include the main equations/formulas relevant to this topic
2. Show mathematical derivations where appropriate
3. Use LaTeX math notation ($...$, \\[...\\], \\begin{equation}...\\end{equation})
4. Include at least 3-5 equations in the document
5. EXPLAIN each equation: define all symbols/variables and interpret what it means

Example: If writing about Schrödinger Equation, you MUST include:

The time-dependent Schrödinger equation:
\\[
i\\hbar \\frac{\\partial \\Psi}{\\partial t} = \\hat{H}\\Psi
\\]
where $\\Psi$ is the wave function, $\\hbar$ is the reduced Planck constant, $t$ is time, 
and $\\hat{H}$ is the Hamiltonian operator. This equation describes how quantum states 
evolve over time, showing that the time derivative of the wave function is proportional 
to the energy operator acting on it.

DO NOT write about equations without:
- Showing the actual mathematical expressions
- Defining all variables and symbols
- Explaining the physical/mathematical meaning

CRITICAL RULES - PURE LaTeX ONLY:
❌ DO NOT use markdown syntax (###, **, -, >, etc.)
❌ DO NOT use markdown headers (# or ##)
❌ DO NOT use markdown lists (- or *)
❌ DO NOT use markdown code blocks (```)
✅ USE ONLY valid LaTeX commands
✅ INCLUDE mathematical equations using $...$ or \\[...\\]

Required structure:
```latex
\\documentclass[11pt,article]{article}
\\usepackage{amsmath,amssymb,amsfonts}
\\usepackage{graphicx}
\\usepackage{hyperref}
\\usepackage{geometry}
\\geometry{margin=1in}

\\title{Your Title}
\\author{Nexus Research Agent}
\\date{\\today}

\\begin{document}
\\maketitle

\\section{Introduction}
Your introduction text here.

\\subsection{Background}
More content.

\\section{Main Content}
Use \\textbf{bold} for emphasis, \\textit{italic} for italics.

IMPORTANT: Include relevant mathematical equations! Examples:

Inline equation in text: The energy-mass equivalence $E = mc^2$ shows...

Display equation (centered):
\\[ \\frac{\\partial^2 u}{\\partial t^2} = c^2 \\nabla^2 u \\]

Multiple equations:
\\begin{align}
    F &= ma \\\\
    E &= \\frac{1}{2}mv^2
\\end{align}

For lists:
\\begin{itemize}
    \\item First item
    \\item Second item
\\end{itemize}

\\section{Conclusion}
Your conclusion.

\\end{document}
```

SPECIAL CHARACTERS - Must escape these in text:
- # → \\#
- % → \\%
- & → \\&
- $ → \\$ (unless in math mode)
- _ → \\_ (unless in math mode)
- { → \\{
- } → \\}
- ~ → \\textasciitilde
- ^ → \\textasciicircum
- \\ → \\textbackslash

STRUCTURE:
- Use \\section{Title} for main sections
- Use \\subsection{Title} for subsections
- Use \\subsubsection{Title} for sub-subsections
- Use \\paragraph{Title} for paragraphs

LISTS:
- Bullet lists: \\begin{itemize} \\item ... \\end{itemize}
- Numbered lists: \\begin{enumerate} \\item ... \\end{enumerate}

EMPHASIS:
- Bold: \\textbf{text}
- Italic: \\textit{text}
- Underline: \\underline{text}

MATH:
- Inline: $E = mc^2$
- Display: \\[ E = mc^2 \\] or $$E = mc^2$$
- Equation environment: \\begin{equation} ... \\end{equation}

Remember: This will be compiled directly with XeLaTeX. Any markdown syntax will cause compilation errors!
"""
    
    else:  # markdown
        return """
📄 OUTPUT FORMAT: Markdown

Generate clean, well-structured Markdown. Use:
- # for main headings, ## for subheadings
- **bold** for emphasis
- `code` for technical terms
- > for quotes
- - for bullet lists
- 1. for numbered lists
"""
