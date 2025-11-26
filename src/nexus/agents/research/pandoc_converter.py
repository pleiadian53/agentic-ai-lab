"""
Pandoc-based LaTeX to Markdown converter with fallback to custom converter.

This module uses Pandoc (industry standard) for high-quality LaTeX to Markdown
conversion, with automatic fallback to the custom converter if Pandoc is not installed.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, Tuple


def is_pandoc_available() -> bool:
    """Check if Pandoc is installed and available."""
    return shutil.which("pandoc") is not None


def convert_with_pandoc(
    latex_content: str,
    output_path: Path,
    math_renderer: str = "mathjax"
) -> Tuple[bool, Optional[str]]:
    """
    Convert LaTeX to Markdown using Pandoc.
    
    Args:
        latex_content: Full LaTeX document source
        output_path: Path to save Markdown file
        math_renderer: Math rendering method ('mathjax', 'katex', 'webtex')
        
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    if not is_pandoc_available():
        return False, "Pandoc not installed"
    
    try:
        # Create temporary LaTeX file
        temp_tex = output_path.with_suffix('.temp.tex')
        with open(temp_tex, 'w') as f:
            f.write(latex_content)
        
        # Build pandoc command
        # Note: GitHub supports $...$ and $$...$$ for LaTeX math
        cmd = [
            "pandoc",
            str(temp_tex),
            "-o", str(output_path),
            "--wrap=none",        # Don't wrap lines
            "--standalone",       # Include header/footer
            "--from=latex",
            "--to=gfm",          # GitHub Flavored Markdown
            "--webtex",          # Convert math to images (fallback for complex equations)
        ]
        
        # Run pandoc
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Clean up temp file
        if temp_tex.exists():
            temp_tex.unlink()
        
        if result.returncode != 0:
            return False, f"Pandoc error: {result.stderr}"
        
        # Add GitHub header note
        _add_github_header(output_path)
        
        return True, None
        
    except subprocess.TimeoutExpired:
        return False, "Pandoc conversion timed out"
    except Exception as e:
        return False, f"Conversion error: {str(e)}"


def _add_github_header(md_path: Path):
    """Add a header note to the Markdown file."""
    header = """> **Note**: This is a GitHub-friendly Markdown preview generated with Pandoc.
> For the full report with properly rendered equations, see the [PDF version](report_*.pdf).

---

"""
    
    # Read existing content
    with open(md_path, 'r') as f:
        content = f.read()
    
    # Prepend header
    with open(md_path, 'w') as f:
        f.write(header + content)


def generate_markdown_preview(
    latex_content: str,
    output_path: Path,
    prefer_pandoc: bool = True
) -> Tuple[bool, str]:
    """
    Generate a Markdown preview from LaTeX content.
    
    Uses Pandoc if available, falls back to custom converter otherwise.
    
    Args:
        latex_content: Full LaTeX document source
        output_path: Path to save Markdown file
        prefer_pandoc: If True, try Pandoc first (default: True)
        
    Returns:
        Tuple of (success: bool, method_used: str)
    """
    
    if prefer_pandoc and is_pandoc_available():
        # Try Pandoc first
        success, error = convert_with_pandoc(latex_content, output_path)
        if success:
            return True, "pandoc"
        else:
            print(f"⚠️  Pandoc conversion failed: {error}")
            print(f"   Falling back to custom converter...")
    
    # Fallback to custom converter
    try:
        from . import latex_to_markdown
        success = latex_to_markdown.generate_markdown_preview(latex_content, output_path)
        if success:
            return True, "custom"
        else:
            return False, "failed"
    except Exception as e:
        print(f"❌ Custom converter also failed: {e}")
        return False, "failed"


def check_pandoc_installation() -> dict:
    """
    Check Pandoc installation and return version info.
    
    Returns:
        dict with keys:
            - installed: bool
            - version: str (if installed)
            - path: str (if installed)
    """
    if not is_pandoc_available():
        return {
            "installed": False,
            "version": None,
            "path": None,
            "install_instructions": {
                "macOS": "brew install pandoc",
                "Ubuntu/Debian": "sudo apt-get install pandoc",
                "Windows": "choco install pandoc",
                "Other": "https://pandoc.org/installing.html"
            }
        }
    
    try:
        # Get version
        result = subprocess.run(
            ["pandoc", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        version_line = result.stdout.split('\n')[0]
        version = version_line.split()[-1] if version_line else "unknown"
        
        # Get path
        pandoc_path = shutil.which("pandoc")
        
        return {
            "installed": True,
            "version": version,
            "path": pandoc_path
        }
        
    except Exception as e:
        return {
            "installed": True,
            "version": "unknown",
            "path": shutil.which("pandoc"),
            "error": str(e)
        }


# Convenience function for backward compatibility
def latex_to_markdown_pandoc(latex_content: str, output_path: Path) -> bool:
    """
    Convert LaTeX to Markdown using Pandoc (backward compatibility wrapper).
    
    Args:
        latex_content: Full LaTeX document source
        output_path: Path to save Markdown file
        
    Returns:
        True if successful, False otherwise
    """
    success, _ = generate_markdown_preview(latex_content, output_path, prefer_pandoc=True)
    return success
