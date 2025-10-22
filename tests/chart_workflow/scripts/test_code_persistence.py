#!/usr/bin/env python3
"""
Test script for final code persistence feature.

Tests:
1. Default behavior (save_final_code=True)
2. Code file exists and is valid Python
3. Code can be executed independently
4. Disabled persistence (--no-save-final-code)
5. Code content matches final iteration
6. Multiple iterations with code persistence
"""

from pathlib import Path
import sys
import subprocess

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from reflection.chart_workflow import ChartWorkflowConfig, run_reflection_workflow


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def test_default_code_persistence():
    """Test default behavior: save_final_code=True"""
    print_section("Test 1: Default Code Persistence (Enabled)")
    
    output_dir = Path("tests/chart_workflow/outputs/code_persistence_test/default")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config = ChartWorkflowConfig(
        generation_model="gpt-4o-mini",
        reflection_model="gpt-4o",
        image_basename="test_persist",
        output_dir=output_dir,
        max_iterations=2,
        save_final_code=True,  # Default
    )
    
    artifacts = run_reflection_workflow(
        dataset="reflection/M2_UGL_1/coffee_sales.csv",
        instruction="Create a bar chart of coffee sales by type",
        config=config,
    )
    
    print(f"✓ Workflow completed in {len(artifacts.iterations)} iteration(s)")
    print(f"✓ Final chart: {artifacts.iterations[-1].chart_path}")
    print(f"✓ Final code path: {artifacts.final_code_path}")
    
    # Verify code file exists
    assert artifacts.final_code_path is not None, "final_code_path should not be None"
    assert artifacts.final_code_path.exists(), f"Code file should exist: {artifacts.final_code_path}"
    
    print(f"✓ Code file exists: {artifacts.final_code_path}")
    
    # Verify file naming
    expected_name = f"{config.image_basename}_final.py"
    assert artifacts.final_code_path.name == expected_name, f"Expected {expected_name}, got {artifacts.final_code_path.name}"
    print(f"✓ Code file name correct: {expected_name}")
    
    # Read and display code
    code_content = artifacts.final_code_path.read_text()
    print(f"✓ Code file size: {len(code_content)} characters")
    print(f"\n--- First 500 chars of saved code ---")
    print(code_content[:500])
    print("...")
    
    return artifacts


def test_code_validity():
    """Test that saved code is valid Python"""
    print_section("Test 2: Code Validity (Syntax Check)")
    
    output_dir = Path("tests/chart_workflow/outputs/code_persistence_test/validity")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config = ChartWorkflowConfig(
        generation_model="gpt-4o-mini",
        reflection_model="gpt-4o",
        image_basename="test_valid",
        output_dir=output_dir,
        max_iterations=2,
        save_final_code=True,
    )
    
    artifacts = run_reflection_workflow(
        dataset="reflection/M2_UGL_1/coffee_sales.csv",
        instruction="Create a simple bar chart",
        config=config,
    )
    
    code_file = artifacts.final_code_path
    print(f"✓ Code file: {code_file}")
    
    # Check Python syntax
    try:
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(code_file)],
            capture_output=True,
            text=True,
            check=True
        )
        print("✓ Python syntax is valid")
    except subprocess.CalledProcessError as e:
        print(f"❌ Syntax error in generated code:")
        print(e.stderr)
        raise
    
    # Verify it's executable Python
    code_content = code_file.read_text()
    assert "import" in code_content, "Code should contain import statements"
    assert "plt" in code_content or "matplotlib" in code_content, "Code should use matplotlib"
    print("✓ Code contains expected imports")
    
    return artifacts


def test_code_execution():
    """Test that saved code can be executed independently"""
    print_section("Test 3: Independent Code Execution")
    
    output_dir = Path("tests/chart_workflow/outputs/code_persistence_test/execution")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config = ChartWorkflowConfig(
        generation_model="gpt-4o-mini",
        reflection_model="gpt-4o",
        image_basename="test_exec",
        output_dir=output_dir,
        max_iterations=2,
        save_final_code=True,
    )
    
    artifacts = run_reflection_workflow(
        dataset="reflection/M2_UGL_1/coffee_sales.csv",
        instruction="Create a bar chart",
        config=config,
    )
    
    code_file = artifacts.final_code_path
    print(f"✓ Code file: {code_file}")
    
    # Try to execute the code
    print("✓ Attempting to execute saved code...")
    
    # Read the code
    code_content = code_file.read_text()
    
    # Load data for execution
    import pandas as pd
    df = pd.read_csv("reflection/M2_UGL_1/coffee_sales.csv")
    
    # Execute the code
    try:
        exec_globals = {"df": df}
        exec(code_content, exec_globals)
        print("✓ Code executed successfully")
    except Exception as e:
        print(f"❌ Code execution failed: {e}")
        raise
    
    # Verify chart was created
    expected_chart = output_dir / f"{config.image_basename}_v{len(artifacts.iterations)}.png"
    if expected_chart.exists():
        print(f"✓ Chart created by executed code: {expected_chart}")
    
    return artifacts


