"""Prompt templates for the research agent workflow."""

from __future__ import annotations


def build_draft_prompt(topic: str) -> str:
    """
    Build a prompt for generating an initial essay draft.
    
    Args:
        topic: The essay topic or question to address
        
    Returns:
        Formatted prompt string
    """
    return f"""Write a comprehensive, well-structured essay on the following topic:

TOPIC: {topic}

Requirements:
- Write a complete essay with introduction, body paragraphs, and conclusion
- Present clear arguments supported by reasoning and examples
- Maintain an academic tone appropriate for a research essay
- Aim for approximately 500-800 words
- Use proper paragraph structure and transitions
- Include a thesis statement in the introduction

Output only the essay text, without any meta-commentary or explanations.
""".strip()


def build_reflection_prompt(draft: str) -> str:
    """
    Build a prompt for reflecting on and critiquing an essay draft.
    
    Args:
        draft: The essay text to critique
        
    Returns:
        Formatted prompt string with structured critique framework
    """
    return f"""You are a meticulous peer reviewer and writing coach. Read the essay below and provide a critical but constructive review.

Do NOT rewrite the whole essay. Focus on analysis and concrete guidance.

ESSAY
------
{draft}
------

REVIEW FORMAT (use these exact section headers):

1) One-Sentence Verdict:
   - Provide a concise overall assessment.

2) Strengths:
   - Bullet points highlighting what works well (content and presentation).

3) Structural Issues:
   - Organization, flow, sectioning, transitions, redundancy, missing pieces.

4) Clarity & Precision:
   - Ambiguity, jargon without definition, long sentences, unclear references.

5) Argument Quality:
   - Thesis clarity, logic, evidence/citations, counterarguments, assumptions, fallacies.

6) Style & Tone:
   - Readability, voice consistency, passive/active balance, formatting.

7) Most Important Fixes (Top 5, prioritized):
   - For each: (Problem) → (Why it matters) → (How to fix concretely).
   - Include examples of improved phrasing **only for 1–2 sentences**, not full rewrites.

8) Outline-Level Revision Plan:
   - Bullet list showing a better section order and the purpose of each section.

9) Rubric (1–5, integers):
   - Structure: _
   - Clarity: _
   - Argument Strength: _
   - Style: _
   - Overall: _

Constraints:
- Be frank but professional.
- No full rewrites; keep examples short and targeted.
- If evidence is asserted without support, note it and suggest what sources or data would help.
""".strip()


def build_revision_prompt(original_draft: str, reflection: str) -> str:
    """
    Build a prompt for revising an essay based on feedback.
    
    Args:
        original_draft: The initial essay text
        reflection: Critique and feedback on the draft
        
    Returns:
        Formatted prompt string
    """
    return f"""You are an expert editor and writing coach. 
Revise the following essay based on the provided feedback. 
Incorporate the suggestions to improve clarity, coherence, logical flow, and persuasiveness, 
while preserving the essay's core ideas and factual accuracy.

=====================
ORIGINAL DRAFT
---------------------
{original_draft}

=====================
FEEDBACK / REFLECTION
---------------------
{reflection}

=====================
REVISION INSTRUCTIONS
---------------------
- Address the issues raised in the feedback directly.
- Strengthen argument structure and transitions between sections.
- Clarify ambiguous phrasing or weak evidence.
- Improve readability, sentence flow, and conciseness.
- Ensure consistent academic tone and formatting.
- Do NOT add unrelated content or fabricate citations.
- Output ONLY the revised essay, without commentary or explanation.
""".strip()
