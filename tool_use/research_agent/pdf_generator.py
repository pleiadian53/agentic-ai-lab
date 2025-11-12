"""
PDF Generation for Research Reports

This module provides utilities to convert research reports to PDF format.
Supports multiple conversion methods with fallbacks.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Union


class PDFGenerator:
    """
    Generate PDF documents from research reports.
    Supports multiple conversion methods with automatic fallback.
    """
    
    def __init__(self):
        """Initialize PDF generator and detect available tools."""
        self.available_methods = self._detect_available_methods()
    
    def _detect_available_methods(self) -> list:
        """Detect which PDF conversion methods are available."""
        methods = []
        
        # Check for weasyprint
        try:
            import weasyprint
            methods.append("weasyprint")
        except ImportError:
            pass
        
        # Check for pdfkit/wkhtmltopdf
        try:
            import pdfkit
            # Check if wkhtmltopdf is installed
            try:
                subprocess.run(["wkhtmltopdf", "--version"], 
                             capture_output=True, check=True)
                methods.append("pdfkit")
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        except ImportError:
            pass
        
        # Check for reportlab
        try:
            import reportlab
            methods.append("reportlab")
        except ImportError:
            pass
        
        # Check for pandoc
        try:
            subprocess.run(["pandoc", "--version"], 
                         capture_output=True, check=True)
            methods.append("pandoc")
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return methods
    
    def html_to_pdf(self, html_content: str, output_path: Union[str, Path], 
                    method: Optional[str] = None) -> Path:
        """
        Convert HTML content to PDF.
        
        Args:
            html_content: HTML string to convert
            output_path: Path where PDF should be saved
            method: Specific method to use (None = auto-select best available)
        
        Returns:
            Path: Path to generated PDF file
            
        Raises:
            RuntimeError: If no conversion method is available
            Exception: If conversion fails
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.available_methods:
            raise RuntimeError(
                "No PDF conversion tools available. Please install one of:\n"
                "  - weasyprint: pip install weasyprint\n"
                "  - pdfkit: pip install pdfkit (requires wkhtmltopdf)\n"
                "  - reportlab: pip install reportlab\n"
                "  - pandoc: brew install pandoc (macOS) or apt-get install pandoc (Linux)"
            )
        
        # Select method
        if method and method in self.available_methods:
            selected_method = method
        else:
            # Auto-select best available method
            # Priority: weasyprint > pdfkit > pandoc > reportlab
            priority = ["weasyprint", "pdfkit", "pandoc", "reportlab"]
            selected_method = next((m for m in priority if m in self.available_methods), 
                                  self.available_methods[0])
        
        print(f"📄 Converting to PDF using {selected_method}...")
        
        # Convert using selected method
        if selected_method == "weasyprint":
            return self._convert_weasyprint(html_content, output_path)
        elif selected_method == "pdfkit":
            return self._convert_pdfkit(html_content, output_path)
        elif selected_method == "pandoc":
            return self._convert_pandoc(html_content, output_path)
        elif selected_method == "reportlab":
            return self._convert_reportlab(html_content, output_path)
        else:
            raise RuntimeError(f"Unknown conversion method: {selected_method}")
    
    def _convert_weasyprint(self, html_content: str, output_path: Path) -> Path:
        """Convert using WeasyPrint (best quality, CSS support)."""
        from weasyprint import HTML, CSS
        
        # Add default styling if not present
        if "<style>" not in html_content.lower():
            html_content = self._add_default_pdf_styles(html_content)
        
        HTML(string=html_content).write_pdf(output_path)
        return output_path
    
    def _convert_pdfkit(self, html_content: str, output_path: Path) -> Path:
        """Convert using pdfkit/wkhtmltopdf."""
        import pdfkit
        
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        pdfkit.from_string(html_content, str(output_path), options=options)
        return output_path
    
    def _convert_pandoc(self, html_content: str, output_path: Path) -> Path:
        """Convert using pandoc."""
        # Save HTML to temp file
        temp_html = output_path.parent / f"{output_path.stem}_temp.html"
        temp_html.write_text(html_content)
        
        try:
            subprocess.run([
                "pandoc",
                str(temp_html),
                "-o", str(output_path),
                "--pdf-engine=pdflatex",
                "-V", "geometry:margin=1in"
            ], check=True, capture_output=True)
        finally:
            # Clean up temp file
            if temp_html.exists():
                temp_html.unlink()
        
        return output_path
    
    def _convert_reportlab(self, html_content: str, output_path: Path) -> Path:
        """Convert using reportlab (basic HTML support)."""
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from html.parser import HTMLParser
        
        # Simple HTML parser for reportlab
        class SimpleHTMLParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text_parts = []
            
            def handle_data(self, data):
                self.text_parts.append(data.strip())
        
        parser = SimpleHTMLParser()
        parser.feed(html_content)
        text = " ".join(parser.text_parts)
        
        # Create PDF
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Split into paragraphs
        for para in text.split('\n\n'):
            if para.strip():
                story.append(Paragraph(para, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        
        doc.build(story)
        return output_path
    
    def _add_default_pdf_styles(self, html_content: str) -> str:
        """Add default PDF-friendly styles to HTML."""
        default_styles = """
        <style>
            @page {
                size: letter;
                margin: 1in;
            }
            body {
                font-family: 'Georgia', 'Times New Roman', serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #333;
                max-width: 100%;
            }
            h1 {
                font-size: 24pt;
                margin-top: 0;
                margin-bottom: 12pt;
                color: #2c3e50;
                page-break-after: avoid;
            }
            h2 {
                font-size: 18pt;
                margin-top: 18pt;
                margin-bottom: 10pt;
                color: #34495e;
                page-break-after: avoid;
            }
            h3 {
                font-size: 14pt;
                margin-top: 14pt;
                margin-bottom: 8pt;
                color: #34495e;
                page-break-after: avoid;
            }
            p {
                margin-bottom: 10pt;
                text-align: justify;
            }
            a {
                color: #3498db;
                text-decoration: none;
            }
            code, pre {
                font-family: 'Courier New', monospace;
                background-color: #f5f5f5;
                padding: 2pt 4pt;
                font-size: 10pt;
            }
            blockquote {
                margin-left: 20pt;
                margin-right: 20pt;
                font-style: italic;
                border-left: 3pt solid #3498db;
                padding-left: 10pt;
            }
            ul, ol {
                margin-bottom: 10pt;
            }
            li {
                margin-bottom: 5pt;
            }
        </style>
        """
        
        # Insert styles before </head> or at the beginning
        if "</head>" in html_content:
            html_content = html_content.replace("</head>", f"{default_styles}</head>")
        elif "<body>" in html_content:
            html_content = html_content.replace("<body>", f"<head>{default_styles}</head><body>")
        else:
            html_content = f"<html><head>{default_styles}</head><body>{html_content}</body></html>"
        
        return html_content
    
    def get_installation_instructions(self) -> str:
        """Get installation instructions for PDF tools."""
        if self.available_methods:
            return f"Available PDF methods: {', '.join(self.available_methods)}"
        
        return """
No PDF conversion tools found. Install one of the following:

1. WeasyPrint (Recommended - best quality):
   pip install weasyprint

2. pdfkit (requires wkhtmltopdf):
   pip install pdfkit
   # macOS: brew install wkhtmltopdf
   # Linux: apt-get install wkhtmltopdf

3. Pandoc:
   # macOS: brew install pandoc
   # Linux: apt-get install pandoc

4. ReportLab (basic support):
   pip install reportlab
"""


# Convenience function
def convert_html_to_pdf(html_content: str, output_path: Union[str, Path]) -> Path:
    """
    Simple function to convert HTML to PDF.
    
    Args:
        html_content: HTML string
        output_path: Where to save PDF
    
    Returns:
        Path to generated PDF
    """
    generator = PDFGenerator()
    return generator.html_to_pdf(html_content, output_path)
