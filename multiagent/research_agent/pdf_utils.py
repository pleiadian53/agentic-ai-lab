"""
Utilities for generating PDF reports from markdown content.

Uses multiple approaches for robust PDF generation:
1. agentic-doc (primary) - Professional formatting with document intelligence
2. markdown-pdf (fallback) - Simple markdown to PDF conversion
3. weasyprint (alternative) - HTML to PDF with CSS styling
"""
import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def markdown_to_pdf(
    markdown_content: str,
    output_path: Path,
    title: Optional[str] = None,
    author: str = "AI Research Agent",
    method: str = "auto"
) -> Tuple[bool, Optional[str]]:
    """
    Convert markdown content to PDF.
    
    Args:
        markdown_content: Markdown text to convert
        output_path: Path where PDF should be saved
        title: Document title (optional, extracted from markdown if not provided)
        author: Document author
        method: Conversion method - "auto", "agentic-doc", "weasyprint", or "pypandoc"
        
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
        
    Examples:
        >>> success, error = markdown_to_pdf(report, Path("output.pdf"))
        >>> if success:
        ...     print("PDF generated successfully!")
    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Try methods in order of preference
    methods = []
    if method == "auto":
        methods = ["weasyprint", "pypandoc"]  # agentic-doc is for extraction, not generation
    else:
        methods = [method]
    
    last_error = None
    
    for conversion_method in methods:
        try:
            if conversion_method == "weasyprint":
                success, error = _convert_with_weasyprint(
                    markdown_content, output_path, title, author
                )
                if success:
                    logger.info(f"✓ PDF generated using weasyprint: {output_path}")
                    return True, None
                last_error = error
                
            elif conversion_method == "pypandoc":
                success, error = _convert_with_pypandoc(
                    markdown_content, output_path, title, author
                )
                if success:
                    logger.info(f"✓ PDF generated using pypandoc: {output_path}")
                    return True, None
                last_error = error
                
        except Exception as e:
            last_error = f"{conversion_method} failed: {str(e)}"
            logger.warning(f"⚠️  {last_error}")
            continue
    
    # All methods failed
    error_msg = f"All PDF conversion methods failed. Last error: {last_error}"
    logger.error(f"❌ {error_msg}")
    return False, error_msg


def _convert_with_weasyprint(
    markdown_content: str,
    output_path: Path,
    title: Optional[str],
    author: str
) -> Tuple[bool, Optional[str]]:
    """
    Convert markdown to PDF using WeasyPrint (HTML → PDF).
    
    This method converts markdown to HTML first, then renders to PDF with CSS styling.
    """
    try:
        from weasyprint import HTML, CSS
        from markdown import markdown
        
        # Convert markdown to HTML
        html_content = markdown(
            markdown_content,
            extensions=['extra', 'codehilite', 'toc', 'tables']
        )
        
        # Extract title if not provided
        if not title:
            title = _extract_title_from_markdown(markdown_content)
        
        # Create styled HTML document
        styled_html = _create_styled_html(html_content, title, author)
        
        # Generate PDF
        HTML(string=styled_html).write_pdf(
            output_path,
            stylesheets=[CSS(string=_get_pdf_css())]
        )
        
        return True, None
        
    except ImportError as e:
        return False, f"WeasyPrint not installed: {e}"
    except Exception as e:
        return False, f"WeasyPrint conversion failed: {e}"


def _convert_with_pypandoc(
    markdown_content: str,
    output_path: Path,
    title: Optional[str],
    author: str
) -> Tuple[bool, Optional[str]]:
    """
    Convert markdown to PDF using pypandoc (requires pandoc system binary).
    
    This method uses pandoc for high-quality PDF generation with LaTeX.
    """
    try:
        import pypandoc
        
        # Extract title if not provided
        if not title:
            title = _extract_title_from_markdown(markdown_content)
        
        # Create temporary markdown file with metadata
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp:
            # Add YAML front matter
            tmp.write("---\n")
            tmp.write(f"title: {title}\n")
            tmp.write(f"author: {author}\n")
            tmp.write("geometry: margin=1in\n")
            tmp.write("fontsize: 11pt\n")
            tmp.write("---\n\n")
            tmp.write(markdown_content)
            tmp_path = tmp.name
        
        try:
            # Convert to PDF
            pypandoc.convert_file(
                tmp_path,
                'pdf',
                outputfile=str(output_path),
                extra_args=[
                    '--pdf-engine=xelatex',
                    '--toc',
                    '--number-sections'
                ]
            )
            return True, None
            
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except ImportError as e:
        return False, f"pypandoc not installed: {e}"
    except Exception as e:
        return False, f"pypandoc conversion failed: {e}"


def _extract_title_from_markdown(markdown_content: str) -> str:
    """
    Extract title from markdown content (first H1 heading).
    
    Args:
        markdown_content: Markdown text
        
    Returns:
        Title string or "Research Report" if not found
    """
    lines = markdown_content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
    return "Research Report"


def _create_styled_html(html_content: str, title: str, author: str) -> str:
    """
    Wrap HTML content in a styled document template.
    
    Args:
        html_content: HTML body content
        title: Document title
        author: Document author
        
    Returns:
        Complete HTML document string
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="author" content="{author}">
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p class="author">By {author}</p>
    </div>
    <div class="content">
        {html_content}
    </div>
