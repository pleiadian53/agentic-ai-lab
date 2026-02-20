"""
Nexus Knowledge Layer
======================

File-based personal knowledge base with lexical search.
Shared substrate with OpenClaw/Lyra's ``kb add`` workflow.
"""

from .kb import KnowledgeBase, get_kb_dir

__all__ = ["KnowledgeBase", "get_kb_dir"]
