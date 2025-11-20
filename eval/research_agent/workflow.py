#!/usr/bin/env python3
"""
Enhanced Research Workflow with Integrated Evaluation

This module provides a complete workflow that combines research generation,
component-wise evaluation, reflection, and output formatting.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from .agent import EvaluatedResearchAgent
from ..config import ACADEMIC_DOMAINS, BIOLOGY_FOCUSED_DOMAINS
from ..visualize import display_evaluation_result


def sanitize_filename(text: str, max_length: int = 50) -> str:
    """Convert text to safe filename."""
    safe = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in text)
    safe = safe.replace(' ', '_')
    return safe[:max_length].strip('_')


def run_evaluated_workflow(
    topic: str,
    output_dir: str = "./evaluated_research_outputs",
    preferred_domains: Optional[list] = None,
    min_source_ratio: float = 0.5,
    max_retries: int = 2,
    save_intermediate: bool = True,
    generate_html: bool = True,
    run_reflection: bool = True,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Run the complete evaluated research workflow.
    
    This workflow includes:
    1. Research report generation with tool use
    2. Component-wise source evaluation
    3. Automatic retry if source quality is poor
    4. Optional reflection with evaluation feedback
    5. HTML conversion
    6. Comprehensive evaluation metrics
    
    Args:
        topic: Research topic/question
        output_dir: Directory to save outputs
        preferred_domains: List of preferred domains (default: ACADEMIC_DOMAINS)
        min_source_ratio: Minimum ratio of preferred sources (0.0-1.0)
        max_retries: Maximum retries if source quality is poor
        save_intermediate: Save intermediate outputs
        generate_html: Generate HTML output
        run_reflection: Run reflection and rewrite step
        verbose: Print progress
    
    Returns:
        dict: Results including all generated content and evaluation metrics
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
        "files": {},
        "config": {
            "preferred_domains": preferred_domains or ACADEMIC_DOMAINS,
            "min_source_ratio": min_source_ratio,
            "max_retries": max_retries
        }
    }
    
    try:
        # Initialize agent
        agent = EvaluatedResearchAgent(
            preferred_domains=preferred_domains,
            min_source_ratio=min_source_ratio,
            max_retries=max_retries,
            verbose=verbose
        )
        
        # Step 1: Generate research report with evaluation
        if verbose:
            print("\n" + "="*80)
            print("STEP 1: Generating Research Report with Evaluation")
            print("="*80)
        
        research_result = agent.generate_report(
            topic,
            evaluate_sources=True
        )
        
        results["preliminary_report"] = research_result["report"]
        results["evaluation"] = research_result["evaluation"]
        results["tool_calls"] = research_result["tool_calls"]
        results["retry_count"] = research_result.get("retry_count", 0)
        
        # Display evaluation
        if verbose:
            print("\n" + "="*80)
            print("📊 SOURCE QUALITY EVALUATION")
            print("="*80)
            eval_result = research_result["evaluation"]
            print(f"Status: {eval_result.status}")
            print(f"Total sources: {eval_result.total_sources}")
            print(f"Preferred sources: {eval_result.preferred_count} ({eval_result.preferred_ratio:.1%})")
            print(f"Retries needed: {results['retry_count']}")
            
            if eval_result.preferred_sources:
                print(f"\n✅ Preferred domains found:")
                for source in eval_result.preferred_sources[:5]:
                    print(f"   - {source.domain}")
            
            if eval_result.other_sources:
                print(f"\n⚠️  Other domains:")
                for source in eval_result.other_sources[:5]:
                    print(f"   - {source.domain}")
        
        # Save preliminary report
        if save_intermediate:
            report_file = output_path / f"{base_filename}_preliminary.txt"
            report_file.write_text(research_result["report"])
            results["files"]["preliminary_report"] = str(report_file)
            
            # Save evaluation report
            eval_file = output_path / f"{base_filename}_evaluation.md"
            eval_file.write_text(research_result["evaluation"].to_markdown())
            results["files"]["evaluation"] = str(eval_file)
            
            if verbose:
                print(f"\n💾 Saved preliminary report: {report_file}")
                print(f"💾 Saved evaluation: {eval_file}")
        
        # Step 2: Reflection and rewrite (optional)
        if run_reflection:
            if verbose:
                print("\n" + "="*80)
                print("STEP 2: Reflecting and Rewriting with Evaluation Feedback")
                print("="*80)
            
            reflection_result = agent.reflect_and_rewrite(
                research_result["report"],
                evaluation=research_result["evaluation"]
            )
            
            results["reflection"] = reflection_result["reflection"]
            results["revised_report"] = reflection_result["revised_report"]
            
            # Evaluate revised report
            revised_evaluation = agent.evaluator.evaluate_text(
                reflection_result["revised_report"]
            )
            results["revised_evaluation"] = revised_evaluation
            
            if verbose:
                print(f"\n📊 Revised Report Evaluation:")
                print(f"   Status: {revised_evaluation.status}")
                print(f"   Preferred: {revised_evaluation.preferred_count}/{revised_evaluation.total_sources}")
                print(f"   Ratio: {revised_evaluation.preferred_ratio:.1%}")
            
            if save_intermediate:
                reflection_file = output_path / f"{base_filename}_reflection.txt"
                reflection_file.write_text(reflection_result["reflection"])
                results["files"]["reflection"] = str(reflection_file)
                
                revised_file = output_path / f"{base_filename}_revised.txt"
                revised_file.write_text(reflection_result["revised_report"])
                results["files"]["revised_report"] = str(revised_file)
                
                revised_eval_file = output_path / f"{base_filename}_revised_evaluation.md"
                revised_eval_file.write_text(revised_evaluation.to_markdown())
                results["files"]["revised_evaluation"] = str(revised_eval_file)
                
                if verbose:
                    print(f"💾 Saved reflection: {reflection_file}")
                    print(f"💾 Saved revised report: {revised_file}")
                    print(f"💾 Saved revised evaluation: {revised_eval_file}")
            
            # Use revised report for HTML generation
            final_report = reflection_result["revised_report"]
        else:
            final_report = research_result["report"]
        
        # Step 3: Convert to HTML (optional)
        if generate_html:
            if verbose:
                print("\n" + "="*80)
                print("STEP 3: Converting to HTML")
                print("="*80)
            
            html = agent.convert_to_html(final_report)
            results["html"] = html
            
            html_file = output_path / f"{base_filename}_report.html"
            html_file.write_text(html)
            results["files"]["html"] = str(html_file)
            
            if verbose:
                print(f"💾 Saved HTML report: {html_file}")
        
        # Success summary
        if verbose:
            print("\n" + "="*80)
            print("✅ EVALUATED WORKFLOW COMPLETED SUCCESSFULLY")
            print("="*80)
            print(f"\nTopic: {topic}")
            print(f"Output directory: {output_path}")
            print(f"\n📊 Final Evaluation Summary:")
            final_eval = results.get("revised_evaluation", results["evaluation"])
            print(f"   Status: {final_eval.status}")
            print(f"   Source Quality: {final_eval.preferred_ratio:.1%} preferred")
            print(f"   Retries: {results['retry_count']}")
            print(f"\nGenerated files:")
            for key, filepath in results["files"].items():
                print(f"  • {key}: {filepath}")
        
        return results
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        results["error"] = str(e)
        import traceback
        results["traceback"] = traceback.format_exc()
        return results


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Enhanced Research Agent with Integrated Evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python -m eval.research_agent.workflow "quantum computing applications"
  
  # With custom domain set
  python -m eval.research_agent.workflow "CRISPR gene editing" --domains biology
  
  # High quality threshold
  python -m eval.research_agent.workflow "climate change" --min-ratio 0.7
  
  # Skip reflection for faster results
  python -m eval.research_agent.workflow "AI safety" --no-reflection
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
        default="./evaluated_research_outputs",
        help="Output directory for generated files (default: ./evaluated_research_outputs)"
    )
    parser.add_argument(
        "--domains", "-d",
        choices=["academic", "biology", "custom"],
        default="academic",
        help="Preferred domain set: academic, biology, or custom (default: academic)"
    )
    parser.add_argument(
        "--min-ratio", "-r",
        type=float,
        default=0.5,
        help="Minimum ratio of preferred sources (0.0-1.0, default: 0.5)"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=2,
        help="Maximum retries if source quality is poor (default: 2)"
    )
    parser.add_argument(
        "--no-reflection",
        action="store_true",
        help="Skip reflection and rewrite step"
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Skip HTML generation"
    )
    parser.add_argument(
        "--no-save-intermediate",
        action="store_true",
        help="Don't save intermediate outputs"
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
    
    # Select domain set
    if args.domains == "biology":
        preferred_domains = BIOLOGY_FOCUSED_DOMAINS
    elif args.domains == "academic":
        preferred_domains = ACADEMIC_DOMAINS
    else:
        preferred_domains = None  # Will use default
    
    # Run workflow
    results = run_evaluated_workflow(
        topic=topic,
        output_dir=args.output_dir,
        preferred_domains=preferred_domains,
        min_source_ratio=args.min_ratio,
        max_retries=args.max_retries,
        save_intermediate=not args.no_save_intermediate,
        generate_html=not args.no_html,
        run_reflection=not args.no_reflection,
        verbose=not args.quiet
    )
    
    # Exit with error code if workflow failed
    if "error" in results:
        sys.exit(1)


if __name__ == "__main__":
    main()
