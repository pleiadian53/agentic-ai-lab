#!/usr/bin/env python3
"""
Basic Usage Example: Enhanced Research Agent with Evaluation

This example demonstrates the simplest way to use the evaluated research agent.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from eval.research_agent import EvaluatedResearchAgent
from eval import ACADEMIC_DOMAINS


def main():
    print("="*80)
    print("BASIC USAGE: Enhanced Research Agent with Evaluation")
    print("="*80)
    
    # Initialize agent with default settings
    agent = EvaluatedResearchAgent(
        preferred_domains=ACADEMIC_DOMAINS,
        min_source_ratio=0.5,  # Require 50% from preferred domains
        max_retries=2,
        verbose=True
    )
    
    # Research topic
    topic = "recent advances in quantum error correction"
    
    print(f"\n📝 Research Topic: {topic}\n")
    
    # Generate research report with evaluation
    results = agent.generate_report(topic, evaluate_sources=True)
    
    # Display results
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    
    print(f"\n📊 Evaluation Summary:")
    eval_result = results['evaluation']
    print(f"   Status: {eval_result.status}")
    print(f"   Total sources: {eval_result.total_sources}")
    print(f"   Preferred sources: {eval_result.preferred_count} ({eval_result.preferred_ratio:.1%})")
    print(f"   Retries needed: {results['retry_count']}")
    
    if eval_result.preferred_sources:
        print(f"\n✅ Preferred domains found:")
        for source in eval_result.preferred_sources[:5]:
            print(f"   - {source.domain}")
    
    if eval_result.other_sources:
        print(f"\n⚠️  Other domains:")
        for source in eval_result.other_sources[:5]:
            print(f"   - {source.domain}")
    
    print(f"\n📄 Research Report Preview:")
    print("-" * 80)
    print(results['report'][:500] + "...")
    print("-" * 80)
    
    # Save output
    output_file = Path("basic_research_output.txt")
    output_file.write_text(results['report'])
    print(f"\n💾 Full report saved to: {output_file}")
    
    # Save evaluation
    eval_file = Path("basic_evaluation.md")
    eval_file.write_text(eval_result.to_markdown())
    print(f"💾 Evaluation saved to: {eval_file}")


if __name__ == "__main__":
    main()