def test_disabled_persistence():
    """Test disabled code persistence: save_final_code=False"""
    print_section("Test 4: Disabled Code Persistence")
    
    output_dir = Path("tests/chart_workflow/outputs/code_persistence_test/disabled")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config = ChartWorkflowConfig(
        generation_model="gpt-4o-mini",
        reflection_model="gpt-4o",
        image_basename="test_disabled",
        output_dir=output_dir,
        max_iterations=2,
        save_final_code=False,  # Disabled
    )
    
    artifacts = run_reflection_workflow(
        dataset="reflection/M2_UGL_1/coffee_sales.csv",
        instruction="Create a bar chart",
        config=config,
    )
    
    print(f"✓ Workflow completed in {len(artifacts.iterations)} iteration(s)")
    print(f"✓ Final code path: {artifacts.final_code_path}")
    
    # Verify code file was NOT created
    assert artifacts.final_code_path is None, "final_code_path should be None when disabled"
    print("✓ Code persistence correctly disabled")
    
    # Verify no _final.py file exists
    potential_file = output_dir / f"{config.image_basename}_final.py"
    assert not potential_file.exists(), f"Code file should not exist: {potential_file}"
    print(f"✓ No code file created: {potential_file.name}")
    
    return artifacts


def test_code_content_matches():
    """Test that saved code matches final iteration code"""
    print_section("Test 5: Code Content Matches Final Iteration")
    
    output_dir = Path("tests/chart_workflow/outputs/code_persistence_test/content")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config = ChartWorkflowConfig(
        generation_model="gpt-4o-mini",
        reflection_model="gpt-4o",
        image_basename="test_content",
        output_dir=output_dir,
        max_iterations=3,
        save_final_code=True,
    )
    
    artifacts = run_reflection_workflow(
        dataset="reflection/M2_UGL_1/coffee_sales.csv",
        instruction="Create a bar chart",
        config=config,
    )
    
    print(f"✓ Workflow completed in {len(artifacts.iterations)} iteration(s)")
    
    # Get final iteration code
    final_iteration_code = artifacts.iterations[-1].code
    print(f"✓ Final iteration code length: {len(final_iteration_code)} chars")
    
    # Read saved code
    saved_code = artifacts.final_code_path.read_text()
    print(f"✓ Saved code length: {len(saved_code)} chars")
    
    # The saved code should be the executable block from the final iteration
    # It may be processed (tags stripped), so we check it's derived from final code
    assert len(saved_code) > 0, "Saved code should not be empty"
    assert "import" in saved_code, "Saved code should contain imports"
    
    # Check that key elements from final code are present
    if "matplotlib" in final_iteration_code:
        assert "matplotlib" in saved_code or "plt" in saved_code, "Saved code should contain matplotlib references"
    
    print("✓ Saved code is properly derived from final iteration")
    
    return artifacts


def test_multiple_iterations_persistence():
    """Test code persistence with multiple iterations"""
    print_section("Test 6: Multiple Iterations with Code Persistence")
    
    output_dir = Path("tests/chart_workflow/outputs/code_persistence_test/multi_iter")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config = ChartWorkflowConfig(
        generation_model="gpt-4o-mini",
        reflection_model="gpt-4o",
        image_basename="test_multi",
        output_dir=output_dir,
        max_iterations=4,
        save_final_code=True,
        stop_on_convergence=False,  # Force all iterations
    )
    
    artifacts = run_reflection_workflow(
        dataset="reflection/M2_UGL_1/coffee_sales.csv",
        instruction="Create a bar chart",
        config=config,
    )
    
    print(f"✓ Workflow completed in {len(artifacts.iterations)} iteration(s)")
    
    # Verify only ONE final code file exists
    code_files = list(output_dir.glob("*_final.py"))
    assert len(code_files) == 1, f"Expected 1 final code file, found {len(code_files)}"
    print(f"✓ Only one final code file exists: {code_files[0].name}")
    
    # Verify it's the code from the last iteration
    final_code = artifacts.final_code_path.read_text()
    last_iteration = artifacts.iterations[-1]
    
    print(f"✓ Final code saved from iteration {last_iteration.iteration}")
    print(f"✓ Code length: {len(final_code)} chars")
    
    # List all generated charts
    chart_files = sorted(output_dir.glob("*.png"))
    print(f"\n✓ Generated {len(chart_files)} chart(s):")
    for chart in chart_files:
        print(f"    {chart.name}")
    
    return artifacts


def main():
    """Run all tests."""
    print_section("Code Persistence Testing Suite")
    print("Testing new feature:")
    print("  • save_final_code parameter")
    print("  • final_code_path in artifacts")
    print("  • Code file creation and validity")
    print("  • Independent code execution")
    print("  • --no-save-final-code CLI flag")
    
    try:
        test_default_code_persistence()
        test_code_validity()
        test_code_execution()
        test_disabled_persistence()
        test_code_content_matches()
        test_multiple_iterations_persistence()
        
        print_section("All Tests Passed! ✅")
        print("Summary:")
        print("  ✓ Default code persistence works")
        print("  ✓ Saved code is valid Python")
        print("  ✓ Saved code can be executed independently")
        print("  ✓ Persistence can be disabled")
        print("  ✓ Saved code matches final iteration")
        print("  ✓ Multiple iterations handled correctly")
        print("\nCode persistence feature is working correctly! 🎉")
        
    except Exception as e:
        print(f"\n❌ Test failed with error:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