</body>
</html>"""


def _get_pdf_css() -> str:
    """
    Get CSS styling for PDF generation.
    
    Returns:
        CSS string for professional document styling
    """
    return """
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
        
        .header {
            text-align: center;
            margin-bottom: 2em;
            border-bottom: 2px solid #333;
            padding-bottom: 1em;
        }
        
        .header h1 {
            font-size: 24pt;
            margin-bottom: 0.5em;
            color: #000;
        }
        
        .author {
            font-style: italic;
            color: #666;
        }
        
        h1 {
            font-size: 20pt;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            color: #000;
            page-break-after: avoid;
        }
        
        h2 {
            font-size: 16pt;
            margin-top: 1.2em;
            margin-bottom: 0.4em;
            color: #222;
            page-break-after: avoid;
        }
        
        h3 {
            font-size: 13pt;
            margin-top: 1em;
            margin-bottom: 0.3em;
            color: #333;
            page-break-after: avoid;
        }
        
        p {
            margin-bottom: 0.8em;
            text-align: justify;
        }
        
        code {
            font-family: 'Courier New', monospace;
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        pre {
            background-color: #f5f5f5;
            padding: 1em;
            border-left: 3px solid #333;
            overflow-x: auto;
            page-break-inside: avoid;
        }
        
        pre code {
            background-color: transparent;
            padding: 0;
        }
        
        blockquote {
            border-left: 4px solid #ccc;
            padding-left: 1em;
            margin-left: 0;
            font-style: italic;
            color: #666;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
            page-break-inside: avoid;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        
        th {
            background-color: #f5f5f5;
            font-weight: bold;
        }
        
        ul, ol {
            margin-bottom: 1em;
            padding-left: 2em;
        }
        
        li {
            margin-bottom: 0.3em;
        }
        
        a {
            color: #0066cc;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
    """


def check_pdf_dependencies() -> dict:
    """
    Check which PDF generation dependencies are available.
    
    Returns:
        Dictionary with availability status for each method
    """
    status = {
        "weasyprint": False,
        "pypandoc": False,
        "pandoc_binary": False
    }
    
    # Check WeasyPrint
    try:
        import weasyprint
        import markdown
        status["weasyprint"] = True
    except ImportError:
        pass
    
    # Check pypandoc
    try:
        import pypandoc
        status["pypandoc"] = True
        # Check if pandoc binary is available
        try:
            pypandoc.get_pandoc_version()
            status["pandoc_binary"] = True
        except:
            pass
    except ImportError:
        pass
    
    return status


def install_instructions() -> str:
    """
    Get installation instructions for PDF dependencies.
    
    Returns:
        String with installation commands
    """
    return """
PDF Generation Dependencies:

Option 1: WeasyPrint (Recommended - Pure Python)
    mamba install -c conda-forge weasyprint markdown

Option 2: Pandoc (High Quality LaTeX-based)
    # Install pandoc binary
    mamba install -c conda-forge pandoc
    
    # Install Python wrapper
    pip install pypandoc

Note: WeasyPrint is easier to install and works well for most cases.
Pandoc produces higher quality PDFs but requires LaTeX installation.
"""


# Testing and examples
if __name__ == "__main__":
    print("PDF Generation Utilities")
    print("=" * 60)
    
    # Check dependencies
    print("\nChecking PDF dependencies...")
    deps = check_pdf_dependencies()
    for dep, available in deps.items():
        status = "✓" if available else "✗"
        print(f"  {status} {dep}")
    
    if not any(deps.values()):
        print("\n⚠️  No PDF generation dependencies found!")
        print(install_instructions())
    else:
        print("\n✓ PDF generation is available!")
        
        # Test with sample markdown
        sample_md = """# Sample Research Report

## Introduction

This is a test report to demonstrate PDF generation capabilities.

## Methods

- Method 1: Data collection
- Method 2: Analysis
- Method 3: Synthesis

## Results

The results show promising findings in the field of AI research.

### Key Findings

1. Finding one
2. Finding two
3. Finding three

## Conclusion

This demonstrates successful PDF generation from markdown content.
"""
        
        test_output = Path("test_report.pdf")
        success, error = markdown_to_pdf(sample_md, test_output)
        
        if success:
            print(f"\n✓ Test PDF generated: {test_output}")
        else:
            print(f"\n✗ Test failed: {error}")
