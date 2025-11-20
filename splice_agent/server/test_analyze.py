#!/usr/bin/env python
"""
Direct test of the analyze endpoint to debug validation errors.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openai import OpenAI
from dotenv import load_dotenv
from chart_agent.server.schemas import AnalysisRequest, PlanResponse, ModelType
from chart_agent.server.chart_service import ChartGenerator
from chart_agent.data_access import DuckDBDataset
from chart_agent.server import config

# Load environment
load_dotenv()

def test_analyze():
    """Test the analyze endpoint directly"""
    
    print("=" * 60)
    print("Testing Chart Agent Analyze Endpoint")
    print("=" * 60)
    
    # Initialize client
    print("\n1. Initializing OpenAI client...")
    client = OpenAI()
    print("   ✓ Client initialized")
    
    # Create request
    print("\n2. Creating analysis request...")
    request = AnalysisRequest(
        dataset_path="data/splice_sites_enhanced.tsv",
        question="Show the top 20 genes with the most splice sites",
        context="Focus on standard chromosomes only. Use publication-ready styling with clear labels.",
        model=ModelType.GPT_5_CODEX_MINI
    )
    print(f"   ✓ Request created")
    print(f"   - Dataset: {request.dataset_path}")
    print(f"   - Question: {request.question}")
    print(f"   - Model: {request.model.value}")
    
    # Test dataset loading
    print("\n3. Testing dataset loading...")
    dataset_path = config.resolve_dataset_path(request.dataset_path)
    print(f"   - Resolved path: {dataset_path}")
    print(f"   - Exists: {dataset_path.exists()}")
    
    if dataset_path.exists():
        dataset = DuckDBDataset(str(dataset_path))
        print("   ✓ Dataset loaded")
        
        # Test schema
        print("\n4. Testing schema description...")
        try:
            stats = dataset.get_summary_stats()
            print(f"   ✓ Schema retrieved")
            print(f"   - Rows: {stats['row_count']:,}")
            print(f"   - Columns: {stats['column_count']}")
            print(f"   - First 5 columns: {stats['columns'][:5]}")
        except Exception as e:
            print(f"   ✗ Schema error: {e}")
            return False
    else:
        print(f"   ✗ Dataset not found at {dataset_path}")
        return False
    
    # Test code generation
    print("\n5. Testing code generation...")
    try:
        generator = ChartGenerator(client)
        plan = generator.generate_plan(request)
        
        print("   ✓ Code generated successfully!")
        print(f"\n   Response type: {type(plan)}")
        print(f"   Response class: {plan.__class__.__name__}")
        
        # Check response fields
        print("\n6. Validating response fields...")
        print(f"   - code: {type(plan.code).__name__} ({len(plan.code)} chars)")
        print(f"   - explanation: {type(plan.explanation).__name__} ('{plan.explanation}')")
        print(f"   - libraries_used: {type(plan.libraries_used).__name__} ({plan.libraries_used})")
        
        # Validate it's a proper PlanResponse
        print("\n7. Testing Pydantic validation...")
        try:
            # Try to serialize it
            response_dict = plan.model_dump()
            print("   ✓ model_dump() succeeded")
            print(f"   - Keys: {list(response_dict.keys())}")
            
            # Try to create a new instance from dict
            validated = PlanResponse(**response_dict)
            print("   ✓ Re-validation succeeded")
            
            # Show first 200 chars of code
            print("\n8. Generated code preview:")
            print("   " + "-" * 56)
            code_preview = plan.code[:200].replace('\n', '\n   ')
            print(f"   {code_preview}...")
            print("   " + "-" * 56)
            
            return True
            
        except Exception as e:
            print(f"   ✗ Validation error: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"   ✗ Generation error: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_analyze()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        sys.exit(0)
    else:
        print("✗ TESTS FAILED")
        print("=" * 60)
        sys.exit(1)
