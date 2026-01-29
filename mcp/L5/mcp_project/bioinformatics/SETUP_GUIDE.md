# Bioinformatics MCP Servers Setup Guide

This guide covers setting up existing MCP servers for protein analysis.

## Available Servers

| Server | Purpose | Language |
|--------|---------|----------|
| **UniProt MCP** | Protein database queries, sequences, features | Node.js |
| **AlphaFold MCP** | Protein structure predictions | Node.js |

---

## Prerequisites

```bash
# Node.js (for the MCP servers)
node --version  # Should be v18+

# Python (for our client)
mamba activate agentic-ai
```

---

## 1. UniProt MCP Server

### Installation

```bash
cd /Users/pleiadian53/work/agentic-ai-lab/mcp/L5/mcp_project/bioinformatics

# Clone the repository
git clone https://github.com/Augmented-Nature/Augmented-Nature-UniProt-MCP-Server.git uniprot-server
cd uniprot-server

# Install dependencies and build
npm install
npm run build
```

### Test the Server

```bash
# Run directly (for testing)
npm start
```

### Available Tools (26 total)

**Core Protein Analysis:**
- `search_proteins` - Search by name, keywords, organism
- `get_protein_info` - Comprehensive protein information
- `search_by_gene` - Find proteins by gene name
- `get_protein_sequence` - Get amino acid sequences (FASTA/JSON)
- `get_protein_features` - Domains, active sites, binding sites

**Comparative & Evolutionary:**
- `compare_proteins` - Side-by-side comparison
- `find_homologs` - Homologous proteins across species
- `find_orthologs` - Orthologous proteins
- `get_phylogenetic_data` - Evolutionary relationships

**Structure & Function:**
- `get_structure_info` - PDB references, structural data
- `analyze_domains` - InterPro, Pfam, SMART annotations
- `get_variants` - Disease-associated mutations
- `get_sequence_composition` - AA composition, hydrophobicity

**Biological Context:**
- `get_pathways` - KEGG, Reactome pathways
- `get_interactions` - Protein-protein interactions
- `search_by_go_term` - GO term search
- `search_by_localization` - Subcellular localization

---

## 2. AlphaFold MCP Server

### Installation

```bash
cd /Users/pleiadian53/work/agentic-ai-lab/mcp/L5/mcp_project/bioinformatics

# Clone the repository
git clone https://github.com/Augmented-Nature/AlphaFold-MCP-Server.git alphafold-server
cd alphafold-server

# Install dependencies and build
npm install
npm run build
```

### Available Tools

**Core Structure:**
- `get_structure` - Get AlphaFold prediction (PDB/CIF/JSON)
- `download_structure` - Download structure file
- `check_availability` - Check if prediction exists

**Search & Discovery:**
- `search_structures` - Search by protein/gene name
- `list_by_organism` - List structures for an organism
- `get_organism_stats` - Coverage statistics

**Confidence & Quality:**
- `get_confidence_scores` - Per-residue pLDDT scores
- `analyze_confidence_regions` - High/low confidence regions
- `get_prediction_metadata` - Version, date, quality metrics

**Batch Processing:**
- `batch_structure_info` - Multiple proteins at once
- `batch_download` - Download multiple structures
- `batch_confidence_analysis` - Analyze multiple proteins

---

## 3. Configuration

### Option A: Claude Desktop / Cursor

Add to your MCP client configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "uniprot": {
      "command": "node",
      "args": ["/Users/pleiadian53/work/agentic-ai-lab/mcp/L5/mcp_project/bioinformatics/uniprot-server/build/index.js"]
    },
    "alphafold": {
      "command": "node",
      "args": ["/Users/pleiadian53/work/agentic-ai-lab/mcp/L5/mcp_project/bioinformatics/alphafold-server/build/index.js"]
    }
  }
}
```

### Option B: Custom Python Client

See `bioinformatics_client.py` for a Python client that connects to these servers.

---

## 4. Example Queries

Once connected, you can ask:

**UniProt queries:**
- "Search for human insulin protein"
- "Get the sequence for UniProt P01308"
- "What are the functional domains of TP53?"
- "Find proteins involved in the MAPK pathway"

**AlphaFold queries:**
- "Get the AlphaFold structure for P04637 (p53)"
- "What's the confidence score for the insulin structure?"
- "Compare structures of human and mouse hemoglobin"

---

## 5. Future: Adding ESM-2 / ML Models

For ML-based protein analysis (ESM-2, ProtTrans, etc.), we'll create a custom server:

```
bioinformatics/
├── uniprot-server/          # Existing (Node.js)
├── alphafold-server/        # Existing (Node.js)
└── protein-ml-server/       # Custom (Python) - ESM-2, classification
    ├── protein_ml_server.py
    └── models/
        └── esm2/
```

This allows:
- Sequence embeddings with ESM-2
- Protein classification
- Function prediction
- Custom fine-tuned models

See `protein_ml_server.py` (to be created) for implementation.
