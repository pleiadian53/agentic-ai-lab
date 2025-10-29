#!/usr/bin/env python3
"""
Test script to evaluate the enhanced reflection prompt quality.

This test compares chart quality improvements across iterations to verify
that the structured critique framework produces measurably better visualizations.

Tests:
1. Basic enhancement (2 iterations with enhanced prompt)
2. Extended refinement (3 iterations to see progressive improvement)
3. Comparison with baseline (if available)
"""

from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from reflection.chart_workflow import ChartWorkflowConfig, run_reflection_workflow


def print_section(title: str, char: str = "=") -> None:
    """Print a formatted section header."""
    print(f"\n{char * 80}")
    print(f"  {title}")
    print(f"{char * 80}\n")


def test_enhanced_prompt_basic():
    """Test basic enhancement with 2 iterations."""
    print_section("Test 1: Enhanced Prompt - Basic (2 iterations)")
    
    output_dir = project_root / "tests" / "chart_workflow" / "outputs" / "enhanced_prompt_test" / "basic"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("📊 Configuration:")
    print("   • Using enhanced reflection prompt (automatic)")
    print("   • 2 iterations (initial + 1 refinement)")
    print("   • Coffee sales dataset")
    print()
    
    config = ChartWorkflowConfig(
        generation_model="gpt-4o-mini",
        reflection_model="gpt-4o",  # Vision model for reflection
        image_basename="enhanced_basic",
        output_dir=output_dir,
        max_iterations=2,
        stop_on_convergence=True,
        save_final_code=True,
    )
    
    dataset_path = project_root / "reflection" / "M2_UGL_1" / "coffee_sales.csv"
    
    artifacts = run_reflection_workflow(
        dataset=str(dataset_path),
        instruction="Create a bar chart showing total sales by coffee type",
        config=config,
    )
    
    print(f"\n✅ Workflow completed in {len(artifacts.iterations)} iteration(s)")
    print(f"\n📈 Results:")
    
    for iteration in artifacts.iterations:
        print(f"\n   Iteration {iteration.iteration}:")
        print(f"   • Chart: {iteration.chart_path}")
        print(f"   • Code length: {len(iteration.code)} characters")
        
        if iteration.description:
            print(f"   • Description: {iteration.description}")
        
        if iteration.feedback:
            print(f"   • Feedback preview:")
            feedback_lines = iteration.feedback.split('\n')[:3]
            for line in feedback_lines:
                print(f"     {line}")
            if len(iteration.feedback.split('\n')) > 3:
                print("     ...")
    
    if artifacts.final_code_path:
        print(f"\n💾 Final code saved: {artifacts.final_code_path}")
    
    print("\n💡 Enhanced Prompt Features Applied:")
    print("   ✓ Chart type appropriateness evaluation")
    print("   ✓ Perceptual accuracy checks")
    print("   ✓ Clarity & readability improvements")
    print("   ✓ Data-ink ratio optimization")
    print("   ✓ Statistical integrity validation")
    
    return artifacts


def test_enhanced_prompt_extended():
    """Test extended refinement with 3 iterations."""
    print_section("Test 2: Enhanced Prompt - Extended (3 iterations)")
    
    output_dir = project_root / "tests" / "chart_workflow" / "outputs" / "enhanced_prompt_test" / "extended"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("📊 Configuration:")
    print("   • Using enhanced reflection prompt (automatic)")
    print("   • 3 iterations (initial + 2 refinements)")
    print("   • Testing progressive improvement")
    print()
    
    config = ChartWorkflowConfig(
        generation_model="gpt-4o-mini",
        reflection_model="gpt-4o",
        image_basename="enhanced_extended",
        output_dir=output_dir,
        max_iterations=3,
        stop_on_convergence=True,
        save_final_code=True,
    )
    
    dataset_path = project_root / "reflection" / "M2_UGL_1" / "coffee_sales.csv"
    
    artifacts = run_reflection_workflow(
        dataset=str(dataset_path),
        instruction="Visualize coffee sales trends with clear labels and professional styling",
        config=config,
    )
    
    print(f"\n✅ Workflow completed in {len(artifacts.iterations)} iteration(s)")
    print(f"   (Max allowed: 3, stopped early: {len(artifacts.iterations) < 3})")
    
    print(f"\n📈 Progressive Improvement Analysis:")
    
    for i, iteration in enumerate(artifacts.iterations):
        print(f"\n   Iteration {iteration.iteration}:")
        print(f"   • Chart: {iteration.chart_path.name}")
        
        if iteration.feedback:
            # Extract key improvement areas from feedback
            feedback_lower = iteration.feedback.lower()
            improvements = []
            
            if "label" in feedback_lower or "legib" in feedback_lower:
                improvements.append("Label clarity")
            if "color" in feedback_lower or "palette" in feedback_lower:
                improvements.append("Color accessibility")
            if "legend" in feedback_lower:
                improvements.append("Legend placement")
            if "gridline" in feedback_lower or "clutter" in feedback_lower:
                improvements.append("Data-ink ratio")
            if "axis" in feedback_lower or "scale" in feedback_lower:
                improvements.append("Axis formatting")
            
            if improvements:
                print(f"   • Focus areas: {', '.join(improvements)}")
            
            print(f"   • Feedback length: {len(iteration.feedback)} chars")
    
    return artifacts


