# PDF Generation Setup

The research agent can automatically convert reports to PDF format. This requires installing one of several PDF conversion tools.

## Quick Setup (Recommended)

### Option 1: WeasyPrint (Best Quality)

**Recommended for most users** - Excellent CSS support and high-quality output.

```bash
# Activate your environment
mamba activate agentic-ai

# Install WeasyPrint
pip install weasyprint
```

### Option 2: pdfkit + wkhtmltopdf

Good alternative with wide compatibility.

```bash
# Install Python package
pip install pdfkit

# Install wkhtmltopdf
# macOS:
brew install wkhtmltopdf

# Linux (Ubuntu/Debian):
sudo apt-get install wkhtmltopdf

# Linux (Fedora/RHEL):
sudo dnf install wkhtmltopdf
```

### Option 3: Pandoc

Versatile document converter.

```bash
# macOS:
brew install pandoc

# Linux (Ubuntu/Debian):
sudo apt-get install pandoc texlive-latex-base texlive-latex-recommended

# Linux (Fedora/RHEL):
sudo dnf install pandoc texlive-scheme-basic
```

### Option 4: ReportLab (Basic)

Lightweight but limited HTML support.

```bash
pip install reportlab
```

## Verification

Check which PDF tools are available:

```python
from pdf_generator import PDFGenerator

generator = PDFGenerator()
print(generator.get_installation_instructions())
```

## Usage

### Command Line

```bash
# PDF generation is enabled by default
python run_research_workflow.py "quantum computing"

# Skip PDF generation
python run_research_workflow.py "quantum computing" --no-pdf
```

### Python API

```python
from pdf_generator import convert_html_to_pdf

# Convert HTML to PDF
convert_html_to_pdf(html_content, "output.pdf")
```

### Notebook

```python
from notebook_helpers import save_research_results

# PDF is generated automatically
results = quick_research("quantum computing")
save_research_results(results, "quantum_computing_2024")

# Skip PDF
save_research_results(results, "quantum_computing_2024", generate_pdf=False)
```

## Troubleshooting

### "No PDF conversion tools available"

Install at least one of the tools listed above. WeasyPrint is recommended for best results.

### WeasyPrint Installation Issues

On some systems, WeasyPrint requires additional dependencies:

```bash
# macOS (if you get errors):
brew install cairo pango gdk-pixbuf libffi

# Linux (Ubuntu/Debian):
sudo apt-get install python3-dev python3-pip python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# Then reinstall:
pip install --upgrade weasyprint
```

### wkhtmltopdf Not Found

Make sure wkhtmltopdf is in your PATH:

```bash
# Check if installed:
which wkhtmltopdf

# If not found, reinstall or add to PATH
```

### Pandoc LaTeX Errors

Pandoc requires LaTeX for PDF generation. Install a LaTeX distribution:

```bash
# macOS:
brew install --cask mactex-no-gui

# Linux:
sudo apt-get install texlive-full  # Full install (large)
# or
sudo apt-get install texlive-latex-base texlive-latex-recommended  # Minimal
```

## PDF Quality Comparison

| Tool | Quality | CSS Support | Speed | File Size |
|------|---------|-------------|-------|-----------|
| **WeasyPrint** | ⭐⭐⭐⭐⭐ | Excellent | Fast | Medium |
| **pdfkit** | ⭐⭐⭐⭐ | Very Good | Medium | Medium |
| **Pandoc** | ⭐⭐⭐⭐ | Good | Slow | Small |
| **ReportLab** | ⭐⭐⭐ | Limited | Very Fast | Small |

## Recommendation

For research reports with citations, formatting, and links:
1. **First choice**: WeasyPrint
2. **Second choice**: pdfkit
3. **Fallback**: Pandoc

## Advanced Configuration

### Custom PDF Styling

The PDF generator automatically adds print-friendly CSS. To customize:

```python
from pdf_generator import PDFGenerator

generator = PDFGenerator()

# Your HTML with custom styles
html_with_styles = """
<html>
<head>
    <style>
        @page { size: A4; margin: 2cm; }
        body { font-family: 'Times New Roman', serif; }
        h1 { color: #2c3e50; }
    </style>
</head>
<body>
    <h1>My Report</h1>
    <p>Content here...</p>
</body>
</html>
"""

generator.html_to_pdf(html_with_styles, "custom_report.pdf")
```

### Force Specific Method

```python
# Use a specific conversion method
generator.html_to_pdf(html, "output.pdf", method="weasyprint")
```

## Support

If you encounter issues:
1. Check that at least one PDF tool is installed
2. Verify the tool works independently (e.g., `wkhtmltopdf --version`)
3. Try a different PDF tool
4. The workflow will continue even if PDF generation fails - HTML output is always available
