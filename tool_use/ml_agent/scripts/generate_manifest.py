"""
Generate manifest.json for data files.

Creates a manifest file documenting all data files in a directory,
including size, checksums, and metadata.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROCESSED_DATA_DIR, RAW_DATA_DIR


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def count_csv_rows(file_path: Path) -> int:
    """Count rows in CSV file."""
    try:
        with open(file_path, "r") as f:
            return sum(1 for _ in f) - 1  # Subtract header
    except Exception:
        return -1


def count_csv_columns(file_path: Path) -> int:
    """Count columns in CSV file."""
    try:
        with open(file_path, "r") as f:
            header = f.readline()
            return len(header.split(","))
    except Exception:
        return -1


def generate_manifest(data_dir: Path, output_name: str = "manifest.json"):
    """
    Generate manifest.json for data directory.
    
    Args:
        data_dir: Directory containing data files
        output_name: Name of manifest file to create
    """
    print(f"Generating manifest for {data_dir}")
    
    manifest = {
        "version": "1.0.0",
        "generated": datetime.utcnow().isoformat() + "Z",
        "directory": str(data_dir.relative_to(Path.cwd())),
        "files": {}
    }
    
    # Process CSV files
    for file in data_dir.glob("*.csv"):
        print(f"  Processing {file.name}...")
        
        file_info = {
            "size_bytes": file.stat().st_size,
            "size_mb": round(file.stat().st_size / (1024 * 1024), 2),
            "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
        }
        
        # Add CSV-specific metadata
        if file.suffix == ".csv":
            rows = count_csv_rows(file)
            cols = count_csv_columns(file)
            if rows > 0:
                file_info["rows"] = rows
            if cols > 0:
                file_info["columns"] = cols
        
        # Compute hash for files < 100MB
        if file.stat().st_size < 100 * 1024 * 1024:
            file_info["sha256"] = compute_sha256(file)
        else:
            file_info["sha256"] = "skipped_large_file"
        
        manifest["files"][file.name] = file_info
    
    # Process other data files
    for pattern in ["*.txt", "*.json", "*.pkl"]:
        for file in data_dir.glob(pattern):
            if file.name == output_name:
                continue  # Skip the manifest itself
            
            print(f"  Processing {file.name}...")
            
            file_info = {
                "size_bytes": file.stat().st_size,
                "size_mb": round(file.stat().st_size / (1024 * 1024), 2),
                "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
            }
            
            # Add line count for text files
            if file.suffix == ".txt":
                try:
                    with open(file, "r") as f:
                        file_info["lines"] = sum(1 for _ in f)
                except Exception:
                    pass
            
            # Compute hash for small files
            if file.stat().st_size < 10 * 1024 * 1024:
                file_info["sha256"] = compute_sha256(file)
            
            manifest["files"][file.name] = file_info
    
    # Add regeneration command
    manifest["regenerate_command"] = "python scripts/download_tcga_data.py"
    
    # Save manifest
    output_path = data_dir / output_name
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Manifest saved to {output_path}")
    print(f"   Documented {len(manifest['files'])} files")
    
    return manifest


def print_manifest_summary(manifest: dict):
    """Print summary of manifest."""
    print("\n" + "=" * 60)
    print("Manifest Summary")
    print("=" * 60)
    
    total_size = sum(f["size_bytes"] for f in manifest["files"].values())
    total_size_mb = total_size / (1024 * 1024)
    
    print(f"Directory: {manifest['directory']}")
    print(f"Generated: {manifest['generated']}")
    print(f"Total files: {len(manifest['files'])}")
    print(f"Total size: {total_size_mb:.2f} MB")
    
    print("\nFiles:")
    for name, info in manifest["files"].items():
        size_str = f"{info['size_mb']:.2f} MB"
        extra = ""
        if "rows" in info:
            extra = f" ({info['rows']} rows × {info['columns']} cols)"
        elif "lines" in info:
            extra = f" ({info['lines']} lines)"
        print(f"  • {name}: {size_str}{extra}")


def main():
    """Generate manifests for all data directories."""
    print("=" * 60)
    print("ML Agent Data Manifest Generator")
    print("=" * 60)
    
    # Generate manifest for processed data
    if PROCESSED_DATA_DIR.exists() and any(PROCESSED_DATA_DIR.glob("*.csv")):
        manifest = generate_manifest(PROCESSED_DATA_DIR)
        print_manifest_summary(manifest)
    else:
        print(f"\n⚠️  No data found in {PROCESSED_DATA_DIR}")
        print("   Run download_tcga_data.py first!")
    
    # Generate manifest for raw data if it exists
    if RAW_DATA_DIR.exists() and any(RAW_DATA_DIR.glob("*.csv")):
        print("\n" + "=" * 60)
        manifest = generate_manifest(RAW_DATA_DIR)
        print_manifest_summary(manifest)


if __name__ == "__main__":
    main()
