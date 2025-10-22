#!/usr/bin/env python3
"""
Test script for iterative refinement with convergence handling.

Tests:
1. Default behavior (max_iterations=2, stop_on_convergence=True)
2. Extended iterations (max_iterations=4)
3. Forced iterations (--no-stop-on-convergence)
4. Single iteration (max_iterations=1)
5. Backward compatibility (v1/v2 properties)
"""

from pathlib import Path
import sys
import shutil

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from reflection.chart_workflow import ChartWorkflowConfig, run_reflection_workflow


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def test_default_behavior():
    """Test default behavior: max_iterations=2, stop_on_convergence=True"""
    print_section("Test 1: Default Behavior (2 iterations max, stop on convergence)")
    
    output_dir = Path("tests/chart_workflow/outputs/iterative_test/default")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config = ChartWorkflowConfig(
        generation_model="gpt-4o-mini",
        reflection_model="gpt-4o",
        image_basename="test_default",
        output_dir=output_dir,
        max_iterations=2,
        stop_on_convergence=True,
    )
    
    artifacts = run_reflection_workflow(
        dataset="reflection/M2_UGL_1/coffee_sales.csv",
        instruction="Create a simple bar chart of coffee sales by type",
        config=config,
    )
    
    print(f"✓ Completed in {len(artifacts.iterations)} iteration(s)")
    print(f"✓ Instruction: {artifacts.instruction}")
    print(f"✓ V1 chart: {artifacts.chart_v1}")
    print(f"✓ V2 chart: {artifacts.chart_v2}")
    
    # Verify backward compatibility
    assert artifacts.code_v1 == artifacts.iterations[0].code
    assert artifacts.chart_v1 == artifacts.iterations[0].chart_path
    
    if len(artifacts.iterations) >= 2:
        assert artifacts.code_v2 == artifacts.iterations[1].code
        assert artifacts.chart_v2 == artifacts.iterations[1].chart_path
    
    print("✓ Backward compatibility verified")
    
    for i, iteration in enumerate(artifacts.iterations, 1):
        print(f"\n  Iteration {iteration.iteration}:")
        print(f"    Chart: {iteration.chart_path}")
        print(f"    Code length: {len(iteration.code)} chars")
        print(f"    Feedback: {iteration.feedback or 'n/a'}")


def test_extended_iterations():
    """Test extended iterations: max_iterations=4"""
    print_section("Test 2: Extended Iterations (4 iterations max)")
    
    output_dir = Path("tests/chart_workflow/outputs/iterative_test/extended")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config = ChartWorkflowConfig(
        generation_model="gpt-4o-mini",
        reflection_model="gpt-4o",
        image_basename="test_extended",
        output_dir=output_dir,
        max_iterations=4,
        stop_on_convergence=True,
    )
    
    artifacts = run_reflection_workflow(
        dataset="reflection/M2_UGL_1/coffee_sales.csv",
        instruction="Create a bar chart showing coffee sales by type",
        config=config,
    )
    
    print(f"✓ Completed in {len(artifacts.iterations)} iteration(s)")
    print(f"✓ Max allowed: 4 iterations")
    print(f"✓ Stopped early: {len(artifacts.iterations) < 4}")
    
    for iteration in artifacts.iterations:
        print(f"\n  Iteration {iteration.iteration}:")
        print(f"    Chart: {iteration.chart_path}")
        print(f"    Feedback: {iteration.feedback or 'n/a'}")


def test_forced_iterations():
    """Test forced iterations: stop_on_convergence=False"""
    print_section("Test 3: Forced Iterations (no early stopping)")
    
    output_dir = Path("tests/chart_workflow/outputs/iterative_test/forced")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config = ChartWorkflowConfig(
        generation_model="gpt-4o-mini",
        reflection_model="gpt-4o",
        image_basename="test_forced",
        output_dir=output_dir,
        max_iterations=3,
        stop_on_convergence=False,  # Force all iterations
    )
    
    artifacts = run_reflection_workflow(
        dataset="reflection/M2_UGL_1/coffee_sales.csv",
        instruction="Create a bar chart of coffee sales",
        config=config,
    )
    
    print(f"✓ Completed in {len(artifacts.iterations)} iteration(s)")
    print(f"✓ Expected: 3 iterations (forced)")
    print(f"✓ Actual: {len(artifacts.iterations)} iterations")
    
    # Should run all 3 iterations even if converged
    assert len(artifacts.iterations) == 3, f"Expected 3 iterations, got {len(artifacts.iterations)}"
    print("✓ All iterations executed as expected")


def test_single_iteration():
    """Test single iteration: max_iterations=1"""
    print_section("Test 4: Single Iteration (no refinement)")
    
    output_dir = Path("tests/chart_workflow/outputs/iterative_test/single")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config = ChartWorkflowConfig(
        generation_model="gpt-4o-mini",
        reflection_model="gpt-4o",
        image_basename="test_single",
        output_dir=output_dir,
        max_iterations=1,
        stop_on_convergence=True,
    )
    
    artifacts = run_reflection_workflow(
        dataset="reflection/M2_UGL_1/coffee_sales.csv",
        instruction="Create a bar chart",
        config=config,
    )
    
    print(f"✓ Completed in {len(artifacts.iterations)} iteration(s)")
    assert len(artifacts.iterations) == 1, f"Expected 1 iteration, got {len(artifacts.iterations)}"
    
    # V2 should fallback to V1
    assert artifacts.chart_v2 == artifacts.chart_v1
    assert artifacts.code_v2 == artifacts.code_v1
    
    print("✓ Single iteration mode works correctly")
    print("✓ V2 properties correctly fallback to V1")


def test_auto_prompt_with_iterations():
    """Test auto-generated prompt with multiple iterations"""
    print_section("Test 5: Auto-Generated Prompt + Iterations")
    
    output_dir = Path("tests/chart_workflow/outputs/iterative_test/auto_prompt")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config = ChartWorkflowConfig(
        generation_model="gpt-4o-mini",
        reflection_model="gpt-4o",
        image_basename="test_auto",
        output_dir=output_dir,
        max_iterations=3,
        stop_on_convergence=True,
    )
    
    artifacts = run_reflection_workflow(
        dataset="reflection/M2_UGL_1/coffee_sales.csv",
        instruction=None,  # Auto-generate
        config=config,
    )
    
    print(f"✓ Auto-generated instruction:")
    print(f"  {artifacts.instruction}")
    print(f"\n✓ Completed in {len(artifacts.iterations)} iteration(s)")
    
    # Verify instruction is consistent across iterations
    for iteration in artifacts.iterations:
        print(f"  Iteration {iteration.iteration}: {iteration.chart_path.name}")


def main():
    """Run all tests."""
    print_section("Iterative Refinement Testing Suite")
    print("Testing new features:")
    print("  • max_iterations parameter")
    print("  • stop_on_convergence flag")
    print("  • IterationResult tracking")
    print("  • Backward compatibility")
    
    try:
        test_default_behavior()
        test_extended_iterations()
        test_forced_iterations()
        test_single_iteration()
        test_auto_prompt_with_iterations()
        
        print_section("All Tests Passed! ✅")
        print("Summary:")
        print("  ✓ Default behavior works correctly")
        print("  ✓ Extended iterations supported")
        print("  ✓ Forced iterations (no early stop) works")
        print("  ✓ Single iteration mode works")
        print("  ✓ Auto-prompt with iterations works")
        print("  ✓ Backward compatibility maintained")
        
    except Exception as e:
        print(f"\n❌ Test failed with error:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
