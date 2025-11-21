#!/usr/bin/env python3
"""CLI driver script for market research campaign generation.

This script provides a command-line interface to run the full
multi-agent marketing campaign pipeline.

Usage:
    python run_campaign.py [--model MODEL] [--output PATH] [--quiet]

Examples:
    # Run with defaults
    python run_campaign.py
    
    # Use specific model
    python run_campaign.py --model openai:gpt-5.1
    
    # Custom output path
    python run_campaign.py --output my_campaign.md
    
    # Quiet mode (minimal output)
    python run_campaign.py --quiet
"""

import argparse
import sys
from pathlib import Path

import aisuite
from dotenv import load_dotenv

# Import from package - handle both direct execution and package import
try:
    from .pipeline import run_campaign_pipeline
except ImportError:
    # Running as script directly - add parent to path
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from market_research.pipeline import run_campaign_pipeline


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Run market research campaign generation pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --model openai:gpt-5.1
  %(prog)s --output my_campaign.md --quiet
        """
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="Model to use for agents (default: gpt-4o-mini). Examples: gpt-5.1, gpt-5.1-codex, gpt-4o"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Full output path for markdown report (overrides --output-dir and --topic)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Base output directory (default: output/)"
    )
    
    parser.add_argument(
        "--topic",
        type=str,
        default="sunglasses_campaign",
        help="Topic subdirectory name (default: sunglasses_campaign)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimize output (only show final results)"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Initialize client
    try:
        client = aisuite.Client()
    except Exception as e:
        print(f"❌ Error initializing aisuite client: {e}", file=sys.stderr)
        print("Make sure you have set up your API keys in .env", file=sys.stderr)
        return 1
    
    # Run pipeline
    try:
        results = run_campaign_pipeline(
            client=client,
            model=args.model,
            output_path=args.output,
            output_dir=args.output_dir,
            topic=args.topic,
            verbose=not args.quiet
        )
        
        # Print summary
        if args.quiet:
            print(f"\n✅ Campaign generated successfully!")
            print(f"📦 Report: {results['markdown_path']}")
            print(f"🖼️  Image: {results['visual']['image_path']}")
            print(f"💬 Quote: {results['quote_result']['quote']}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"\n❌ Error running pipeline: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