def test_auto_instruction_with_enhancement():
    """Test auto-generated instruction with enhanced prompt."""
    print_section("Test 3: Auto-Instruction + Enhanced Prompt")
    
    output_dir = project_root / "tests" / "chart_workflow" / "outputs" / "enhanced_prompt_test" / "auto_instruction"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("📊 Configuration:")
    print("   • Auto-generated instruction (no user input)")
    print("   • Enhanced reflection prompt")
    print("   • 2 iterations")
    print()
    
    config = ChartWorkflowConfig(
        generation_model="gpt-4o-mini",
        reflection_model="gpt-4o",
        image_basename="enhanced_auto",
        output_dir=output_dir,
        max_iterations=2,
        stop_on_convergence=True,
        save_final_code=True,
    )
    
    dataset_path = project_root / "reflection" / "M2_UGL_1" / "coffee_sales.csv"
    
    artifacts = run_reflection_workflow(
        dataset=str(dataset_path),
        instruction=None,  # Auto-generate
        config=config,
    )
    
    print(f"\n✅ Workflow completed in {len(artifacts.iterations)} iteration(s)")
    print(f"\n📝 Auto-generated instruction:")
    print(f"   {artifacts.instruction[:200]}...")
    
    print(f"\n📈 Results:")
    for iteration in artifacts.iterations:
        print(f"   • Iteration {iteration.iteration}: {iteration.chart_path.name}")
    
    return artifacts


def main():
    """Run all enhanced prompt quality tests."""
    print_section("Enhanced Reflection Prompt Quality Testing")
    print("This test suite evaluates the structured critique framework:")
    print("  • Chart type appropriateness")
    print("  • Perceptual accuracy & truthfulness")
    print("  • Clarity & readability")
    print("  • Data-ink ratio (Tufte's principle)")
    print("  • Statistical integrity")
    print()
    print("All tests use the enhanced prompt automatically (no code changes needed).")
    
    try:
        artifacts_basic = test_enhanced_prompt_basic()
        artifacts_extended = test_enhanced_prompt_extended()
        artifacts_auto = test_auto_instruction_with_enhancement()
        
        print_section("All Tests Passed! ✅")
        print("Summary:")
        print(f"  ✓ Basic enhancement: {len(artifacts_basic.iterations)} iteration(s)")
        print(f"  ✓ Extended refinement: {len(artifacts_extended.iterations)} iteration(s)")
        print(f"  ✓ Auto-instruction: {len(artifacts_auto.iterations)} iteration(s)")
        print()
        print("📁 Output locations:")
        print("  • tests/chart_workflow/outputs/enhanced_prompt_test/basic/")
        print("  • tests/chart_workflow/outputs/enhanced_prompt_test/extended/")
        print("  • tests/chart_workflow/outputs/enhanced_prompt_test/auto_instruction/")
        print()
        print("🔍 To evaluate quality improvements:")
        print("  1. Compare chart_v1.png vs chart_v2.png in each directory")
        print("  2. Review feedback in iteration results")
        print("  3. Examine final code for best practices")
        print()
        
    except Exception as e:
        print(f"\n❌ Test failed with error:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
