#!/usr/bin/env python3
"""
Test all research tools to verify they work correctly with OpenAI API.
This validates tool schemas and basic functionality.
"""

import json
import sys
from pathlib import Path

def _find_project_root(marker_name: str = "agentic-ai-lab") -> Path:
    """
    Find project root by searching for a directory with the given name.
    More robust than counting parent directories.
    """
    current = Path(__file__).resolve()
    
    # Traverse up the directory tree
    for parent in [current] + list(current.parents):
        if parent.name == marker_name:
            return parent
    
    # Fallback: look for common project markers
    for parent in [current] + list(current.parents):
        if any((parent / marker).exists() for marker in ['.git', 'pyproject.toml', 'setup.py']):
            return parent
    
    raise RuntimeError(
        f"Could not find project root. Expected directory named '{marker_name}' "
        f"or a directory containing .git, pyproject.toml, or setup.py"
    )

# Add project root to path
PROJECT_ROOT = _find_project_root()
sys.path.insert(0, str(PROJECT_ROOT))

from src.nexus.agents.research.tools import (
    tavily_tool_def,
    arxiv_tool_def,
    wikipedia_tool_def,
    europe_pmc_tool_def,
    reddit_tool_def,
    semantic_scholar_tool_def
)

def validate_tool_schema(tool_def: dict, tool_name: str) -> bool:
    """Validate that a tool definition has correct JSON Schema format."""
    print(f"\n{'='*60}")
    print(f"Testing: {tool_name}")
    print(f"{'='*60}")
    
    try:
        # Check basic structure
        assert tool_def.get("type") == "function", "Missing type: function"
        assert "function" in tool_def, "Missing function key"
        
        func = tool_def["function"]
        assert "name" in func, "Missing function name"
        assert "description" in func, "Missing description"
        assert "parameters" in func, "Missing parameters"
        
        params = func["parameters"]
        assert params.get("type") == "object", "Parameters type must be object"
        assert "properties" in params, "Missing properties"
        
        # Check for invalid Optional[str] patterns
        properties = params["properties"]
        for prop_name, prop_def in properties.items():
            prop_type = prop_def.get("type")
            
            # Check if type contains string representation of Optional
            if isinstance(prop_type, str):
                if "Optional" in prop_type or "typing." in prop_type:
                    print(f"  ❌ INVALID: Property '{prop_name}' has type: {prop_type}")
                    print(f"     Should use ['string', 'null'] for optional strings")
                    return False
            
            # For optional parameters, should use array notation
            if prop_name not in params.get("required", []):
                if isinstance(prop_type, str) and prop_type == "string":
                    print(f"  ⚠️  WARNING: Optional property '{prop_name}' uses 'string' instead of ['string', 'null']")
                    print(f"     This may work but ['string', 'null'] is more explicit")
        
        print(f"  ✅ Schema structure valid")
        print(f"  📋 Function: {func['name']}")
        print(f"  📝 Description: {func['description'][:80]}...")
        print(f"  🔧 Parameters: {list(properties.keys())}")
        print(f"  ✓ Required: {params.get('required', [])}")
        
        return True
        
    except AssertionError as e:
        print(f"  ❌ FAILED: {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False


def test_all_tools():
    """Test all research tools."""
    print("\n" + "="*60)
    print("NEXUS RESEARCH TOOLS VALIDATION")
    print("="*60)
    
    tools = [
        ("Tavily Search", tavily_tool_def),
        ("arXiv Search", arxiv_tool_def),
        ("Wikipedia Search", wikipedia_tool_def),
        ("Europe PMC Search", europe_pmc_tool_def),
        ("Reddit Search", reddit_tool_def),
        ("Semantic Scholar Search", semantic_scholar_tool_def),
    ]
    
    results = {}
    for tool_name, tool_def in tools:
        results[tool_name] = validate_tool_schema(tool_def, tool_name)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for tool_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"  {status}: {tool_name}")
    
    print(f"\n  Total: {passed}/{total} tools passed")
    
    if passed == total:
        print("\n  🎉 All tools validated successfully!")
        return 0
    else:
        print(f"\n  ⚠️  {total - passed} tool(s) failed validation")
        return 1


if __name__ == "__main__":
    sys.exit(test_all_tools())
