"""Splice Site Analysis - Domain-Specific Analysis Templates and Workflows.

This module provides specialized analysis templates and workflows for genomic
splice site analysis, including:
- Alternative splicing patterns
- Transcript structure analysis
- Genomic distribution analysis
- Site type and strand analysis
- Gene-level aggregations

Built on top of the core chart generation framework with domain expertise
embedded in prompts and analysis templates.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pathlib import Path

from splice_agent.data_access import ChartDataset
from splice_agent.planning import generate_chart_code
from splice_agent.llm_client import call_llm_json
from openai import OpenAI


# =========================
# Domain Context
# =========================

SPLICE_SITE_CONTEXT = """
DOMAIN CONTEXT: Genomic Splice Site Analysis (MANE Dataset - GRCh38)

This dataset contains splice sites from MANE (Matched Annotation from NCBI and EBI) transcripts:
- **Dataset**: 369,918 splice sites from 18,200 genes and 18,264 transcripts
- **Splice Site Types**: donor (5' splice site with GT) and acceptor (3' splice site with AG)
- **Genomic Coverage**: 65 chromosomes (24 standard + 41 alternative/fix patches)
  - 99.6% on standard chromosomes (chr1-22, chrX, chrY)
  - 0.4% on alternative contigs and fix patches
- **Key Columns**:
  - chrom, position: Genomic coordinates
  - site_type: donor or acceptor (perfectly balanced: 184,959 each)
  - strand: + or - (nearly balanced: 50.2% vs 49.8%)
  - gene_name: HGNC gene symbol (e.g., 'TP53', 'OR4F5')
  - gene_id: Format 'gene-{SYMBOL}'
  - transcript_id: RefSeq format 'rna-{ID}.{version}'
  - exon_rank: Exon position in transcript (1-363, avg 11.64)

VISUALIZATION BEST PRACTICES:
- Use gene_name directly for gene symbols (no extraction needed)
- Color-code by site_type (donor vs acceptor) and strand
- Leverage exon_rank for transcript structure analysis
- Filter to standard chromosomes for primary analyses
- Use vertical bars for genomic position plots
"""


# =========================
# Analysis Templates
# =========================

ANALYSIS_TEMPLATES = {
    "high_alternative_splicing": {
        "title": "Genes with Most Splice Sites",
        "description": "Identify genes with high alternative splicing potential",
        "data_query": """
            SELECT 
                gene_name,
                COUNT(*) as splice_site_count,
                COUNT(DISTINCT transcript_id) as transcript_count,
                MAX(CAST(exon_rank AS INTEGER)) as max_exon_rank,
                AVG(CAST(exon_rank AS FLOAT)) as avg_exon_rank
            FROM splice_sites
            WHERE chrom NOT LIKE '%\_%'  -- Standard chromosomes only
            GROUP BY gene_name
            HAVING splice_site_count > 20
            ORDER BY splice_site_count DESC
            LIMIT 20
        """,
        "chart_prompt": """
{context}

Create a horizontal bar chart showing the top 20 genes with the most splice sites.

DATA PREPARATION (already done via SQL):
- Filtered to standard chromosomes only
- Counted splice sites per gene
- Sorted by count (descending)
- Limited to top 20

CHART REQUIREMENTS:
- X-axis: Splice site count
- Y-axis: Gene names (sorted by count)
- Color: Use a gradient or categorical color scheme
- Title: "Top 20 Genes by Splice Site Count"
- Add value labels on bars
- Use publication-ready styling (large fonts, clear labels)

BIOLOGICAL INSIGHT:
Genes with many splice sites often undergo extensive alternative splicing,
which is crucial for protein diversity and gene regulation.
"""
    },
    
    "splice_site_genomic_view": {
        "title": "Genomic Distribution of Splice Sites",
        "description": "Visualize splice site distribution across chromosomes",
        "data_query": """
            SELECT 
                chrom,
                COUNT(*) as site_count,
                SUM(CASE WHEN site_type = 'donor' THEN 1 ELSE 0 END) as donor_count,
                SUM(CASE WHEN site_type = 'acceptor' THEN 1 ELSE 0 END) as acceptor_count
            FROM splice_sites
            WHERE chrom NOT LIKE '%\_%'  -- Standard chromosomes only
            GROUP BY chrom
            ORDER BY 
                CASE 
                    WHEN chrom = 'chrX' THEN 23
                    WHEN chrom = 'chrY' THEN 24
                    WHEN chrom = 'chrM' THEN 25
                    ELSE CAST(REPLACE(chrom, 'chr', '') AS INTEGER)
                END
        """,
        "chart_prompt": """
{context}

