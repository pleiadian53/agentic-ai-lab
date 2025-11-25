"""
Utilities for generating PDF reports from markdown content.

Uses multiple approaches for robust PDF generation:
1. agentic-doc (primary) - Professional formatting with document intelligence
2. markdown-pdf (fallback) - Simple markdown to PDF conversion
3. weasyprint (alternative) - HTML to PDF with CSS styling
"""
import os
import tempfile
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def fix_common_latex_errors(latex_content: str) -> Tuple[str, list[str]]:
    """
    Automatically fix common LaTeX syntax errors.
    
    Args:
        latex_content: LaTeX source code
        
    Returns:
        Tuple of (fixed_content, list_of_fixes_applied)
    """
    import re
    
    fixes_applied = []
    content = latex_content
    
    # Fix 1: \labeleq: → \label{eq:
    pattern = r'\\labeleq:(\w+)'
    if re.search(pattern, content):
        content = re.sub(pattern, r'\\label{eq:\1}', content)
        fixes_applied.append("Fixed \\labeleq: → \\label{eq:}")
    
    # Fix 2: \begineq: → \begin{eq:
    pattern = r'\\begineq:(\w+)'
    if re.search(pattern, content):
        content = re.sub(pattern, r'\\begin{eq:\1}', content)
        fixes_applied.append("Fixed \\begineq: → \\begin{eq:}")
    
    # Fix 3: Missing closing braces in \label
    pattern = r'\\label\{([^}]+)$'
    if re.search(pattern, content, re.MULTILINE):
        content = re.sub(pattern, r'\\label{\1}', content, flags=re.MULTILINE)
        fixes_applied.append("Added missing closing brace in \\label")
    
    # Fix 4: Comma after equation in \label (should be period or nothing)
    pattern = r'(\\label\{eq:[^}]+\}),\s*\n'
    if re.search(pattern, content):
        content = re.sub(pattern, r'\1.\n', content)
        fixes_applied.append("Fixed comma after \\label in equation")
    
    return content, fixes_applied


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
        # pypandoc first - it properly handles LaTeX math equations
        methods = ["pypandoc", "weasyprint"]
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
    Convert markdown to PDF using pypandoc (requires pandoc and LaTeX).
    
    This method uses pandoc for high-quality PDF generation with LaTeX.
    """
    try:
        import pypandoc
        import re
        
        # Preprocess markdown to fix math delimiters
        # Convert \[ \] to $$ $$ which pandoc handles more reliably
        # Handle both inline and on separate lines
        markdown_content = re.sub(r'\\\[', r'$$', markdown_content)
        markdown_content = re.sub(r'\\\]', r'$$', markdown_content)
        # Also convert \( \) to $ $ for inline math
        markdown_content = re.sub(r'\\\(', r'$', markdown_content)
        markdown_content = re.sub(r'\\\)', r'$', markdown_content)
        
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
            # Convert to PDF using available PDF engine
            # Try different engines in order of preference
            engines = ['xelatex', 'pdflatex', 'lualatex']
            last_error = None
            
            for engine in engines:
                try:
                    pypandoc.convert_file(
                        tmp_path,
                        'pdf',
                        outputfile=str(output_path),
                        format='markdown+tex_math_dollars',
                        extra_args=[
                            f'--pdf-engine={engine}',
                            '--toc',
                            '--number-sections',
                            '--from=markdown+tex_math_dollars'
                        ]
                    )
                    logger.info(f"✓ PDF generated using pandoc with {engine}")
                    return True, None
                except RuntimeError as e:
                    last_error = str(e)
                    if 'not found' in last_error.lower() or 'exitcode "47"' in last_error:
                        # Engine not available, try next one
                        continue
                    else:
                        # Different error, propagate it
                        raise
            
            # All engines failed
            return False, f"No LaTeX engine available. Tried: {', '.join(engines)}. Last error: {last_error}"
            
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except ImportError as e:
        return False, f"pypandoc not installed: {e}"
    except Exception as e:
        return False, f"pypandoc conversion failed: {e}"


def latex_to_pdf(
    latex_content: str,
    output_path: Path,
    title: Optional[str] = None,
    author: str = "Nexus Research Agent"
) -> Tuple[bool, Optional[str]]:
    """
    Compile LaTeX source directly to PDF.
    
    This is the preferred method for documents with mathematical equations.
    Tries Tectonic first (modern, self-contained), then falls back to XeLaTeX.
    
    Args:
        latex_content: Complete LaTeX document source
        output_path: Path where PDF should be saved
        title: Document title (optional, can be in LaTeX)
        author: Document author
        
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    # Auto-fix common LaTeX errors
    fixed_content, fixes = fix_common_latex_errors(latex_content)
    if fixes:
        logger.info(f"🔧 Auto-fixed {len(fixes)} LaTeX error(s):")
        for fix in fixes:
            logger.info(f"   - {fix}")
    
    # Try Tectonic first (modern, self-contained LaTeX engine)
    success, error = _compile_with_tectonic(fixed_content, output_path)
    if success:
        return True, None
    
    logger.info(f"Tectonic failed ({error}), trying XeLaTeX...")
    
    # Fall back to XeLaTeX
    return _compile_with_xelatex(fixed_content, output_path)


