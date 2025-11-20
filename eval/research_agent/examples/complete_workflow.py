#!/usr/bin/env python3
"""
Complete Workflow Example: Research with Evaluation, Reflection, and HTML Output

This example demonstrates the full workflow including all steps.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from eval.research_agent import run_evaluated_workflow
from eval import BIOLOGY_FOCUSED_DOMAINS


def main():
    print("="*80)
    print("COMPLETE WORKFLOW: Research + Evaluation + Reflection + HTML")
    print("="*80)
    
    # Research topic
    topic = "CRISPR-Cas9 gene editing applications in medicine"
    
    print(f"\n📝 Research Topic: {topic}")
    print(f"🎯 Domain Focus: Biology/Life Sciences")
    print(f"📊 Quality Threshold: 60% from preferred domains")
    print(f"🔄 Max Retries: 2")
    
    # Run complete workflow
    results = run_evaluated_workflow(
        topic=topic,
        output_dir="./complete_workflow_outputs",
        preferred_domains=BIOLOGY_FOCUSED_DOMAINS,
        min_source_ratio=0.6,
        max_retries=2,
        save_intermediate=True,
        generate_html=True,
        run_reflection=True,
        verbose=True
    )
    
    # Display summary
    print("\n" + "="*80)
    print("WORKFLOW SUMMARY")
    print("="*80)
    
    print(f"\n📊 Initial Research Evaluation:")
    initial_eval = results['evaluation']
    print(f"   Status: {initial_eval.status}")
    print(f"   Quality: {initial_eval.preferred_ratio:.1%} from preferred domains")
    print(f"   Sources: {initial_eval.preferred_count}/{initial_eval.total_sources}")
    print(f"   Retries: {results['retry_count']}")
    
    if 'revised_evaluation' in results:
        print(f"\n📊 Revised Report Evaluation:")
        revised_eval = results['revised_evaluation']
        print(f"   Status: {revised_eval.status}")
        print(f"   Quality: {revised_eval.preferred_ratio:.1%} from preferred domains")
        print(f"   Sources: {revised_eval.preferred_count}/{revised_eval.total_sources}")
        
        # Compare improvement
        improvement = revised_eval.preferred_ratio - initial_eval.preferred_ratio
        if improvement > 0:
            print(f"   📈 Improvement: +{improvement:.1%}")
        elif improvement < 0:
            print(f"   📉 Change: {improvement:.1%}")
        else:
            print(f"   ➡️  No change in ratio")
    
    print(f"\n📁 Generated Files:")
    for key, filepath in results['files'].items():
        print(f"   • {key}: {filepath}")
    
    print(f"\n✅ Workflow completed successfully!")
    print(f"   Output directory: {Path('./complete_workflow_outputs').absolute()}")


if __name__ == "__main__":
    main()
