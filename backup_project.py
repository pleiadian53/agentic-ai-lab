#!/usr/bin/env python3
"""
Project Backup Script
Backs up .py, .ipynb, and .md files and creates a timestamped zip archive.
"""

import os
import zipfile
from pathlib import Path
from datetime import datetime
import argparse
import sys


def get_backup_filename(project_name: str, backup_dir: Path, use_timestamp: bool = False) -> Path:
    """Generate a backup filename."""
    if use_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return backup_dir / f"{project_name}_backup_{timestamp}.zip"
    else:
        return backup_dir / f"{project_name}_backup.zip"


def collect_files(root_dir: Path, extensions: list[str], exclude_dirs: list[str]) -> list[Path]:
    """
    Collect all files with specified extensions, excluding certain directories.
    
    Args:
        root_dir: Root directory to search
        extensions: List of file extensions to include (e.g., ['.py', '.ipynb'])
        exclude_dirs: List of directory names to exclude
    
    Returns:
        List of Path objects for files to backup
    """
    files_to_backup = []
    exclude_dirs_set = set(exclude_dirs)
    
    for item in root_dir.rglob('*'):
        # Skip if any parent directory is in exclude list
        if any(part in exclude_dirs_set for part in item.parts):
            continue
        
        # Check if file has one of the desired extensions
        if item.is_file() and item.suffix in extensions:
            files_to_backup.append(item)
    
    return sorted(files_to_backup)


def create_backup(
    root_dir: Path,
    backup_dir: Path,
    extensions: list[str],
    exclude_dirs: list[str],
    project_name: str,
    verbose: bool = False,
    use_timestamp: bool = False
) -> Path:
    """
    Create a zip backup of specified files.
    
    Args:
        root_dir: Root directory of the project
        backup_dir: Directory where backup zip will be created
        extensions: File extensions to include
        exclude_dirs: Directories to exclude
        project_name: Name of the project (used in backup filename)
        verbose: Print detailed progress
    
    Returns:
        Path to the created backup file
    """
    # Collect files
    print(f"Scanning {root_dir} for files...")
    files = collect_files(root_dir, extensions, exclude_dirs)
    
    if not files:
        print("No files found to backup!")
        sys.exit(1)
    
    print(f"Found {len(files)} files to backup")
    
    # Create backup directory if it doesn't exist
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate backup filename
    backup_file = get_backup_filename(project_name, backup_dir, use_timestamp)
    
    # Create zip archive
    print(f"Creating backup: {backup_file}")
    
    with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files:
            # Calculate relative path from root_dir
            arcname = file_path.relative_to(root_dir)
            
            if verbose:
                print(f"  Adding: {arcname}")
            
            zipf.write(file_path, arcname)
    
    # Get backup file size
    backup_size = backup_file.stat().st_size
    size_mb = backup_size / (1024 * 1024)
    
    print(f"\n✓ Backup created successfully!")
    print(f"  Location: {backup_file}")
    print(f"  Size: {size_mb:.2f} MB")
    print(f"  Files: {len(files)}")
    
    return backup_file


def main():
    parser = argparse.ArgumentParser(
        description="Backup project files (.py, .ipynb, .md, .yaml, .json) to a zip archive"
    )
    parser.add_argument(
        "--root-dir",
        type=Path,
        default=Path.cwd(),
        help="Root directory of the project (default: current directory)"
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=Path.cwd() / "backups",
        help="Directory to store backups (default: ./backups)"
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=[".py", ".ipynb", ".md", ".yaml", ".yml", ".json"],
        help="File extensions to backup (default: .py .ipynb .md .yaml .yml .json)"
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[
            ".git", "__pycache__", ".pytest_cache", "node_modules",
            ".venv", "venv", "env", ".ipynb_checkpoints",
            "backups", ".mypy_cache", ".ruff_cache"
        ],
        help="Directories to exclude from backup"
    )
    parser.add_argument(
        "--project-name",
        type=str,
        help="Project name for backup file (default: directory name)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed progress"
    )
    parser.add_argument(
        "--timestamp",
        action="store_true",
        help="Add timestamp to backup filename (prevents overwriting)"
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    root_dir = args.root_dir.resolve()
    backup_dir = args.backup_dir.resolve()
    
    # Determine project name
    project_name = args.project_name or root_dir.name
    
    # Ensure extensions start with dot
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in args.extensions]
    
    print("=" * 60)
    print("Project Backup Script")
    print("=" * 60)
    print(f"Project: {project_name}")
    print(f"Root directory: {root_dir}")
    print(f"Backup directory: {backup_dir}")
    print(f"Extensions: {', '.join(extensions)}")
    print(f"Excluding: {', '.join(args.exclude)}")
    print("=" * 60)
    print()
    
    # Create backup
    try:
        backup_file = create_backup(
            root_dir=root_dir,
            backup_dir=backup_dir,
            extensions=extensions,
            exclude_dirs=args.exclude,
            project_name=project_name,
            verbose=args.verbose,
            use_timestamp=args.timestamp
        )
    except Exception as e:
        print(f"Error creating backup: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
