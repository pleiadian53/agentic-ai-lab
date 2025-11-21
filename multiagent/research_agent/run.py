import argparse
import sys
from pathlib import Path

# Add project root to path to allow imports if run directly
sys.path.append(str(Path(__file__).parent.parent.parent))

from multiagent.research_agent import pipeline

def main():
    parser = argparse.ArgumentParser(description="AI Research Agent CLI")
    parser.add_argument("topic", help="Research topic to investigate")
    parser.add_argument("--model", default="openai:gpt-4o", help="Model to use (e.g., openai:gpt-4o, openai:gpt-5.1-codex-mini)")
    parser.add_argument("--output", help="Path to save the final report", default=None)
    
    args = parser.parse_args()
    
    try:
        results = pipeline.generate_research_report(args.topic, model=args.model)
        
        report = results.get("final_report", "")
        if report:
            print("\n✅ Final Report Generated:\n")
            print("="*60)
            print(report)
            print("="*60)
            
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(report)
                print(f"Saved to {output_path}")
            else:
                # Save to default location
                filename = f"research_{args.topic.replace(' ', '_')}.md"
                with open(filename, "w") as f:
                    f.write(report)
                print(f"Saved to {filename}")
        else:
            print("❌ No report generated.")
            
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
