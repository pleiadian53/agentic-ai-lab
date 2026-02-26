# ML Agent Data Patterns

## Documentation Pattern Implemented

Following the pattern you established with `tcga_processed.md`, we now have a complete data management system:

### Files Created

```
tool_use/ml_agent/data/
├── README.md                      # ✅ Data catalog
├── .gitignore                     # ✅ Excludes large files
├── processed/
│   ├── tcga_processed.csv         # Generated (gitignored)
│   ├── tcga_processed.md          # Your documentation (committed)
│   ├── manifest.json              # Generated (committed)
│   └── selected_genes.txt         # Generated (gitignored)
└── raw/
    └── (similar structure)
```

## Pattern Benefits

### 1. GitHub-Friendly
- Large `.csv` files are gitignored
- Documentation `.md` files are committed
- Anyone browsing GitHub can understand the data

### 2. Self-Documenting
Each dataset has:
- **`.md`** - Human-readable documentation
- **`manifest.json`** - Machine-readable metadata
- **Regeneration script** - Reproducibility

### 3. Discoverable
- `data/README.md` - Central catalog
- Cross-references to related files
- Clear provenance and versioning

## Usage Workflow

### For New Datasets

1. **Generate data**:
   ```bash
   python scripts/download_new_data.py
   ```

2. **Create documentation** (like your `tcga_processed.md`):
   - Dataset statistics
   - Schema description
   - Modeling recommendations
   - Clinical context
   - Version history

3. **Generate manifest**:
   ```bash
   python scripts/generate_manifest.py
   ```

4. **Update catalog**:
   - Add entry to `data/README.md`
   - Cross-reference related datasets

### For Existing Datasets

When someone clones the repo:

1. **Read documentation**: `tcga_processed.md` explains the data
2. **Check manifest**: `manifest.json` shows expected files
3. **Regenerate data**: `python scripts/download_tcga_data.py`
4. **Verify**: `python scripts/generate_manifest.py`

## Centralization Decision

### Current Approach: Agent-Local Data ✅

**Rationale**:
- ML agent is self-contained and portable
- No other agents currently need TCGA data
- Simpler paths within the agent
- Easy to distribute as standalone package

### When to Centralize

Move to `/data/tcga/` when:
- 2+ agents need TCGA data
- Data becomes a shared resource
- Cross-agent analysis is needed

### Migration Path

If we centralize later:

```python
# config.py with fallback
def get_tcga_data():
    # Try shared location first
    shared = PROJECT_ROOT / "data" / "tcga" / "tcga_processed.csv"
    if shared.exists():
        return shared
    
    # Fallback to local
    local = ML_AGENT_DIR / "data" / "processed" / "tcga_processed.csv"
    if local.exists():
        return local
    
    raise FileNotFoundError("Run download_tcga_data.py to generate data")
```

## Manifest System

### Purpose
- Document files without committing them
- Track checksums for integrity
- Record metadata (size, rows, columns)
- Enable verification

### Generated Content

```json
{
  "version": "1.0.0",
  "generated": "2024-11-06T22:15:00Z",
  "files": {
    "tcga_processed.csv": {
      "size_mb": 50.23,
      "rows": 500,
      "columns": 1001,
      "sha256": "abc123...",
      "modified": "2024-11-06T20:00:00"
    }
  },
  "regenerate_command": "python scripts/download_tcga_data.py"
}
```

### Usage

```bash
# Generate manifest after creating data
python scripts/generate_manifest.py

# Verify data integrity
python scripts/generate_manifest.py  # Regenerate and compare
```

## Git Strategy

### What Gets Committed

✅ **Documentation**:
- `*.md` files (your pattern!)
- `manifest.json` files
- `README.md` catalogs
- `.gitignore` rules

✅ **Code**:
- Download scripts
- Processing scripts
- Manifest generators

✅ **Small Reference Files**:
- Schema examples (`*_schema.csv`)
- Sample data (`*_sample.csv`, <100 rows)

### What Gets Ignored

❌ **Large Data Files**:
- `*.csv` (except small samples)
- `*.pkl`, `*.h5` (models, arrays)
- `*.parquet`, `*.feather`
- Raw downloads

❌ **Generated Artifacts**:
- Temporary files
- Cache directories
- Intermediate outputs

## Cross-Agent Patterns

### Consistent Naming

```
dataset_name.csv        # Data
dataset_name.md         # Documentation (your pattern)
dataset_name_schema.csv # Schema reference
manifest.json           # Metadata
```

### Related Datasets Section

In each `.md` file:

```markdown
## Related Datasets

- **TCGA v2.0**: Expanded cancer types
- **GTEx Normal Tissue**: Comparison baseline
- **Feature Importance**: `models/feature_importance.csv`
```

### Version Tracking

In each `.md` file:

```markdown
## Version History

- **v1.0.0** (2024-11-06): Initial dataset
  - 500 samples, 5 cancer types
  - 1000 genes selected
```

## Tools Provided

### 1. Manifest Generator

```bash
python scripts/generate_manifest.py
```

Generates `manifest.json` with:
- File sizes and checksums
- Row/column counts for CSVs
- Modification timestamps

### 2. Data Catalog

`data/README.md` provides:
- Overview of all datasets
- Usage examples
- Regeneration instructions
- Troubleshooting

### 3. Gitignore Rules

`data/.gitignore` ensures:
- Large files excluded
- Documentation included
- Consistent across agents

## Best Practices Summary

1. **Document First**: Create `.md` before committing anything
2. **Generate Manifests**: Always create `manifest.json` for data files
3. **Update Catalogs**: Keep `README.md` current
4. **Test Regeneration**: Ensure data can be recreated from scripts
5. **Cross-Reference**: Link related datasets and models

## Example: Adding New Dataset

```bash
# 1. Generate data
python scripts/download_new_data.py

# 2. Create documentation (manual)
# Edit data/processed/new_dataset.md

# 3. Generate manifest
python scripts/generate_manifest.py

# 4. Update catalog
# Edit data/README.md to add entry

# 5. Commit documentation only
git add data/processed/new_dataset.md
git add data/processed/manifest.json
git add data/README.md
git commit -m "Add new_dataset documentation"
```

## Future Enhancements

### Potential Additions

1. **Data versioning**: Track dataset versions explicitly
2. **Checksums validation**: Verify data integrity on load
3. **Download helpers**: Automated data fetching
4. **Sample generators**: Create small samples for testing
5. **Schema validators**: Ensure data matches expected schema

### Shared Data Directory

When needed, create:

```
/data/                  # Project root
├── README.md           # Central catalog
├── tcga/               # Shared TCGA data
├── financial/          # Shared financial data
└── common/             # Common reference data
```

## Summary

Your `tcga_processed.md` pattern is now:

✅ **Standardized** - Template for all datasets  
✅ **Automated** - Manifest generation script  
✅ **Cataloged** - Central `README.md`  
✅ **Git-Friendly** - Large files ignored, docs committed  
✅ **Portable** - Agent-local for now, centralizable later  
✅ **Discoverable** - Easy to browse on GitHub  

This keeps the data pipeline **well-documented and maintainable**! 🎯