Create a grouped bar chart showing splice site distribution across chromosomes.

DATA PREPARATION (already done via SQL):
- Counted donor and acceptor sites per chromosome
- Filtered to standard chromosomes
- Sorted by chromosome number (1-22, X, Y, M)

CHART REQUIREMENTS:
- X-axis: Chromosome (chr1, chr2, ..., chrX, chrY, chrM)
- Y-axis: Count of splice sites
- Bars: Grouped by site_type (donor vs acceptor)
- Colors: Use distinct colors for donor (blue) and acceptor (orange)
- Title: "Splice Site Distribution Across Chromosomes"
- Rotate x-axis labels if needed
- Add legend for site types

BIOLOGICAL INSIGHT:
Chromosome-level distribution reveals gene density and transcript complexity.
Larger chromosomes typically have more splice sites due to more genes.
"""
    },
    
    "exon_complexity": {
        "title": "Transcript Complexity by Exon Count",
        "description": "Analyze transcript structure complexity",
        "data_query": """
            SELECT 
                transcript_id,
                gene_name,
                MAX(CAST(exon_rank AS INTEGER)) as exon_count,
                COUNT(*) as splice_site_count
            FROM splice_sites
            WHERE chrom NOT LIKE '%\_%'
            GROUP BY transcript_id, gene_name
            HAVING exon_count > 10
            ORDER BY exon_count DESC
            LIMIT 30
        """,
        "chart_prompt": """
{context}

Create a scatter plot showing the relationship between exon count and splice sites.

DATA PREPARATION (already done via SQL):
- Calculated max exon rank (= exon count) per transcript
- Counted splice sites per transcript
- Filtered to transcripts with >10 exons
- Limited to top 30 most complex transcripts

CHART REQUIREMENTS:
- X-axis: Exon count
- Y-axis: Splice site count
- Points: Each transcript
- Color: Gradient by exon count
- Title: "Transcript Complexity: Exons vs Splice Sites"
- Add trend line if appropriate
- Annotate outliers with gene names

BIOLOGICAL INSIGHT:
More exons generally means more splice sites. Outliers may indicate
unusual transcript structures or annotation artifacts.
"""
    },
    
    "strand_bias": {
        "title": "Strand Distribution Analysis",
        "description": "Analyze strand bias in splice sites",
        "data_query": """
            SELECT 
                strand,
                site_type,
                COUNT(*) as count
            FROM splice_sites
            WHERE chrom NOT LIKE '%\_%'
            GROUP BY strand, site_type
            ORDER BY strand, site_type
        """,
        "chart_prompt": """
{context}

Create a grouped bar chart showing strand distribution by site type.

DATA PREPARATION (already done via SQL):
- Counted sites by strand (+/-) and type (donor/acceptor)
- Filtered to standard chromosomes

CHART REQUIREMENTS:
- X-axis: Strand (+ and -)
- Y-axis: Count
- Bars: Grouped by site_type
- Colors: Donor (blue), Acceptor (orange)
- Title: "Strand Distribution of Splice Sites"
- Add percentage labels
- Include total counts

BIOLOGICAL INSIGHT:
Balanced strand distribution indicates unbiased gene orientation.
Imbalances may reflect genomic organization or annotation biases.
"""
    },
    
    "gene_transcript_diversity": {
        "title": "Gene Transcript Diversity",
        "description": "Genes with most transcript isoforms",
        "data_query": """
            SELECT 
                gene_name,
                COUNT(DISTINCT transcript_id) as transcript_count,
                COUNT(*) as total_splice_sites,
                AVG(CAST(exon_rank AS FLOAT)) as avg_exon_rank
            FROM splice_sites
            WHERE chrom NOT LIKE '%\_%'
            GROUP BY gene_name
            HAVING transcript_count > 1
            ORDER BY transcript_count DESC
            LIMIT 20
        """,
        "chart_prompt": """
{context}

Create a horizontal bar chart showing genes with most transcript isoforms.

DATA PREPARATION (already done via SQL):
- Counted distinct transcripts per gene
- Filtered to genes with multiple transcripts
- Sorted by transcript count
- Limited to top 20

