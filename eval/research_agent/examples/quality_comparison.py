#!/usr/bin/env python3
"""
Quality Comparison: Base Agent vs. Evaluated Agent

This example compares the source quality between the base research agent
and the evaluated research agent with automatic quality improvement.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from eval.research_agent import EvaluatedResearchAgent
from eval import DomainEvaluator, ACADEMIC_DOMAINS


def simulate_base_agent_research(topic: str) -> str:
    """
    Simulate base agent (no evaluation, no retry).
    In reality, this would call tool_use.research_agent.
    """
    print(f"\n🔵 BASE AGENT (No Evaluation)")
    print(f"   Topic: {topic}")
    print(f"   - Generates report without quality checks")
    print(f"   - No retry mechanism")
    print(f"   - No source evaluation")
    
    # For demonstration, we'll use the evaluated agent but with no retries
    agent = EvaluatedResearchAgent(
        preferred_domains=ACADEMIC_DOMAINS,
        max_retries=0,  # No retries
        verbose=False
    )
    
    results = agent.generate_report(topic, evaluate_sources=True)
    return results


def run_evaluated_agent_research(topic: str) -> dict:
    """Run evaluated agent with quality improvement."""
    print(f"\n🟢 EVALUATED AGENT (With Quality Improvement)")
    print(f"   Topic: {topic}")
    print(f"   - Evaluates source quality")
    print(f"   - Retries if quality is poor")
    print(f"   - Provides quality metrics")
    
    agent = EvaluatedResearchAgent(
        preferred_domains=ACADEMIC_DOMAINS,
        min_source_ratio=0.5,
        max_retries=2,
        verbose=False
    )
    
    results = agent.generate_report(topic, evaluate_sources=True)
    return results


def main():
    print("="*80)
    print("QUALITY COMPARISON: Base Agent vs. Evaluated Agent")
    print("="*80)
    
    # Test topics
    topics = [
        "recent advances in quantum computing",
        "CRISPR gene editing applications",
        "climate change mitigation strategies"
    ]
    
    for i, topic in enumerate(topics, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(topics)}: {topic}")
        print(f"{'='*80}")
        
        # Run base agent (simulated)
        base_results = simulate_base_agent_research(topic)
        base_eval = base_results['evaluation']
        
        print(f"\n   📊 Base Agent Results:")
        print(f"      Sources: {base_eval.total_sources}")
        print(f"      Preferred: {base_eval.preferred_count} ({base_eval.preferred_ratio:.1%})")
        print(f"      Status: {base_eval.status}")
        
        # Run evaluated agent
        eval_results = run_evaluated_agent_research(topic)
        eval_eval = eval_results['evaluation']
        
        print(f"\n   📊 Evaluated Agent Results:")
        print(f"      Sources: {eval_eval.total_sources}")
        print(f"      Preferred: {eval_eval.preferred_count} ({eval_eval.preferred_ratio:.1%})")
        print(f"      Status: {eval_eval.status}")
        print(f"      Retries: {eval_results['retry_count']}")
        
        # Compare
        improvement = eval_eval.preferred_ratio - base_eval.preferred_ratio
        print(f"\n   📈 Comparison:")
        if improvement > 0:
            print(f"      ✅ Evaluated agent improved quality by {improvement:.1%}")
        elif improvement < 0:
            print(f"      ⚠️  Quality decreased by {abs(improvement):.1%}")
        else:
            print(f"      ➡️  No change in quality")
        
        if eval_results['retry_count'] > 0:
            print(f"      🔄 Required {eval_results['retry_count']} retries to improve quality")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print("\n✅ Key Benefits of Evaluated Agent:")
    print("   1. Automatic source quality evaluation")
    print("   2. Retry mechanism for poor quality results")
    print("   3. Comprehensive quality metrics")
    print("   4. Feedback loop for continuous improvement")
    print("\n⚠️  Base Agent Limitations:")
    print("   1. No quality awareness")
    print("   2. No retry mechanism")
    print("   3. No quality metrics")
    print("   4. Manual quality checking required")


if __name__ == "__main__":
    main()
