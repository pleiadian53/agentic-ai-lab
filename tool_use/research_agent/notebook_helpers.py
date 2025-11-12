"""
Notebook Helper Functions

Convenience functions for using the research agent in Jupyter notebooks.
"""

from IPython.display import display, HTML
from research_agent import (
    generate_research_report_with_tools,
    reflection_and_rewrite,
    convert_report_to_html
)
from pdf_generator import PDFGenerator
import inspect_utils


def quick_research(topic: str, parallel: bool = True, show_html: bool = True):
    """
    Quick research workflow for notebooks - all steps in one function.
    
    Args:
        topic: Research topic/question
        parallel: Use parallel tool execution (default: True)
        show_html: Display HTML output in notebook (default: True)
    
    Returns:
        dict: All results (preliminary_report, reflection, revised_report, html)
    """
    print(f"🔬 Researching: {topic}\n")
    
    # Step 1: Generate report
    print("="*80)
    print("STEP 1: Generating Research Report")
    print("="*80)
    preliminary_report = generate_research_report_with_tools(topic, parallel=parallel)
    
    # Step 2: Reflect and rewrite
    print("\n" + "="*80)
    print("STEP 2: Reflecting and Rewriting")
    print("="*80)
    reflection_result = reflection_and_rewrite(preliminary_report)
    
    # Display reflection
    inspect_utils.inspect_reflection_output(reflection_result, max_length=1000)
    
    # Step 3: Convert to HTML
    print("\n" + "="*80)
    print("STEP 3: Converting to HTML")
    print("="*80)
    html = convert_report_to_html(reflection_result["revised_report"])
    
    print("✅ HTML generated")
    
    # Display HTML
    if show_html:
        print("\n" + "="*80)
        print("FINAL REPORT (HTML)")
        print("="*80 + "\n")
        display(HTML(html))
    
    return {
        "preliminary_report": preliminary_report,
        "reflection": reflection_result["reflection"],
        "revised_report": reflection_result["revised_report"],
        "html": html
    }


def research_and_compare(topic: str, parallel: bool = True):
    """
    Research workflow with side-by-side comparison of preliminary vs revised.
    
    Args:
        topic: Research topic/question
        parallel: Use parallel tool execution
    
    Returns:
        dict: All results
    """
    # Generate preliminary report
    print(f"🔬 Researching: {topic}\n")
    preliminary_report = generate_research_report_with_tools(topic, parallel=parallel)
    
    # Reflect and rewrite
    reflection_result = reflection_and_rewrite(preliminary_report)
    
    # Display comparison
    print("\n" + "="*80)
    print("COMPARISON: Preliminary vs Revised")
    print("="*80 + "\n")
    
    inspect_utils.compare_reports(preliminary_report, reflection_result)
    
    # Display both reports
    inspect_utils.display_research_report(preliminary_report, title="Preliminary Report")
    inspect_utils.display_research_report(
        reflection_result["revised_report"], 
        title="Revised Report"
    )
    
    return {
        "preliminary_report": preliminary_report,
        "reflection": reflection_result["reflection"],
        "revised_report": reflection_result["revised_report"]
    }


def preview_html_file(filepath: str):
    """
    Preview an HTML file in Jupyter notebook.
    
    Args:
        filepath: Path to HTML file (relative or absolute)
    """
    from pathlib import Path
    
    filepath = Path(filepath)
    
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return
    
    html_content = filepath.read_text()
    display(HTML(html_content))
    print(f"📄 Previewing: {filepath.name}")


def open_html_in_browser(filepath: str):
    """
    Open an HTML file in the default web browser.
    
    Args:
        filepath: Path to HTML file (relative or absolute)
    """
    from pathlib import Path
    import webbrowser
    
    filepath = Path(filepath).resolve()
    
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return
    
    webbrowser.open(f"file://{filepath}")
    print(f"🌐 Opened in browser: {filepath.name}")


def save_research_results(results: dict, filename_base: str, generate_pdf: bool = True):
    """
    Save research results to files.
    
    Args:
        results: Dict from quick_research() or research_and_compare()
        filename_base: Base filename (without extension)
        generate_pdf: Also generate PDF from HTML (default: True)
    """
    from pathlib import Path
    
    output_dir = Path("./research_outputs")
    output_dir.mkdir(exist_ok=True)
    
    files_saved = []
    
    # Save preliminary report
    if "preliminary_report" in results:
        path = output_dir / f"{filename_base}_preliminary.txt"
        path.write_text(results["preliminary_report"])
        files_saved.append(str(path))
    
    # Save reflection
    if "reflection" in results:
        path = output_dir / f"{filename_base}_reflection.txt"
        path.write_text(results["reflection"])
        files_saved.append(str(path))
    
    # Save revised report
    if "revised_report" in results:
        path = output_dir / f"{filename_base}_revised.txt"
        path.write_text(results["revised_report"])
        files_saved.append(str(path))
    
    # Save HTML
    if "html" in results:
        path = output_dir / f"{filename_base}_report.html"
        path.write_text(results["html"])
        files_saved.append(str(path))
        
        # Generate PDF from HTML
        if generate_pdf:
            try:
                pdf_generator = PDFGenerator()
                if pdf_generator.available_methods:
                    pdf_path = output_dir / f"{filename_base}_report.pdf"
                    pdf_generator.html_to_pdf(results["html"], pdf_path)
                    files_saved.append(str(pdf_path))
                    print("📄 PDF generated successfully")
                else:
                    print("⚠️  PDF generation skipped (no tools available)")
                    print(pdf_generator.get_installation_instructions())
            except Exception as e:
                print(f"⚠️  PDF generation failed: {str(e)}")
    
    print(f"\n💾 Saved {len(files_saved)} file(s) to {output_dir}/")
    for f in files_saved:
        print(f"  • {f}")
    
    return files_saved
