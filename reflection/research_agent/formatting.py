"""Text formatting and PDF generation utilities for research agent output."""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any


def wrap_text(text: str, width: int = 88, preserve_paragraphs: bool = True) -> str:
    """
    Wrap text to a specified width while preserving paragraph structure.
    
    Args:
        text: Input text to wrap
        width: Maximum line width (default: 88 characters)
        preserve_paragraphs: If True, preserve paragraph breaks
        
    Returns:
        Formatted text with proper line wrapping
    """
    if not preserve_paragraphs:
        return textwrap.fill(text, width=width)
    
    # Split into paragraphs (separated by blank lines or single newlines)
    paragraphs = []
    current_para = []
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            # Empty line - end current paragraph
            if current_para:
                paragraphs.append(' '.join(current_para))
                current_para = []
            paragraphs.append('')  # Preserve blank line
        else:
            current_para.append(line)
    
    # Don't forget the last paragraph
    if current_para:
        paragraphs.append(' '.join(current_para))
    
    # Wrap each paragraph
    wrapped_paragraphs = []
    for para in paragraphs:
        if not para:
            wrapped_paragraphs.append('')
        else:
            wrapped_paragraphs.append(textwrap.fill(para, width=width))
    
    return '\n'.join(wrapped_paragraphs)


def format_essay_as_markdown(
    *,
    essay_text: str,
    topic: str,
    word_count: int,
    iteration: int | None = None,
    wrap_width: int = 88,
) -> str:
    """
    Format an essay as a well-structured markdown document.
    
    Args:
        essay_text: The essay content
        topic: The essay topic
        word_count: Number of words in the essay
        iteration: Optional iteration number
        wrap_width: Maximum line width for text wrapping
        
    Returns:
        Formatted markdown string
    """
    lines = []
    
    # Title
    if iteration is not None:
        lines.append(f"# Essay (Iteration {iteration})")
    else:
        lines.append("# Essay")
    
    lines.append("")
    
    # Metadata
    lines.append("## Metadata")
    lines.append("")
    lines.append(f"- **Topic**: {topic}")
    lines.append(f"- **Word Count**: {word_count}")
    if iteration is not None:
        lines.append(f"- **Iteration**: {iteration}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Essay content with proper wrapping
    lines.append("## Content")
    lines.append("")
    wrapped_essay = wrap_text(essay_text, width=wrap_width, preserve_paragraphs=True)
    lines.append(wrapped_essay)
    
    return '\n'.join(lines)


def generate_pdf_from_markdown(
    markdown_path: Path,
    output_pdf_path: Path | None = None,
    title: str | None = None,
) -> Path:
    """
    Generate a PDF from a markdown file using markdown-pdf or similar tool.
    
    This function requires external dependencies:
    - Option 1: markdown-pdf (npm package)
    - Option 2: pandoc (system package)
    - Option 3: weasyprint (Python package)
    
    Args:
        markdown_path: Path to the markdown file
        output_pdf_path: Optional output PDF path (defaults to same name with .pdf)
        title: Optional document title
        
    Returns:
        Path to the generated PDF file
        
    Raises:
        ImportError: If no PDF generation tool is available
        RuntimeError: If PDF generation fails
    """
    if output_pdf_path is None:
        output_pdf_path = markdown_path.with_suffix('.pdf')
    
    # Try different PDF generation methods in order of preference
    
    # Method 1: Try weasyprint (Python-based, good quality)
    try:
        from markdown import markdown
        from weasyprint import HTML, CSS
        
        # Read markdown and convert to HTML
        md_content = markdown_path.read_text(encoding='utf-8')
        html_content = markdown(md_content, extensions=['extra', 'codehilite'])
        
        # Add CSS styling for better formatting
        css_style = CSS(string="""
            @page {
                size: letter;
                margin: 1in;
            }
            body {
                font-family: 'Georgia', 'Times New Roman', serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #333;
            }
            h1 {
                font-size: 24pt;
                margin-top: 0;
                margin-bottom: 0.5em;
                color: #1a1a1a;
            }
            h2 {
                font-size: 18pt;
                margin-top: 1.5em;
                margin-bottom: 0.5em;
                color: #2a2a2a;
            }
            h3 {
                font-size: 14pt;
                margin-top: 1em;
                margin-bottom: 0.5em;
                color: #3a3a3a;
            }
            p {
                margin-bottom: 1em;
                text-align: justify;
            }
            ul, ol {
                margin-bottom: 1em;
            }
            code {
                font-family: 'Courier New', monospace;
                background-color: #f5f5f5;
                padding: 2px 4px;
                border-radius: 3px;
            }
            pre {
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
            hr {
                border: none;
                border-top: 1px solid #ccc;
                margin: 2em 0;
            }
        """)
        
        # Generate PDF
        html_doc = HTML(string=html_content)
        html_doc.write_pdf(output_pdf_path, stylesheets=[css_style])
        
        return output_pdf_path
        
    except ImportError:
        pass  # Try next method
    
    # Method 2: Try pandoc (if installed)
    try:
        import subprocess
        
        result = subprocess.run(
            ['pandoc', '--version'],
            capture_output=True,
            text=True,
        )
        
        if result.returncode == 0:
            # Pandoc is available
            cmd = [
                'pandoc',
                str(markdown_path),
                '-o', str(output_pdf_path),
                '--pdf-engine=xelatex',
                '-V', 'geometry:margin=1in',
                '-V', 'fontsize=11pt',
                '-V', 'linestretch=1.5',
            ]
            
            if title:
                cmd.extend(['-V', f'title={title}'])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return output_pdf_path
            else:
                raise RuntimeError(f"Pandoc failed: {result.stderr}")
    
    except (FileNotFoundError, subprocess.SubprocessError):
        pass  # Try next method
    
    # Method 3: Try markdown-pdf (npm package)
    try:
        import subprocess
        
        result = subprocess.run(
            ['markdown-pdf', '--version'],
            capture_output=True,
            text=True,
        )
        
        if result.returncode == 0:
            cmd = [
                'markdown-pdf',
                str(markdown_path),
                '-o', str(output_pdf_path),
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return output_pdf_path
            else:
                raise RuntimeError(f"markdown-pdf failed: {result.stderr}")
    
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    
    # No method worked
    raise ImportError(
        "No PDF generation tool available. Please install one of:\n"
        "  1. pip install weasyprint markdown (recommended)\n"
        "  2. System package: pandoc with xelatex\n"
        "  3. npm install -g markdown-pdf"
    )


def save_formatted_essay(
    *,
    essay_text: str,
    output_path: Path,
    topic: str,
    word_count: int,
    iteration: int | None = None,
    wrap_width: int = 88,
    generate_pdf: bool = False,
) -> dict[str, Path]:
    """
    Save an essay with proper formatting to text, markdown, and optionally PDF.
    
    Args:
        essay_text: The essay content
        output_path: Base output path (without extension)
        topic: The essay topic
        word_count: Number of words
        iteration: Optional iteration number
        wrap_width: Maximum line width for text wrapping
        generate_pdf: Whether to generate a PDF version
        
    Returns:
        Dictionary mapping format names to output paths
    """
    output_files = {}
    
    # Save plain text with wrapping
    txt_path = output_path.with_suffix('.txt')
    wrapped_text = wrap_text(essay_text, width=wrap_width, preserve_paragraphs=True)
    txt_path.write_text(wrapped_text, encoding='utf-8')
    output_files['txt'] = txt_path
    
    # Save markdown version
    md_path = output_path.with_suffix('.md')
    markdown_content = format_essay_as_markdown(
        essay_text=essay_text,
        topic=topic,
        word_count=word_count,
        iteration=iteration,
        wrap_width=wrap_width,
    )
    md_path.write_text(markdown_content, encoding='utf-8')
    output_files['md'] = md_path
    
    # Generate PDF if requested
    if generate_pdf:
        try:
            pdf_path = generate_pdf_from_markdown(
                md_path,
                title=f"Essay: {topic[:50]}..." if len(topic) > 50 else f"Essay: {topic}",
            )
            output_files['pdf'] = pdf_path
        except (ImportError, RuntimeError) as e:
            # PDF generation failed, but we still have text and markdown
            print(f"Warning: PDF generation failed: {e}")
    
    return output_files
