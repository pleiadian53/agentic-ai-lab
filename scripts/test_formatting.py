#!/usr/bin/env python3
"""
Quick test script to demonstrate the new formatting capabilities.
This script reformats existing essay outputs with proper line wrapping.
"""

from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from reflection.research_agent.formatting import wrap_text, save_formatted_essay


def reformat_existing_essay(essay_path: Path, output_dir: Path) -> None:
    """Reformat an existing essay with proper line wrapping."""
    print(f"📄 Reformatting: {essay_path.name}")
    
    # Read the original essay
    essay_text = essay_path.read_text(encoding='utf-8')
    
    # Extract topic from filename (simple heuristic)
    basename = essay_path.stem.replace('_final', '').replace('_v1', '').replace('_v2', '')
    topic = basename.replace('_', ' ').title()
    
    # Count words
    word_count = len(essay_text.split())
    
    # Save formatted version
    output_path = output_dir / f"{basename}_formatted"
    
    files = save_formatted_essay(
        essay_text=essay_text,
        output_path=output_path,
        topic=topic,
        word_count=word_count,
        wrap_width=88,
        generate_pdf=False,  # Set to True if you have PDF tools installed
    )
    
    print(f"   ✅ Saved to:")
    for format_name, file_path in files.items():
        print(f"      - {file_path.name} ({format_name})")
    print()


def main():
    """Main entry point."""
    print("=" * 80)
    print("Essay Formatting Test")
    print("=" * 80)
    print()
    
    # Find existing essays
    essays_dir = project_root / "essays" / "agi_systems"
    
    if not essays_dir.exists():
        print(f"❌ Essays directory not found: {essays_dir}")
        return
    
    # Create output directory
    output_dir = essays_dir / "formatted"
    output_dir.mkdir(exist_ok=True)
    
    # Find essay files
    essay_files = list(essays_dir.glob("*.txt"))
    
    if not essay_files:
        print(f"❌ No essay files found in {essays_dir}")
        return
    
    print(f"Found {len(essay_files)} essay file(s)")
    print()
    
    # Reformat each essay
    for essay_file in essay_files:
        try:
            reformat_existing_essay(essay_file, output_dir)
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()
    
    print("=" * 80)
    print("✨ Formatting complete!")
    print(f"📁 Output directory: {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
