#!/usr/bin/env python3
"""
Research Agent Workflow Driver Script

This script demonstrates the complete research workflow:
1. Generate research report with tool use
2. Reflect and rewrite the report
3. Convert to HTML
4. Save outputs

Usage:
    python run_research_workflow.py "Your research topic here"
    python run_research_workflow.py --topic "quantum computing" --output-dir ./reports
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path if needed
sys.path.insert(0, str(Path(__file__).parent))

from research_agent import (
    generate_research_report_with_tools,
    reflection_and_rewrite,
    convert_report_to_html
)
from pdf_generator import PDFGenerator


def sanitize_filename(text: str, max_length: int = 50) -> str:
    """Convert text to safe filename."""
    # Remove special characters
    safe = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in text)
    # Replace spaces with underscores
    safe = safe.replace(' ', '_')
    # Truncate
    return safe[:max_length].strip('_')


def run_research_workflow(
    topic: str,
    output_dir: str = "./research_outputs",
    parallel: bool = True,
    save_intermediate: bool = True,
    generate_pdf: bool = True,
    verbose: bool = True
):
    """
    Run the complete research workflow.
    
    Args:
        topic: Research topic/question
        output_dir: Directory to save outputs
        parallel: Use parallel tool execution
        save_intermediate: Save intermediate outputs
        generate_pdf: Generate PDF output (default: True)
        verbose: Print progress
    
    Returns:
        dict: Results including all generated content
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp and safe filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = sanitize_filename(topic)
    base_filename = f"{timestamp}_{safe_topic}"
    
    results = {
        "topic": topic,
        "timestamp": timestamp,
        "files": {}
    }
    
    try:
        # Step 1: Generate research report
        if verbose:
            print("\n" + "="*80)
            print("STEP 1: Generating Research Report")
            print("="*80)
        
        preliminary_report = generate_research_report_with_tools(
            topic, 
            parallel=parallel,
            verbose=verbose
        )
        results["preliminary_report"] = preliminary_report
        
        if save_intermediate:
            report_file = output_path / f"{base_filename}_preliminary.txt"
            report_file.write_text(preliminary_report)
            results["files"]["preliminary_report"] = str(report_file)
            if verbose:
                print(f"\n💾 Saved preliminary report: {report_file}")
        
        # Step 2: Reflection and rewrite
        if verbose:
            print("\n" + "="*80)
            print("STEP 2: Reflecting and Rewriting")
            print("="*80)
        
        reflection_result = reflection_and_rewrite(preliminary_report)
        results["reflection"] = reflection_result["reflection"]
        results["revised_report"] = reflection_result["revised_report"]
        
        if save_intermediate:
            reflection_file = output_path / f"{base_filename}_reflection.txt"
            reflection_file.write_text(reflection_result["reflection"])
            results["files"]["reflection"] = str(reflection_file)
            
            revised_file = output_path / f"{base_filename}_revised.txt"
            revised_file.write_text(reflection_result["revised_report"])
            results["files"]["revised_report"] = str(revised_file)
            
            if verbose:
                print(f"💾 Saved reflection: {reflection_file}")
                print(f"💾 Saved revised report: {revised_file}")
        
        # Step 3: Convert to HTML
        if verbose:
            print("\n" + "="*80)
            print("STEP 3: Converting to HTML")
            print("="*80)
        
        html = convert_report_to_html(reflection_result["revised_report"])
        results["html"] = html
        
        html_file = output_path / f"{base_filename}_report.html"
        html_file.write_text(html)
        results["files"]["html"] = str(html_file)
        
        if verbose:
            print(f"💾 Saved HTML report: {html_file}")
        
        # Step 4: Convert to PDF (optional)
        if generate_pdf:
            if verbose:
                print("\n" + "="*80)
                print("STEP 4: Converting to PDF")
                print("="*80)
            
            try:
                pdf_generator = PDFGenerator()
                
                # Check if PDF tools are available
                if not pdf_generator.available_methods:
                    if verbose:
                        print("⚠️  No PDF conversion tools available")
                        print(pdf_generator.get_installation_instructions())
                else:
                    pdf_file = output_path / f"{base_filename}_report.pdf"
                    pdf_generator.html_to_pdf(html, pdf_file)
                    results["files"]["pdf"] = str(pdf_file)
                    
                    if verbose:
                        print(f"💾 Saved PDF report: {pdf_file}")
            
            except Exception as e:
                if verbose:
                    print(f"⚠️  PDF generation failed: {str(e)}")
                    print("   HTML version is still available")
                results["pdf_error"] = str(e)
        
        # Success summary
        if verbose:
            print("\n" + "="*80)
            print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
            print("="*80)
            print(f"\nTopic: {topic}")
            print(f"Output directory: {output_path}")
            print(f"\nGenerated files:")
            for key, filepath in results["files"].items():
                print(f"  • {key}: {filepath}")
        
        return results
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        results["error"] = str(e)
        return results


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Research Agent Workflow - Generate, reflect, and format research reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_research_workflow.py "quantum computing applications"
  python run_research_workflow.py --topic "CRISPR gene editing" --output-dir ./my_reports
  python run_research_workflow.py "climate change" --no-parallel --quiet
        """
    )
    
    parser.add_argument(
        "topic",
        nargs="?",
        help="Research topic or question"
    )
    parser.add_argument(
        "--topic", "-t",
        dest="topic_flag",
        help="Research topic (alternative to positional argument)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="./research_outputs",
        help="Output directory for generated files (default: ./research_outputs)"
    )
    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel tool execution"
    )
    parser.add_argument(
        "--no-save-intermediate",
        action="store_true",
        help="Don't save intermediate outputs (only save final HTML/PDF)"
    )
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Skip PDF generation (only generate HTML)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output"
    )
    
    args = parser.parse_args()
    
    # Get topic from either positional or flag argument
    topic = args.topic or args.topic_flag
    
    if not topic:
        parser.print_help()
        print("\n❌ Error: Please provide a research topic")
        sys.exit(1)
    
    # Run workflow
    results = run_research_workflow(
        topic=topic,
        output_dir=args.output_dir,
        parallel=not args.no_parallel,
        save_intermediate=not args.no_save_intermediate,
        generate_pdf=not args.no_pdf,
        verbose=not args.quiet
    )
    
    # Exit with error code if workflow failed
    if "error" in results:
        sys.exit(1)


if __name__ == "__main__":
    main()
