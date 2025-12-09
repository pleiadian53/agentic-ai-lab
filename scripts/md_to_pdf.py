#!/usr/bin/env python3
"""
Markdown to PDF Converter (v2) - Using Pandoc

This version uses pypandoc (Python wrapper for Pandoc) for robust markdown to LaTeX/PDF conversion.
Pandoc is the industry standard for document conversion and handles edge cases much better.

Installation:
    pip install pypandoc
    
    # macOS
    brew install pandoc
    
    # Linux
    sudo apt-get install pandoc

Usage:
    python scripts/md_to_pdf.py docs/llm/llm_tech_history.md
    python scripts/md_to_pdf.py docs/llm/llm_tech_history.md --output output/history.pdf
    python scripts/md_to_pdf.py docs/llm/llm_tech_history.md --latex-only
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

try:
    import pypandoc
    PYPANDOC_AVAILABLE = True
except ImportError:
    PYPANDOC_AVAILABLE = False


class PandocConverter:
    """Markdown to PDF converter using Pandoc."""
    
    @staticmethod
    def check_pandoc() -> Tuple[bool, Optional[str]]:
        """Check if pandoc is installed."""
        try:
            result = subprocess.run(['pandoc', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                return True, version
            return False, None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, None
    
    @staticmethod
    def check_xelatex() -> bool:
        """Check if XeLaTeX is installed."""
        try:
            result = subprocess.run(['xelatex', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    @staticmethod
    def convert_to_latex(input_file: Path, output_file: Path, 
                        title: str = "", author: str = "") -> Tuple[bool, Optional[str]]:
        """
        Convert markdown to LaTeX using Pandoc.
        
        Args:
            input_file: Input markdown file
            output_file: Output LaTeX file
            title: Document title (optional)
            author: Document author (optional)
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not PYPANDOC_AVAILABLE:
            return PandocConverter._convert_to_latex_cli(
                input_file, output_file, title, author
            )
        
        try:
            # Pandoc options
            extra_args = [
                '--standalone',
                '--toc',  # Table of contents
                '--number-sections',  # Number sections
                '-V', 'geometry:margin=1in',
                '-V', 'colorlinks=true',
                '-V', 'linkcolor=blue',
                '-V', 'urlcolor=blue',
            ]
            
            if title:
                extra_args.extend(['-V', f'title={title}'])
            if author:
                extra_args.extend(['-V', f'author={author}'])
            
            # Convert using pypandoc
            pypandoc.convert_file(
                str(input_file),
                'latex',
                outputfile=str(output_file),
                extra_args=extra_args
            )
            
            return True, None
            
        except Exception as e:
            return False, f"Pandoc conversion failed: {str(e)}"
    
    @staticmethod
    def _convert_to_latex_cli(input_file: Path, output_file: Path,
                              title: str = "", author: str = "") -> Tuple[bool, Optional[str]]:
        """Convert using pandoc CLI (fallback when pypandoc not available)."""
        cmd = [
            'pandoc',
            str(input_file),
            '-o', str(output_file),
            '--standalone',
            '--toc',
            '--number-sections',
            '-V', 'geometry:margin=1in',
            '-V', 'colorlinks=true',
            '-V', 'linkcolor=blue',
            '-V', 'urlcolor=blue',
        ]
        
        if title:
            cmd.extend(['-V', f'title={title}'])
        if author:
            cmd.extend(['-V', f'author={author}'])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return True, None
            return False, f"Pandoc error: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Pandoc conversion timed out"
        except Exception as e:
            return False, f"Pandoc conversion failed: {str(e)}"
    
    @staticmethod
    def convert_to_pdf(input_file: Path, output_file: Path,
                      title: str = "", author: str = "") -> Tuple[bool, Optional[str]]:
        """
        Convert markdown directly to PDF using Pandoc.
        
        Args:
            input_file: Input markdown file
            output_file: Output PDF file
            title: Document title (optional)
            author: Document author (optional)
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not PYPANDOC_AVAILABLE:
            return PandocConverter._convert_to_pdf_cli(
                input_file, output_file, title, author
            )
        
        try:
            # Pandoc options
            extra_args = [
                '--pdf-engine=xelatex',
                '--toc',
                '--number-sections',
                '-V', 'geometry:margin=1in',
                '-V', 'colorlinks=true',
                '-V', 'linkcolor=blue',
                '-V', 'urlcolor=blue',
            ]
            
            if title:
                extra_args.extend(['-V', f'title={title}'])
            if author:
                extra_args.extend(['-V', f'author={author}'])
            
            # Convert using pypandoc
            pypandoc.convert_file(
                str(input_file),
                'pdf',
                outputfile=str(output_file),
                extra_args=extra_args
            )
            
            return True, None
            
        except Exception as e:
            return False, f"PDF generation failed: {str(e)}"
    
    @staticmethod
    def _convert_to_pdf_cli(input_file: Path, output_file: Path,
                           title: str = "", author: str = "") -> Tuple[bool, Optional[str]]:
        """Convert to PDF using pandoc CLI (fallback)."""
        cmd = [
            'pandoc',
            str(input_file),
            '-o', str(output_file),
            '--pdf-engine=xelatex',
            '--toc',
            '--number-sections',
            '-V', 'geometry:margin=1in',
            '-V', 'colorlinks=true',
            '-V', 'linkcolor=blue',
            '-V', 'urlcolor=blue',
        ]
        
        if title:
            cmd.extend(['-V', f'title={title}'])
        if author:
            cmd.extend(['-V', f'author={author}'])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                return True, None
            return False, f"PDF generation error: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "PDF generation timed out"
        except Exception as e:
            return False, f"PDF generation failed: {str(e)}"


def main():
    parser = argparse.ArgumentParser(
        description='Convert Markdown to PDF using Pandoc',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert to PDF
  python scripts/md_to_pdf_v2.py docs/llm/llm_tech_history.md
  
  # Specify output path
  python scripts/md_to_pdf_v2.py docs/llm/llm_tech_history.md -o output/history.pdf
  
  # Generate LaTeX only
  python scripts/md_to_pdf_v2.py docs/llm/llm_tech_history.md --latex-only
  
  # Custom title and author
  python scripts/md_to_pdf_v2.py docs/llm/llm_tech_history.md \\
      --title "LLM History" --author "Your Name"

Requirements:
  - Pandoc: brew install pandoc (macOS) or sudo apt-get install pandoc (Linux)
  - XeLaTeX: For PDF generation (see docs/LATEX_SETUP.md)
  - pypandoc (optional): pip install pypandoc
        """
    )
    
    parser.add_argument('input', type=Path, help='Input markdown file')
    parser.add_argument('-o', '--output', type=Path,
                       help='Output file path (default: same name with .pdf/.tex extension)')
    parser.add_argument('--latex-only', action='store_true',
                       help='Generate LaTeX file only, do not compile to PDF')
    parser.add_argument('--title', type=str, default="",
                       help='Document title')
    parser.add_argument('--author', type=str, default="",
                       help='Document author')
    
    args = parser.parse_args()
    
    # Check dependencies
    pandoc_available, pandoc_version = PandocConverter.check_pandoc()
    if not pandoc_available:
        print("❌ Error: Pandoc is not installed", file=sys.stderr)
        print("\nInstallation instructions:", file=sys.stderr)
        print("  macOS:  brew install pandoc", file=sys.stderr)
        print("  Linux:  sudo apt-get install pandoc", file=sys.stderr)
        print("  Or see: https://pandoc.org/installing.html", file=sys.stderr)
        sys.exit(1)
    
    print(f"✓ Found {pandoc_version}")
    
    if not args.latex_only:
        if not PandocConverter.check_xelatex():
            print("⚠️  Warning: XeLaTeX not found. PDF generation may fail.", file=sys.stderr)
            print("   See docs/LATEX_SETUP.md for installation instructions.", file=sys.stderr)
    
    if not PYPANDOC_AVAILABLE:
        print("ℹ️  Note: pypandoc not installed, using pandoc CLI directly")
        print("   Install with: pip install pypandoc")
    
    # Validate input
    if not args.input.exists():
        print(f"❌ Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        if args.latex_only:
            output_path = args.input.with_suffix('.tex')
        else:
            output_path = args.input.with_suffix('.pdf')
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert
    print(f"📖 Reading: {args.input}")
    
    if args.latex_only:
        print("🔄 Converting to LaTeX...")
        success, error = PandocConverter.convert_to_latex(
            args.input, output_path, args.title, args.author
        )
        
        if success:
            print(f"✅ LaTeX generated: {output_path}")
            print(f"   Size: {output_path.stat().st_size / 1024:.1f} KB")
        else:
            print(f"❌ LaTeX generation failed:", file=sys.stderr)
            print(f"   {error}", file=sys.stderr)
            sys.exit(1)
    else:
        print("📄 Converting to PDF...")
        success, error = PandocConverter.convert_to_pdf(
            args.input, output_path, args.title, args.author
        )
        
        if success:
            print(f"✅ PDF generated: {output_path}")
            print(f"   Size: {output_path.stat().st_size / 1024:.1f} KB")
            
            # Also save LaTeX for reference
            tex_path = output_path.with_suffix('.tex')
            print(f"\n💡 Tip: Generate LaTeX with --latex-only to see intermediate output")
        else:
            print(f"❌ PDF generation failed:", file=sys.stderr)
            print(f"   {error}", file=sys.stderr)
            print(f"\n💡 Try generating LaTeX first: --latex-only", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