def _compile_with_tectonic(
    latex_content: str,
    output_path: Path
) -> Tuple[bool, Optional[str]]:
    """Compile LaTeX using Tectonic (modern, self-contained engine)."""
    try:
        import re
        
        # Clean content
        cleaned_content = latex_content.strip()
        if cleaned_content.startswith('```'):
            cleaned_content = re.sub(r'^```(?:latex)?\s*\n', '', cleaned_content)
            cleaned_content = re.sub(r'\n```\s*$', '', cleaned_content)
        
        doc_match = re.search(r'\\documentclass', cleaned_content)
        if doc_match:
            cleaned_content = cleaned_content[doc_match.start():]
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            tex_file = tmpdir_path / "document.tex"
            
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            # Compile with Tectonic
            result = subprocess.run(
                ['tectonic', 'document.tex'],
                cwd=tmpdir_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return False, f"Tectonic compilation failed: {result.stderr[:200]}"
            
            # Move PDF to output location
            pdf_file = tmpdir_path / "document.pdf"
            if pdf_file.exists():
                shutil.copy(pdf_file, output_path)
                logger.info(f"✓ PDF generated using Tectonic: {output_path}")
                return True, None
            else:
                return False, "PDF file was not generated"
                
    except FileNotFoundError:
        return False, "tectonic not found"
    except subprocess.TimeoutExpired:
        return False, "Tectonic compilation timed out (>60s)"
    except Exception as e:
        return False, f"Tectonic compilation failed: {str(e)}"


def _compile_with_xelatex(
    latex_content: str,
    output_path: Path
) -> Tuple[bool, Optional[str]]:
    """Compile LaTeX using XeLaTeX (traditional engine)."""
    logger.info("Compiling LaTeX to PDF with XeLaTeX...")
    
    try:
        # Strip markdown code blocks if present (```latex ... ```)
        import re
        cleaned_content = latex_content.strip()
        
        # Remove markdown code block markers
        if cleaned_content.startswith('```'):
            # Remove opening ```latex or ```
            cleaned_content = re.sub(r'^```(?:latex)?\s*\n', '', cleaned_content)
            # Remove closing ```
            cleaned_content = re.sub(r'\n```\s*$', '', cleaned_content)
        
        # Also remove any leading commentary before \documentclass
        # Find the first \documentclass line
        doc_match = re.search(r'\\documentclass', cleaned_content)
        if doc_match:
            cleaned_content = cleaned_content[doc_match.start():]
        
        # Create temporary directory for LaTeX compilation
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            tex_file = tmpdir_path / "document.tex"
            
            # Write LaTeX content to file
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            # Set up environment with LaTeX in PATH
            env = os.environ.copy()
            
            # Add common LaTeX paths for different systems
            # These paths are tried in order, non-existent paths are harmless
            latex_paths = []
            
            # macOS paths
            if os.path.exists("/usr/local/texlive"):
                # Find all TeX Live installations
                texlive_base = Path("/usr/local/texlive")
                for year_dir in sorted(texlive_base.glob("*"), reverse=True):
                    bin_dir = year_dir / "bin"
                    if bin_dir.exists():
                        # Add all architecture-specific bin directories
                        for arch_dir in bin_dir.iterdir():
                            if arch_dir.is_dir():
                                latex_paths.append(str(arch_dir))
            
            latex_paths.extend([
                "/Library/TeX/texbin",  # macOS MacTeX
                "/usr/local/bin",        # Homebrew
            ])
            
            # Linux paths
            latex_paths.extend([
                "/usr/bin",              # Standard Linux
                "/usr/local/texlive/bin",
            ])
            
            # Windows paths (if running under WSL or similar)
            latex_paths.extend([
                "/mnt/c/Program Files/MiKTeX/miktex/bin/x64",
                "/mnt/c/texlive/bin/win32",
            ])
            
            # Prepend LaTeX paths to existing PATH
            current_path = env.get('PATH', '')
            env['PATH'] = ':'.join(latex_paths) + ':' + current_path
            
            # Compile with XeLaTeX (run twice for references)
            for i in range(2):
                result = subprocess.run(
                    ['xelatex', '-interaction=nonstopmode', '-halt-on-error', 'document.tex'],
                    cwd=tmpdir_path,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    env=env
                )
                
                if result.returncode != 0:
                    # Extract error from log
                    log_file = tmpdir_path / "document.log"
                    error_msg = "XeLaTeX compilation failed"
                    if log_file.exists():
                        with open(log_file) as f:
                            log_content = f.read()
                            # Extract the actual error
                            for line in log_content.split('\n'):
                                if line.startswith('!'):
                                    error_msg = line
                                    break
                    logger.error(f"❌ {error_msg}")
                    return False, f"LaTeX compilation error: {error_msg}"
            
            # Move PDF to output location
            pdf_file = tmpdir_path / "document.pdf"
            if pdf_file.exists():
                shutil.copy(pdf_file, output_path)
                logger.info(f"✓ PDF generated using XeLaTeX: {output_path}")
                return True, None
            else:
                return False, "PDF file was not generated"
                
    except FileNotFoundError:
        return False, "xelatex not found. Please install BasicTeX or TeX Live."
    except subprocess.TimeoutExpired:
        return False, "LaTeX compilation timed out (>60s)"
    except Exception as e:
        logger.error(f"❌ LaTeX compilation failed: {e}")
        return False, f"LaTeX compilation failed: {str(e)}"


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
