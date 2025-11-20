# Biology-Specific Domain Evaluation Guide

This guide shows how to use the biology-focused domain sets for evaluating research in computational biology, bioinformatics, RNA therapeutics, and genomics.

## New Domain Categories

### 1. Computational Biology & Bioinformatics

**`COMPUTATIONAL_BIOLOGY_DOMAINS`** includes:

- **Journals**: PLOS Computational Biology, Bioinformatics (Oxford), Nucleic Acids Research, BMC Bioinformatics, GigaScience, etc.
- **Databases**: NCBI, EBI, Ensembl, UniProt, PDB, KEGG, Reactome, STRING, etc.
- **Resources**: Bioconductor, BioCyc, GeneCards, OMIM, etc.

**Total**: ~50 authoritative domains

### 2. RNA Therapeutics & RNA Biology

**`RNA_THERAPEUTICS_DOMAINS`** includes:

- **Specialized journals**: RNA journal, Nucleic Acid Therapeutics, RNA Biology, Silence
- **Major journals**: Cell, Nature, Science, NEJM, PNAS
- **RNA databases**: RNAcentral, miRBase, tRNA database, RNA modification databases
- **Clinical resources**: ClinicalTrials.gov, FDA, EMA
- **Research institutions**: UMass RNA Therapeutics Institute, Broad Institute, Sanger Institute

**Total**: ~25 authoritative domains

### 3. Genomics & Genetics

**`GENOMICS_DOMAINS`** includes:

- **Journals**: Genome Biology, Genome Research, Genetics, Nature Genetics, AJHG
- **Databases**: gnomAD, 1000 Genomes, GTEx, ENCODE, Roadmap Epigenomics
- **Organizations**: NHGRI, ASHG

**Total**: ~15 authoritative domains

### 4. Biology-Focused (Combined)

**`BIOLOGY_FOCUSED_DOMAINS`** combines:
- All academic domains
- All educational domains
- All government domains
- All computational biology domains
- All RNA therapeutics domains
- All genomics domains

**Total**: ~150+ authoritative domains for life sciences research

## Usage Examples

### Example 1: Evaluate Computational Biology Research

```python
from eval import DomainEvaluator, COMPUTATIONAL_BIOLOGY_DOMAINS

# Create evaluator for computational biology
evaluator = DomainEvaluator(
    preferred_domains=COMPUTATIONAL_BIOLOGY_DOMAINS,
    min_ratio=0.6  # Require 60% from comp bio sources
)

# Evaluate research output
research_output = """
Recent advances in protein structure prediction:
- https://www.nature.com/articles/s41586-021-03819-2
- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8371605/
- https://www.uniprot.org/help/alphafold
- https://www.rcsb.org/structure/7MHP
"""

result = evaluator.evaluate_text(research_output)
print(result.status)  # ✅ PASS (100% from comp bio sources)
```

### Example 2: RNA Therapeutics Research

```python
from eval import get_domain_set

# Get RNA therapeutics domains
rna_domains = get_domain_set('rna_therapeutics')

# Create evaluator
evaluator = DomainEvaluator(
    preferred_domains=rna_domains,
    min_ratio=0.7  # Strict threshold for therapeutic research
)

# Evaluate
result = evaluator.evaluate_text(rna_research_output)

if result.passed:
    print(f"✅ High-quality RNA therapeutics sources: {result.ratio:.1%}")
else:
    print(f"⚠️ Warning: Only {result.ratio:.1%} from trusted RNA sources")
```

### Example 3: Multi-Domain Biology Research

```python
from eval import create_custom_domain_set

# Combine multiple biology categories
my_domains = create_custom_domain_set(
    'computational_biology',
    'rna_therapeutics',
    'genomics',
    extra_domains={
        'mybiolab.edu',  # Your institution
        'specialized-journal.org'  # Field-specific journal
    }
)

evaluator = DomainEvaluator(preferred_domains=my_domains, min_ratio=0.5)
result = evaluator.evaluate(research_output)
```

### Example 4: Use Biology-Focused Preset

```python
from eval import BIOLOGY_FOCUSED_DOMAINS

# Use comprehensive biology domain set
evaluator = DomainEvaluator(
    preferred_domains=BIOLOGY_FOCUSED_DOMAINS,
    min_ratio=0.5
)

# This includes ALL biology-related domains
result = evaluator.evaluate_text(research_output)
```

### Example 5: Integration with Research Agent

```python
from tool_use.research_agent import generate_research_report_with_tools
from eval import DomainEvaluator, COMPUTATIONAL_BIOLOGY_DOMAINS

# Generate research on computational biology topic
topic = "recent advances in protein folding prediction using deep learning"
report = generate_research_report_with_tools(topic)

# Evaluate with computational biology domains
evaluator = DomainEvaluator(
    preferred_domains=COMPUTATIONAL_BIOLOGY_DOMAINS,
    min_ratio=0.6
)
result = evaluator.evaluate_text(report)

# Display results
from eval.visualize import display_evaluation
display_evaluation(result)

if not result.passed:
    print(f"⚠️ Consider re-running with more specific search terms")
    print(f"Current ratio: {result.ratio:.1%}")
```

### Example 6: Batch Evaluation for Multiple Topics

