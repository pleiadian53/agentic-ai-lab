"""Example usage of the market_research package.

This script demonstrates how to use the refactored market research
multi-agent system both as a complete pipeline and with individual agents.
"""

import aisuite
from dotenv import load_dotenv

# Import the package
from market_research import (
    run_campaign_pipeline,
    market_research_agent,
    graphic_designer_agent,
    copywriter_agent,
    packaging_agent,
)


def example_full_pipeline():
    """Example 1: Run the complete pipeline in one call."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Full Pipeline")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize client
    client = aisuite.Client()
    
    # Run complete pipeline
    results = run_campaign_pipeline(
        client=client,
        model="openai:o4-mini",
        verbose=True
    )
    
    # Access results
    print("\n📊 Pipeline Results:")
    print(f"  - Report: {results['markdown_path']}")
    print(f"  - Image: {results['visual']['image_path']}")
    print(f"  - Quote: {results['quote_result']['quote']}")
    
    return results


def example_individual_agents():
    """Example 2: Use agents individually for more control."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Individual Agents")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize client
    client = aisuite.Client()
    
    # Step 1: Market Research
    print("\n🕵️‍♂️ Running Market Research Agent...")
    trends = market_research_agent(
        client=client,
        model="openai:o4-mini",
        verbose=True
    )
    
    # Step 2: Graphic Design
    print("\n🎨 Running Graphic Designer Agent...")
    visual = graphic_designer_agent(
        client=client,
        trend_insights=trends,
        model="openai:o4-mini",
        verbose=True
    )
    
    # Step 3: Copywriting
    print("\n✍️  Running Copywriter Agent...")
    copy = copywriter_agent(
        client=client,
        image_path=visual["image_path"],
        trend_summary=trends,
        model="openai:o4-mini",
        verbose=True
    )
    
    # Step 4: Packaging
    print("\n📦 Running Packaging Agent...")
    report_path = packaging_agent(
        client=client,
        trend_summary=trends,
        image_url=visual["image_path"],
        quote=copy["quote"],
        justification=copy["justification"],
        output_path="example_campaign.md",
        model="openai:o4-mini",
        verbose=True
    )
    
    print(f"\n✅ Campaign complete! Report: {report_path}")
    
    return {
        "trends": trends,
        "visual": visual,
        "copy": copy,
        "report": report_path
    }


def example_custom_model():
    """Example 3: Use a different model (e.g., GPT-5.1)."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Custom Model (GPT-5.1)")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize client
    client = aisuite.Client()
    
    # Run with GPT-5.1 (if available)
    results = run_campaign_pipeline(
        client=client,
        model="openai:gpt-5.1",  # Use latest model
        output_path="campaign_gpt51.md",
        verbose=True
    )
    
    print(f"\n✅ Campaign generated with GPT-5.1!")
    print(f"📦 Report: {results['markdown_path']}")
    
    return results


if __name__ == "__main__":
    # Choose which example to run
    import sys
    
    if len(sys.argv) > 1:
        example = sys.argv[1]
    else:
        example = "full"
    
    if example == "full":
        example_full_pipeline()
    elif example == "individual":
        example_individual_agents()
    elif example == "custom":
        example_custom_model()
    else:
        print("Usage: python example.py [full|individual|custom]")
        print("\nExamples:")
        print("  python example.py full        # Run complete pipeline")
        print("  python example.py individual  # Use agents individually")
        print("  python example.py custom      # Use GPT-5.1 model")
