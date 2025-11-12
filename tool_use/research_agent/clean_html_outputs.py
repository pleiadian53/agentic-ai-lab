#!/usr/bin/env python3
"""
Utility script to clean existing HTML files that have markdown code fences.

Usage:
    python clean_html_outputs.py                           # Clean all HTML files in research_outputs/
    python clean_html_outputs.py path/to/file.html         # Clean specific file
    python clean_html_outputs.py path/to/directory/        # Clean all HTML in directory
"""

import re
import sys
from pathlib import Path


def clean_html_content(html: str) -> str:
    """
    Remove markdown code fences and other artifacts from HTML.
    
    Args:
        html: Raw HTML content
        
    Returns:
        Cleaned HTML string
    """
    # Remove markdown code fences at start
    html = re.sub(r'^```html\s*\n?', '', html, flags=re.IGNORECASE)
    html = re.sub(r'^```\s*\n?', '', html)
    
    # Remove markdown code fences at end
    html = re.sub(r'\n?```\s*$', '', html)
    
    # Strip whitespace
    html = html.strip()
    
    return html


def clean_html_file(filepath: Path, dry_run: bool = False) -> bool:
    """
    Clean a single HTML file.
    
    Args:
        filepath: Path to HTML file
        dry_run: If True, only show what would be changed
        
    Returns:
        True if file was modified (or would be modified in dry_run)
    """
    try:
        original_content = filepath.read_text(encoding='utf-8')
        cleaned_content = clean_html_content(original_content)
        
        if original_content != cleaned_content:
            if dry_run:
                print(f"  Would clean: {filepath.name}")
                return True
            else:
                filepath.write_text(cleaned_content, encoding='utf-8')
                print(f"  ✅ Cleaned: {filepath.name}")
                return True
        else:
            if not dry_run:
                print(f"  ⏭️  Already clean: {filepath.name}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error processing {filepath.name}: {str(e)}")
        return False


def clean_directory(directory: Path, dry_run: bool = False) -> tuple[int, int]:
    """
    Clean all HTML files in a directory.
    
    Args:
        directory: Path to directory
        dry_run: If True, only show what would be changed
        
    Returns:
        Tuple of (files_cleaned, total_files)
    """
    html_files = list(directory.glob("*.html"))
    
    if not html_files:
        print(f"No HTML files found in {directory}")
        return 0, 0
    
    print(f"\nFound {len(html_files)} HTML file(s) in {directory}")
    
    cleaned_count = 0
    for html_file in html_files:
        if clean_html_file(html_file, dry_run=dry_run):
            cleaned_count += 1
    
    return cleaned_count, len(html_files)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clean markdown code fences from HTML files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clean_html_outputs.py
  python clean_html_outputs.py --dry-run
  python clean_html_outputs.py path/to/file.html
  python clean_html_outputs.py path/to/directory/
        """
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        default="research_outputs",
        help="Path to HTML file or directory (default: research_outputs/)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files"
    )
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if not path.exists():
        print(f"❌ Path not found: {path}")
        sys.exit(1)
    
    print("="*80)
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified")
    else:
        print("HTML Cleaning Utility")
    print("="*80)
    
    if path.is_file():
        # Clean single file
        if path.suffix.lower() != '.html':
            print(f"❌ Not an HTML file: {path}")
            sys.exit(1)
        
        print(f"\nCleaning file: {path}")
        clean_html_file(path, dry_run=args.dry_run)
        
    elif path.is_dir():
        # Clean directory
        cleaned, total = clean_directory(path, dry_run=args.dry_run)
        
        print("\n" + "="*80)
        if args.dry_run:
            print(f"Would clean {cleaned} of {total} file(s)")
        else:
            print(f"✅ Cleaned {cleaned} of {total} file(s)")
        print("="*80)
    
    else:
        print(f"❌ Invalid path: {path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
