"""Verify Splice Agent Setup.

Quick script to verify that all dependencies are available and the setup is correct.
"""

import sys
from pathlib import Path

def check_imports():
    """Check that all required packages can be imported."""
    print("=" * 60)
    print("Checking Required Packages...")
    print("=" * 60)
    
    required_packages = [
        ("openai", "OpenAI API client"),
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("pandas", "Data manipulation"),
        ("duckdb", "Efficient data loading"),
        ("matplotlib", "Plotting library"),
        ("seaborn", "Statistical visualization"),
        ("dotenv", "Environment variables"),
    ]
    
    all_ok = True
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✓ {package:15} - {description}")
        except ImportError:
            print(f"✗ {package:15} - MISSING! ({description})")
            all_ok = False
    
    print()
    return all_ok


def check_splice_agent_imports():
    """Check that splice_agent modules can be imported."""
    print("=" * 60)
    print("Checking Splice Agent Modules...")
    print("=" * 60)
    
    modules = [
        ("splice_agent", "Main package"),
        ("splice_agent.data_access", "Data access layer"),
        ("splice_agent.planning", "Code generation"),
        ("splice_agent.llm_client", "LLM client"),
        ("splice_agent.utils", "Utilities"),
        ("splice_agent.splice_analysis", "Splice-specific analysis"),
    ]
    
    all_ok = True
    for module, description in modules:
        try:
            __import__(module)
            print(f"✓ {module:35} - {description}")
        except ImportError as e:
            print(f"✗ {module:35} - FAILED! ({e})")
            all_ok = False
    
    print()
    return all_ok


def check_environment():
    """Check environment configuration."""
    print("=" * 60)
    print("Checking Environment Configuration...")
    print("=" * 60)
    
    import os
    
    # Check for .env file
    env_file = Path(".env")
    if env_file.exists():
        print(f"✓ .env file exists")
    else:
        print(f"⚠ .env file not found (copy from .env.example)")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✓ OPENAI_API_KEY is set")
    else:
        print(f"⚠ OPENAI_API_KEY not set (required for API calls)")
    
    # Check data directory
    data_dir = Path("data")
    if data_dir.exists():
        print(f"✓ data/ directory exists")
        data_files = list(data_dir.glob("*.tsv")) + list(data_dir.glob("*.csv"))
        if data_files:
            print(f"  Found {len(data_files)} data file(s):")
            for f in data_files[:3]:  # Show first 3
                print(f"    - {f.name}")
        else:
            print(f"  ⚠ No data files found (add your splice site dataset)")
    else:
        print(f"⚠ data/ directory not found")
    
    print()


def check_server():
    """Check if server files are present."""
    print("=" * 60)
    print("Checking Server Files...")
    print("=" * 60)
    
    server_files = [
        "server/splice_service.py",
        "server/schemas.py",
        "server/config.py",
    ]
    
    all_ok = True
    for file in server_files:
        path = Path(file)
        if path.exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING!")
            all_ok = False
    
    print()
    return all_ok


def main():
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("SPLICE AGENT - SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    # Change to splice_agent directory if needed
    if Path("splice_agent").exists():
        import os
        os.chdir("splice_agent")
        print("Changed to splice_agent directory\n")
    
    results = {
        "packages": check_imports(),
        "modules": check_splice_agent_imports(),
        "server": check_server(),
    }
    
    check_environment()
    
    # Summary
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if all(results.values()):
        print("✓ All checks passed!")
        print("\nYou're ready to use Splice Agent!")
        print("\nNext steps:")
        print("  1. Ensure OPENAI_API_KEY is set in .env")
        print("  2. Add your splice site dataset to data/")
        print("  3. Start the server: python server/splice_service.py")
        print("  4. Or run examples: python examples/quick_start.py")
        return 0
    else:
        print("✗ Some checks failed!")
        print("\nPlease fix the issues above before proceeding.")
        if not results["packages"]:
            print("\nTo install missing packages:")
            print("  pip install -r requirements.txt")
        if not results["modules"]:
            print("\nMake sure you're in the splice_agent directory:")
            print("  cd splice_agent")
        return 1


if __name__ == "__main__":
    sys.exit(main())