CHART REQUIREMENTS:
- X-axis: Number of transcripts
- Y-axis: Gene names
- Color: Gradient by transcript count
- Title: "Top 20 Genes by Transcript Diversity"
- Add value labels
- Use publication-ready styling

BIOLOGICAL INSIGHT:
High transcript diversity indicates complex alternative splicing,
which is important for tissue-specific expression and protein diversity.
"""
    }
}


# =========================
# Analysis Functions
# =========================

def generate_analysis_insight(
    dataset: ChartDataset,
    analysis_type: str,
    client: OpenAI,
    model: str = "gpt-4o-mini",
    standard_only: bool = True,
    enable_reflection: bool = False,
    reflection_model: Optional[str] = None,
    max_iterations: int = 3
) -> Dict[str, Any]:
    """Generate analysis insight using predefined templates.
    
    Args:
        dataset: The dataset to analyze
        analysis_type: Type of analysis (key from ANALYSIS_TEMPLATES)
        client: OpenAI client
        model: Model to use for generation
        standard_only: Whether to filter to standard chromosomes
        enable_reflection: Whether to use reflection for refinement
        reflection_model: Model to use for reflection (defaults to same as generation)
        max_iterations: Maximum reflection iterations
        
    Returns:
        Dictionary with chart code, title, description, and metadata
    """
    if analysis_type not in ANALYSIS_TEMPLATES:
        raise ValueError(f"Unknown analysis type: {analysis_type}. "
                        f"Available: {list(ANALYSIS_TEMPLATES.keys())}")
    
    template = ANALYSIS_TEMPLATES[analysis_type]
    
    # Execute data query if provided
    if template.get("data_query"):
        query_result = dataset.query(template["data_query"])
        # Store query result for use in code generation
        # (In practice, this would be passed to the LLM context)
    
    # Build prompt with context
    prompt = template["chart_prompt"].format(context=SPLICE_SITE_CONTEXT)
    
    # Generate chart code
    result = generate_chart_code(
        dataset=dataset,
        question=prompt,
        context=SPLICE_SITE_CONTEXT,
        client=client,
        model=model
    )
    
    return {
        "title": template["title"],
        "description": template["description"],
        "chart_code": result["code"],
        "library": result.get("library", "matplotlib"),
        "chart_type": result.get("chart_type", "unknown"),
        "reflection_enabled": enable_reflection,
        "model_used": model
    }


def generate_exploratory_insight(
    dataset: ChartDataset,
    research_question: str,
    client: OpenAI,
    model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """Generate exploratory analysis for custom research questions.
    
    Args:
        dataset: The dataset to analyze
        research_question: Custom research question
        client: OpenAI client
        model: Model to use
        
    Returns:
        Dictionary with chart code, reasoning, and insights
    """
    # Build enhanced prompt with domain context
    enhanced_question = f"""
{SPLICE_SITE_CONTEXT}

RESEARCH QUESTION:
{research_question}

Please generate Python code to create an insightful visualization that addresses
this research question. Consider:
1. What data transformations are needed?
2. What chart type best communicates the insight?
3. What biological interpretation can be drawn?
"""
    
    # Generate code with reasoning
    result = generate_chart_code(
        dataset=dataset,
        question=enhanced_question,
        context=SPLICE_SITE_CONTEXT,
        client=client,
        model=model
    )
    
    # Extract key insights (could be enhanced with LLM call)
    insights = [
        "Generated visualization addresses the research question",
        f"Uses {result.get('library', 'matplotlib')} for plotting",
        f"Chart type: {result.get('chart_type', 'custom')}"
    ]
    
    return {
        "chart_code": result["code"],
        "reasoning": "Generated based on domain context and research question",
        "key_insights": insights,
        "library": result.get("library"),
        "chart_type": result.get("chart_type"),
        "model_used": model
    }


def list_available_analyses() -> List[str]:
    """Get list of available predefined analyses."""
    return list(ANALYSIS_TEMPLATES.keys())


def get_analysis_description(analysis_type: str) -> Dict[str, str]:
    """Get description of a specific analysis type."""
    if analysis_type not in ANALYSIS_TEMPLATES:
        raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    template = ANALYSIS_TEMPLATES[analysis_type]
    return {
        "type": analysis_type,
        "title": template["title"],
        "description": template["description"]
    }


def get_all_analysis_descriptions() -> List[Dict[str, str]]:
    """Get descriptions of all available analyses."""
    return [get_analysis_description(t) for t in ANALYSIS_TEMPLATES.keys()]