```python
from eval import DomainEvaluator, BIOLOGY_FOCUSED_DOMAINS
from eval.metrics import compute_domain_metrics

# Topics in different biology subfields
topics = [
    ("CRISPR gene editing mechanisms", "rna_therapeutics"),
    ("protein-protein interaction networks", "computational_biology"),
    ("single-cell RNA sequencing analysis", "genomics"),
]

evaluator = DomainEvaluator(
    preferred_domains=BIOLOGY_FOCUSED_DOMAINS,
    min_ratio=0.6
)

results = []
for topic, category in topics:
    output = research_function(topic)
    result = evaluator.evaluate_text(output)
    results.append(result)
    print(f"{topic}: {result.status} ({result.ratio:.1%})")

# Aggregate metrics
metrics = compute_domain_metrics(results)
print(f"\nOverall pass rate: {metrics['pass_rate']:.1%}")
print(f"Average quality: {metrics['avg_ratio']:.1%}")
```

## Domain Coverage Statistics

### Computational Biology Domains

| Category | Count | Examples |
|----------|-------|----------|
| Journals | 25 | PLOS Comp Bio, Bioinformatics, NAR |
| Databases | 20 | NCBI, EBI, UniProt, PDB, KEGG |
| Resources | 10 | Bioconductor, BioCyc, GeneCards |

### RNA Therapeutics Domains

| Category | Count | Examples |
|----------|-------|----------|
| Specialized Journals | 4 | RNA journal, Nucleic Acid Therapeutics |
| Major Journals | 7 | Cell, Nature, Science, NEJM |
| RNA Databases | 5 | RNAcentral, miRBase, tRNA database |
| Clinical | 3 | ClinicalTrials.gov, FDA, EMA |
| Institutions | 4 | UMass RTI, Broad, Sanger, JAX |

### Genomics Domains

| Category | Count | Examples |
|----------|-------|----------|
| Journals | 5 | Genome Biology, Genome Research, Genetics |
| Databases | 7 | gnomAD, 1000 Genomes, GTEx, ENCODE |
| Organizations | 2 | NHGRI, ASHG |

## Best Practices for Biology Research

### 1. Choose Appropriate Domain Set

```python
# For general biology research
domains = get_domain_set('biology')

# For specific subfield
domains = get_domain_set('rna_therapeutics')

# For custom combination
domains = create_custom_domain_set('computational_biology', 'genomics')
```

### 2. Set Appropriate Thresholds

```python
# Strict (80%+): For clinical/therapeutic research
evaluator = DomainEvaluator(min_ratio=0.8)

# Moderate (60%+): For academic research
evaluator = DomainEvaluator(min_ratio=0.6)

# Lenient (40%+): For exploratory/interdisciplinary research
evaluator = DomainEvaluator(min_ratio=0.4)
```

### 3. Add Field-Specific Domains

```python
from eval import COMPUTATIONAL_BIOLOGY_DOMAINS

# Add your institution and field-specific sources
my_domains = COMPUTATIONAL_BIOLOGY_DOMAINS | {
    'myuniversity.edu',
    'specialized-bio-journal.org',
    'field-specific-database.org'
}

evaluator = DomainEvaluator(preferred_domains=my_domains)
```

### 4. Track Quality Over Time

```python
from eval.integration import EvaluatedResearchAgent
from eval import BIOLOGY_FOCUSED_DOMAINS

# Wrap research function
agent = EvaluatedResearchAgent(
    research_function,
    preferred_domains=BIOLOGY_FOCUSED_DOMAINS,
    min_ratio=0.6
)

# Run multiple evaluations
for topic in biology_topics:
    result = agent(topic)

# Analyze trends
print(f"Pass rate: {agent.get_pass_rate():.1%}")
print(f"Avg quality: {agent.get_avg_ratio():.1%}")
```

## Common Use Cases

### Use Case 1: Drug Discovery Research

```python
from eval import create_custom_domain_set

drug_discovery_domains = create_custom_domain_set(
    'rna_therapeutics',
    'computational_biology',
    extra_domains={
        'drugbank.ca',
        'chembl.ebi.ac.uk',
        'pubchem.ncbi.nlm.nih.gov'
    }
)
```

### Use Case 2: Genomic Medicine

```python
from eval import create_custom_domain_set

genomic_medicine_domains = create_custom_domain_set(
    'genomics',
    'rna_therapeutics',
    extra_domains={
        'clinvar.ncbi.nlm.nih.gov',
        'cbioportal.org',
        'cancer.sanger.ac.uk'
    }
)
```

### Use Case 3: Systems Biology

```python
from eval import create_custom_domain_set

systems_biology_domains = create_custom_domain_set(
    'computational_biology',
    'genomics',
    extra_domains={
        'systemsbiology.org',
        'cellcollective.org',
        'biomodels.net'
    }
)
```

## Extending the Domain Lists

To add new domains for your specific field:

```python
# 1. Define your custom set
MY_FIELD_DOMAINS = {
    'journal1.org',
    'journal2.org',
    'database1.edu',
    'database2.gov',
}

# 2. Combine with existing sets
from eval import COMPUTATIONAL_BIOLOGY_DOMAINS

my_domains = COMPUTATIONAL_BIOLOGY_DOMAINS | MY_FIELD_DOMAINS

# 3. Use in evaluator
evaluator = DomainEvaluator(preferred_domains=my_domains)
```

Or contribute back to the project by adding to `eval/config.py`!

## Summary

The biology-focused domain sets provide:

- ✅ **150+ authoritative sources** for life sciences research
- ✅ **Organized by subfield** (comp bio, RNA, genomics)
- ✅ **Easy to combine** for interdisciplinary research
- ✅ **Extensible** for field-specific needs
- ✅ **Ready to use** with research agent workflows

Perfect for evaluating research quality in:
- Computational biology
- Bioinformatics
- RNA therapeutics
- Genomics and genetics
- Drug discovery
- Precision medicine
- Systems biology
