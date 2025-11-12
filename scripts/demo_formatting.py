#!/usr/bin/env python3
"""
Demonstration of the new formatting capabilities without requiring API calls.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import only the formatting module directly (no API dependencies)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "formatting",
    project_root / "reflection" / "research_agent" / "formatting.py"
)
formatting = importlib.util.module_from_spec(spec)
spec.loader.exec_module(formatting)

wrap_text = formatting.wrap_text
format_essay_as_markdown = formatting.format_essay_as_markdown


def demo_text_wrapping():
    """Demonstrate text wrapping functionality."""
    print("=" * 80)
    print("Text Wrapping Demo")
    print("=" * 80)
    print()
    
    # Example of poorly formatted text (like the old output)
    long_text = """**The Main Technical Ingredients Needed for AGI Systems** The pursuit of Artificial General Intelligence (AGI) is one of the most ambitious goals in artificial intelligence. Unlike narrow AI, which is designed for specific tasks, AGI aims to emulate human cognitive abilities, including reasoning, learning, and adaptability across various contexts. This essay outlines the essential technical components necessary for constructing AGI systems: reasoning, world modeling, planning, memory, tool use, multimodality, and self-reflection. Integrating these components is crucial for developing a truly versatile and intelligent artificial system.

Reasoning is foundational for AGI systems. It involves drawing logical conclusions from available data or knowledge and can be classified into deductive, inductive, and abductive reasoning."""
    
    print("BEFORE (Hard to Read):")
    print("-" * 80)
    print(long_text[:300] + "...")
    print()
    
    # Apply wrapping
    wrapped = wrap_text(long_text, width=88, preserve_paragraphs=True)
    
    print("AFTER (Readable):")
    print("-" * 80)
    print(wrapped[:500] + "...")
    print()


def demo_markdown_formatting():
    """Demonstrate markdown formatting."""
    print("=" * 80)
    print("Markdown Formatting Demo")
    print("=" * 80)
    print()
    
    essay_text = """**Introduction to AGI**

Artificial General Intelligence represents a significant milestone in AI research.
Unlike narrow AI systems, AGI aims to replicate human-level cognitive abilities
across diverse domains.

**Key Components**

The development of AGI requires several technical ingredients including reasoning,
world modeling, planning, and memory systems."""
    
    markdown = format_essay_as_markdown(
        essay_text=essay_text,
        topic="Technical Ingredients for AGI Systems",
        word_count=42,
        iteration=2,
        wrap_width=88,
    )
    
    print("Generated Markdown:")
    print("-" * 80)
    print(markdown)
    print()


def main():
    """Run all demos."""
    demo_text_wrapping()
    print()
    demo_markdown_formatting()
    
    print("=" * 80)
    print("✨ Formatting Demo Complete!")
    print()
    print("Key Features:")
    print("  • Proper line wrapping at 88 characters (configurable)")
    print("  • Paragraph preservation with blank lines")
    print("  • Markdown formatting with metadata")
    print("  • PDF generation support (requires external tools)")
    print()
    print("To use with the research agent:")
    print("  python scripts/run_reflection_research_agent.py 'Your topic' \\")
    print("      --generate-pdf --min-words 1000 --max-words 2000")
    print("=" * 80)


if __name__ == "__main__":
    main()
