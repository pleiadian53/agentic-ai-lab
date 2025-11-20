"""Splice Site Analysis Driver - Domain-Specific Chart Generation.

This script demonstrates how to use the chart agent for genomic splice site analysis
with guided, insightful visualizations rather than open-ended prompts.

Key Strategy for LLM-Generated Insights:
1. Provide domain context in prompts
2. Use structured analysis templates
3. Combine data queries with visualization requests
4. Let LLM choose best chart type for the question
5. Use reflection to ensure biological relevance

Usage:
    python -m chart_agent.examples.analyze_splice_sites --data data/splice_sites_enhanced.tsv
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

from openai import OpenAI

from chart_agent.llm_client import call_llm_json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load from .env in current directory or parent directories
except ImportError:
    # dotenv not installed, environment variables must be set manually
    pass

# Assuming chart_agent modules are available
# from chart_agent import DuckDBDataset, chart_agent


# =========================
# Domain-Specific Prompts
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
# Guided Analysis Templates
# =========================

ANALYSIS_TEMPLATES = {
    "high_alternative_splicing": {
        "title": "Genes with Most Splice Sites",
        "description": "Identify genes with many splice sites",
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
- Grouped by gene_name
- Counted total splice sites per gene
- Limited to genes with > 20 splice sites

VISUALIZATION REQUIREMENTS:
- X-axis: Number of splice sites
- Y-axis: Gene name (sorted by splice site count)
- Color bars by max_exon_rank (use colormap to show transcript complexity)
- Add colorbar legend
- Title: "Genes with Most Splice Sites (Standard Chromosomes)"
- Include subtitle with filter criteria

INSIGHTS TO HIGHLIGHT:
- Which genes have the most splice sites?
- Is there correlation between splice site count and exon count (max_exon_rank)?
""",
    },
    
    "splice_site_genomic_view": {
        "title": "Splice Site Positions on Genomic Region",
        "description": "Visualize splice sites as vertical bars",
        "data_query": """
            SELECT 
                CAST(position AS INTEGER) as position,
                site_type,
                strand,
                gene_name,
                CAST(exon_rank AS INTEGER) as exon_rank
            FROM splice_sites
            WHERE chrom = 'chr17'
              AND CAST(position AS INTEGER) BETWEEN 7571719 AND 7590868
            ORDER BY position
        """,
        "chart_prompt": """
{context}

Create a genomic visualization showing splice sites as vertical bars.

DATA: Splice sites on chr17:7571719-7590868 (TP53 region example)

VISUALIZATION REQUIREMENTS:
- X-axis: Genomic position (base pairs)
- Y-axis: Exon rank (to show transcript structure)
- Plot vertical bars or scatter points at each splice site position
- Color by site_type: donor (blue), acceptor (red)
- Size or alpha by strand (+ vs -)
- Add gene_name annotations for distinct genes
- Title: "Splice Sites on chr17:7571719-7590868 (TP53 Region)"
- Grid for readability

STYLE:
- Use matplotlib scatter or stem plot
- Show exon structure through y-axis positioning
- Legend for splice site types and strand
- Professional genomics paper style
""",
    },
    
    "site_type_distribution": {
        "title": "Splice Site Type Distribution by Chromosome",
        "description": "Analyze splice site types across chromosomes",
        "data_query": """
            SELECT 
                chrom,
                site_type,
                COUNT(*) as count
            FROM splice_sites
            GROUP BY chrom, site_type
            ORDER BY chrom
        """,
        "chart_prompt": """
{context}

Create a stacked or grouped bar chart showing splice site type distribution by chromosome.

VISUALIZATION REQUIREMENTS:
- X-axis: Chromosome (chr1, chr2, ..., chrX, chrY)
- Y-axis: Count of splice sites
- Stacked or grouped bars by site_type (donor vs acceptor)
- Color by site_type: donor (blue), acceptor (orange)
- Title: "Splice Site Type Distribution by Chromosome"
- Legend for site types
- Rotate x-axis labels if needed

INSIGHTS TO HIGHLIGHT:
- Are donor and acceptor sites balanced across chromosomes?
- Which chromosomes have most splice sites?
""",
    },
    
    "chromosome_coverage": {
        "title": "Splice Site Coverage Across Chromosomes",
        "description": "Overview of splice site distribution by chromosome",
        "data_query": """
            SELECT 
                chrom,
                COUNT(*) as splice_site_count,
                COUNT(DISTINCT gene_id) as gene_count,
                COUNT(DISTINCT transcript_id) as transcript_count
            FROM splice_sites
            GROUP BY chrom
            ORDER BY chrom
        """,
        "chart_prompt": """
{context}

Create a multi-panel visualization showing splice site coverage across chromosomes.

VISUALIZATION REQUIREMENTS:
- Top panel: Bar chart of splice site counts per chromosome
- Bottom panel: Bar chart of gene counts per chromosome
- X-axis: Chromosome (chr1, chr2, ..., chrX, chrY)
- Shared x-axis between panels
- Color bars by transcript count (colormap)
- Title: "Splice Site Distribution Across Chromosomes"

LAYOUT:
- Use plt.subplots(2, 1, figsize=(14, 8), sharex=True)
- Tight layout
- Rotate x-axis labels if needed

INSIGHTS:
- Which chromosomes have most splice sites?
- Is there correlation between gene count and splice site count?
""",
    },
    
    "exon_complexity_analysis": {
        "title": "Transcript Complexity by Exon Count",
        "description": "Analyze transcript complexity using exon rank distribution",
        "data_query": """
            SELECT 
                gene_name,
                transcript_id,
                MAX(CAST(exon_rank AS INTEGER)) as exon_count,
                COUNT(*) as splice_site_count
            FROM splice_sites
            WHERE chrom NOT LIKE '%\_%'  -- Standard chromosomes only
            GROUP BY gene_name, transcript_id
            HAVING exon_count >= 10
            ORDER BY exon_count DESC
            LIMIT 50
        """,
        "chart_prompt": """
{context}

Create a scatter plot showing relationship between exon count and splice site count.

DATA PREPARATION (already done):
- Filtered to standard chromosomes only
- Grouped by transcript
- Calculated exon count (max exon_rank) per transcript
- Limited to transcripts with >= 10 exons

VISUALIZATION REQUIREMENTS:
- X-axis: Exon count (max exon_rank)
- Y-axis: Splice site count per transcript
- Scatter plot with alpha for overlapping points
- Color points by exon_count (colormap)
- Add trend line (linear regression)
- Title: "Transcript Complexity: Exon Count vs Splice Site Count"
- Annotate outliers with gene_name

INSIGHTS TO HIGHLIGHT:
- Is there a linear relationship between exon count and splice sites?
- Which transcripts are outliers (more/fewer splice sites than expected)?
- What's the typical ratio of splice sites to exons?

EXPECTED RELATIONSHIP:
- Each exon (except first and last) should have 2 splice sites (donor + acceptor)
- Expected formula: splice_sites ≈ 2 * (exon_count - 1)
""",
    },
    
    "top_genes_heatmap": {
        "title": "Splice Site Patterns in Top Genes",
        "description": "Heatmap of splice site types across genes with most splice sites",
        "data_query": """
            WITH top_genes AS (
                SELECT 
                    gene_name,
                    COUNT(*) as site_count
                FROM splice_sites
                WHERE chrom NOT LIKE '%\_%'  -- Standard chromosomes only
                GROUP BY gene_name
                ORDER BY site_count DESC
                LIMIT 15
            )
            SELECT 
                tg.gene_name,
                d.site_type,
                COUNT(*) as count
            FROM splice_sites d
            INNER JOIN top_genes tg ON d.gene_name = tg.gene_name
            GROUP BY tg.gene_name, d.site_type
        """,
        "chart_prompt": """
{context}

Create a heatmap showing splice site type patterns in top 15 genes.

DATA PREPARATION (already done):
- Filtered to standard chromosomes only
- Selected top 15 genes by total splice site count
- Counted splice sites by type for each gene

VISUALIZATION REQUIREMENTS:
- Heatmap with genes as rows, site types as columns
- Color intensity = count of splice sites
- Use seaborn heatmap with annotations
- Colormap: "YlOrRd" or "Blues"
- Title: "Splice Site Type Distribution in Top Genes (Standard Chromosomes)"
- Annotate cells with counts

CODE STRUCTURE:
- Pivot data: genes x site_types
- Use sns.heatmap(data, annot=True, fmt='d', cmap='YlOrRd')
- Adjust figure size for readability
""",
    },
}


# =========================
# LLM Insight Generation
# =========================

def reflect_on_chart_code_v0(
    code: str,
    chart_type: str,
    domain_context: str,
    data_description: str,
    client: OpenAI,
    model: str = "gpt-4o"
) -> dict[str, Any]:
    """Critique generated chart code and suggest improvements.
    
    This implements the reflection pattern:
    1. Analyze the generated code
    2. Identify issues (biological relevance, clarity, style)
    3. Suggest specific improvements
    
    Args:
        code: Generated chart code to critique
        chart_type: Type of chart (bar, scatter, etc.)
        domain_context: Domain-specific context
        data_description: Description of the data being visualized
        client: OpenAI client
        model: Model for reflection (recommend gpt-4o for better critique)
        
    Returns:
        Dict with critique, issues, and suggested improvements
    """
    reflection_prompt = f"""
{domain_context}

You are an expert in data visualization and genomics. Review this generated chart code and provide constructive critique.

CHART TYPE: {chart_type}
DATA CONTEXT: {data_description}

GENERATED CODE:
```python
{code}
```

Analyze the code for:
1. **Biological Relevance**: Does it highlight meaningful genomic patterns?
2. **Clarity**: Are labels, titles, and legends clear and informative?
3. **Visual Design**: Is it publication-quality? (colors, fonts, layout)
4. **Code Quality**: Is it clean, efficient, and well-structured?
5. **Domain Best Practices**: Does it follow genomics visualization conventions?

Provide your critique as JSON:
{{
    "overall_quality": "excellent|good|fair|poor",
    "strengths": ["strength 1", "strength 2", ...],
    "issues": [
        {{"severity": "critical|major|minor", "issue": "description", "suggestion": "how to fix"}},
        ...
    ],
    "improvements": ["specific improvement 1", "specific improvement 2", ...],
    "needs_refinement": true/false
}}
"""
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert data visualization and genomics consultant."},
            {"role": "user", "content": reflection_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    
    import json
    critique = json.loads(response.choices[0].message.content)
    return critique


def reflect_on_chart_code(
    code: str,
    chart_type: str,
    domain_context: str,
    data_description: str,
    client: OpenAI,
    model: str = "gpt-4o",
) -> dict[str, Any]:
    """Critique generated chart code and suggest improvements.

    This implements the reflection pattern:
    1. Analyze the generated code
    2. Identify issues (biological relevance, clarity, style)
    3. Suggest specific improvements
    
    Now supports both Chat Completions and Responses API models via unified client.
    """

    reflection_prompt = f"""
{domain_context}

You are an expert in data visualization and genomics. Review this generated chart code and provide constructive critique.

CHART TYPE: {chart_type}
DATA CONTEXT: {data_description}

GENERATED CODE:
```python
{code}
```

Analyze the code for:
1. Biological Relevance: Does it highlight meaningful genomic patterns?
2. Clarity: Are labels, titles, and legends clear and informative?
3. Visual Design: Is it publication-quality?
4. Code Quality: Is it clean and well-structured?
5. Domain Best Practices: Does it follow genomics conventions?

Return your critique strictly in JSON:
{{
  "overall_quality": "excellent|good|fair|poor",
  "strengths": [],
  "issues": [
    {{
      "severity": "critical|major|minor",
      "issue": "",
      "suggestion": ""
    }}
  ],
  "improvements": [],
  "needs_refinement": true
}}
""".strip()

    critique = call_llm_json(
        client=client,
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert genomics and visualization consultant. "
                    "You provide concise, actionable feedback in strict JSON format."
                ),
            },
            {"role": "user", "content": reflection_prompt},
        ],
        temperature=0.3,
    )

    return critique


def refine_chart_code(
    original_code: str,
    critique: dict[str, Any],
    chart_prompt: str,
    dataset: Any,
    client: OpenAI,
    model: str = "gpt-4o-mini"
) -> dict[str, Any]:
    """Refine chart code based on critique.
    
    Args:
        original_code: Original generated code
        critique: Critique from reflect_on_chart_code
        chart_prompt: Original chart generation prompt
        dataset: Dataset for context
        client: OpenAI client
        model: Model for refinement
        
    Returns:
        Dict with refined code
    """
    refinement_prompt = f"""
{chart_prompt}

ORIGINAL CODE:
```python
{original_code}
```

CRITIQUE AND IMPROVEMENTS NEEDED:
{chr(10).join(f"- {imp}" for imp in critique.get('improvements', []))}

SPECIFIC ISSUES TO FIX:
{chr(10).join(f"- [{issue['severity']}] {issue['issue']}: {issue['suggestion']}" 
              for issue in critique.get('issues', []))}

Generate IMPROVED chart code that addresses all the issues and implements the suggested improvements.
The code should be complete and executable with 'df' as the DataFrame variable.
"""
    
    from chart_agent.planning import generate_chart_code
    result = generate_chart_code(
        dataset=dataset,
        user_request=refinement_prompt,
        client=client,
        model=model,
        preferred_library="matplotlib"
    )
    
    return result


def generate_analysis_insight(
    dataset: Any,
    analysis_type: str,
    client: OpenAI,
    model: str = "gpt-4o-mini",
    standard_only: bool = False,
    enable_reflection: bool = False,
    reflection_model: str | None = None,
    max_iterations: int = 2
) -> dict[str, Any]:
    """Generate insightful visualization using guided template.
    
    This is the key to leveraging LLMs for domain-specific insights:
    1. Provide domain context
    2. Pre-query data with SQL
    3. Give specific visualization requirements
    4. Let LLM handle implementation details
    5. (Optional) Use reflection to critique and refine
    
    Args:
        dataset: DuckDBDataset instance
        analysis_type: Key from ANALYSIS_TEMPLATES
        client: OpenAI client
        model: Model for code generation
        standard_only: If True, filter to standard chromosomes only
        enable_reflection: If True, use reflection pattern to refine code
        reflection_model: Model for reflection (defaults to same as model)
        max_iterations: Maximum reflection iterations
        
    Returns:
        Dict with query results, chart code, metadata, and optional critique
    """
    if analysis_type not in ANALYSIS_TEMPLATES:
        raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    template = ANALYSIS_TEMPLATES[analysis_type]
    
    # Step 1: Execute data query
    print(f"\n{'='*60}")
    print(f"Analysis: {template['title']}")
    print(f"{'='*60}")
    print(f"Description: {template['description']}")
    
    # Apply standard chromosome filter if requested
    query = template["data_query"]
    if standard_only and "WHERE chrom NOT LIKE '%\\_%'" not in query:
        # Add standard chromosome filter if not already present
        if "WHERE" in query.upper():
            # Insert after existing WHERE clause
            query = query.replace("WHERE", "WHERE chrom NOT LIKE '%\\_%' AND", 1)
        else:
            # Add WHERE clause before GROUP BY or ORDER BY
            if "GROUP BY" in query.upper():
                query = query.replace("GROUP BY", "WHERE chrom NOT LIKE '%\\_%'\n            GROUP BY", 1)
            elif "ORDER BY" in query.upper():
                query = query.replace("ORDER BY", "WHERE chrom NOT LIKE '%\\_%'\n            ORDER BY", 1)
    
    if standard_only:
        print(f"Filter: Standard chromosomes only (chr1-22, chrX, chrY)")
    print(f"\nExecuting SQL query...")
    
    query_result = dataset.query(query)
    print(f"Query returned {len(query_result)} rows")
    
    # Step 2: Create dataset from query result
    from chart_agent.data_access import DataFrameDataset
    query_dataset = DataFrameDataset(query_result, name=analysis_type)
    
    # Step 3: Generate chart with domain context
    print(f"\nGenerating visualization code...")
    chart_prompt = template["chart_prompt"].format(context=SPLICE_SITE_CONTEXT)
    
    from chart_agent.planning import generate_chart_code
    result = generate_chart_code(
        dataset=query_dataset,
        user_request=chart_prompt,
        client=client,
        model=model,
        preferred_library="matplotlib"  # Genomics papers typically use matplotlib
    )
    
    # Step 4: Optional reflection and refinement
    critique_history = []
    final_code = result["code"]
    
    if enable_reflection:
        reflection_model_to_use = reflection_model or model
        print(f"\n{'='*60}")
        print(f"Reflection Pattern Enabled")
        print(f"{'='*60}")
        print(f"Generation model: {model}")
        print(f"Reflection model: {reflection_model_to_use}")
        
        for iteration in range(max_iterations):
            print(f"\n--- Reflection Iteration {iteration + 1}/{max_iterations} ---")
            
            # Critique the code
            data_description = f"{template['title']}: {len(query_result)} rows"
            critique = reflect_on_chart_code(
                code=final_code,
                chart_type=result["chart_type"],
                domain_context=SPLICE_SITE_CONTEXT,
                data_description=data_description,
                client=client,
                model=reflection_model_to_use
            )
            
            critique_history.append(critique)
            
            print(f"Quality: {critique['overall_quality']}")
            print(f"Strengths: {len(critique.get('strengths', []))}")
            print(f"Issues: {len(critique.get('issues', []))}")
            
            # Display issues
            if critique.get('issues'):
                for issue in critique['issues']:
                    print(f"  [{issue['severity']}] {issue['issue']}")
            
            # Check if refinement is needed
            if not critique.get('needs_refinement', False):
                print("✓ Code quality is good, no refinement needed")
                break
            
            # Refine the code
            print("Refining code based on critique...")
            refined_result = refine_chart_code(
                original_code=final_code,
                critique=critique,
                chart_prompt=chart_prompt,
                dataset=query_dataset,
                client=client,
                model=model
            )
            
            final_code = refined_result["code"]
            print(f"✓ Code refined (iteration {iteration + 1})")
    
    return {
        "analysis_type": analysis_type,
        "title": template["title"],
        "description": template["description"],
        "query": template["data_query"],
        "query_result": query_result,
        "chart_code": final_code,
        "chart_type": result["chart_type"],
        "library": result["library"],
        "reflection_enabled": enable_reflection,
        "critique_history": critique_history if enable_reflection else None,
    }


def generate_exploratory_insight(
    dataset: Any,
    research_question: str,
    client: OpenAI,
    model: str = "gpt-4o"
) -> dict[str, Any]:
    """Generate insight for open-ended research question.
    
    This uses a two-step LLM process:
    1. LLM analyzes question and suggests SQL query + chart type
    2. LLM generates visualization code
    
    This is more flexible but requires stronger model (gpt-4o).
    
    Args:
        dataset: DuckDBDataset with SQL capability
        research_question: Open-ended question about the data
        client: OpenAI client
        model: Model for analysis (recommend gpt-4o)
        
    Returns:
        Dict with suggested query, chart code, and reasoning
    """
    schema = dataset.get_schema_description()
    sample = dataset.get_sample_data(rows=3)
    
    # Step 1: LLM suggests analysis approach
    analysis_prompt = f"""
{SPLICE_SITE_CONTEXT}

DATASET SCHEMA:
{schema}

SAMPLE DATA:
{sample}

RESEARCH QUESTION:
{research_question}

Suggest an analysis approach:
1. What SQL query would answer this question?
2. What chart type would best visualize the results?
3. What insights should we highlight?

Respond in JSON format:
{{
    "sql_query": "SELECT ...",
    "chart_type": "bar|line|scatter|heatmap|violin|...",
    "reasoning": "Brief explanation",
    "key_insights": ["insight 1", "insight 2"]
}}
"""
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a genomics data scientist."},
            {"role": "user", "content": analysis_prompt}
        ],
        temperature=0.1,
    )
    
    import json
    analysis = json.loads(response.choices[0].message.content)
    
    # Step 2: Execute suggested query
    print(f"\n{'='*60}")
    print(f"Research Question: {research_question}")
    print(f"{'='*60}")
    print(f"Reasoning: {analysis['reasoning']}")
    print(f"\nExecuting suggested query...")
    
    query_result = dataset.query(analysis["sql_query"])
    print(f"Query returned {len(query_result)} rows")
    
    # Step 3: Generate visualization
    from chart_agent.data_access import DataFrameDataset
    from chart_agent.planning import generate_chart_code
    
    query_dataset = DataFrameDataset(query_result, name="exploratory_analysis")
    
    viz_prompt = f"""
{SPLICE_SITE_CONTEXT}

RESEARCH QUESTION: {research_question}

ANALYSIS APPROACH: {analysis['reasoning']}

KEY INSIGHTS TO HIGHLIGHT:
{chr(10).join(f"- {insight}" for insight in analysis['key_insights'])}

Create a {analysis['chart_type']} chart that addresses this research question.
Use professional genomics visualization style.
"""
    
    result = generate_chart_code(
        dataset=query_dataset,
        user_request=viz_prompt,
        client=client,
        model=model,
        preferred_library="matplotlib"
    )
    
    return {
        "research_question": research_question,
        "sql_query": analysis["sql_query"],
        "reasoning": analysis["reasoning"],
        "key_insights": analysis["key_insights"],
        "query_result": query_result,
        "chart_code": result["code"],
        "chart_type": result["chart_type"],
    }


# =========================
# Main Driver
# =========================

def main():
    parser = argparse.ArgumentParser(
        description="Analyze splice sites with guided LLM-generated visualizations"
    )
    parser.add_argument(
        "--data",
        type=str,
        default="data/splice_sites_enhanced.tsv",
        help="Path to splice sites TSV file"
    )
    parser.add_argument(
        "--analysis",
        type=str,
        choices=list(ANALYSIS_TEMPLATES.keys()) + ["all", "exploratory"],
        default="all",
        help="Analysis type to run"
    )
    parser.add_argument(
        "--question",
        type=str,
        help="Research question for exploratory analysis"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model for code generation (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--reflection-model",
        type=str,
        default=None,
        help="OpenAI model for reflection/critique (default: same as --model). Use gpt-4o for better critique."
    )
    parser.add_argument(
        "--reflect",
        action="store_true",
        help="Enable reflection pattern: generate code, critique it, and refine. Improves quality but costs more."
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=2,
        help="Maximum reflection iterations (default: 2)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output/splice_analysis",
        help="Directory to save generated charts"
    )
    parser.add_argument(
        "--standard-only",
        action="store_true",
        help="Filter to standard chromosomes only (chr1-22, chrX, chrY). Excludes alternative contigs and fix patches."
    )
    
    args = parser.parse_args()
    
    # Smart defaults: If reflection enabled but no reflection model specified, use same as generation model
    if args.reflect and args.reflection_model is None:
        args.reflection_model = args.model
        print(f"\n💡 Smart default: Using {args.model} for both generation and reflection")
        print(f"   (Specify --reflection-model to use a different model for critique)")
    
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("\nError: OPENAI_API_KEY not set")
        print("Please set it in .env file or as environment variable")
        return
    
    client = OpenAI()
    
    print(f"\n{'='*60}")
    print("Splice Site Analysis with Chart Agent")
    print(f"{'='*60}")
    print(f"Data: {args.data}")
    print(f"Generation Model: {args.model}")
    if args.reflect:
        print(f"Reflection: Enabled (model: {args.reflection_model}, max iterations: {args.max_iterations})")
    else:
        print(f"Reflection: Disabled (use --reflect to enable)")
    
    # Load dataset with DuckDB
    from chart_agent.data_access import DuckDBDataset
    
    print(f"\nLoading dataset with DuckDB...")
    # Use all_varchar=True for genomic data to handle mixed chromosome types (1,2,3,X,Y)
    dataset = DuckDBDataset(
        args.data, 
        table_name="splice_sites",
        all_varchar=True  # Prevents type inference errors with chr column
    )
    
    stats = dataset.get_summary_stats()
    print(f"Loaded {stats['row_count']:,} splice sites")
    print(f"Columns: {', '.join(stats['columns'][:5])}...")
    
    if args.standard_only:
        print(f"Mode: Standard chromosomes only (chr1-22, chrX, chrY)")
        print(f"Note: Filtering out {1340:,} sites on alternative contigs/fix patches")
    else:
        print(f"Mode: All chromosomes (including 41 alternative contigs/fix patches)")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run analyses
    if args.analysis == "exploratory":
        if not args.question:
            print("\nError: --question required for exploratory analysis")
            return
        
        result = generate_exploratory_insight(
            dataset=dataset,
            research_question=args.question,
            client=client,
            model=args.model
        )
        
        # Save results
        output_file = output_dir / "exploratory_analysis.py"
        with open(output_file, "w") as f:
            f.write(f"# Research Question: {args.question}\n")
            f.write(f"# Reasoning: {result['reasoning']}\n\n")
            f.write(result["chart_code"])
        
        print(f"\nSaved chart code to: {output_file}")
        print(f"\nKey Insights:")
        for insight in result["key_insights"]:
            print(f"  - {insight}")
    
    elif args.analysis == "all":
        for analysis_type in ANALYSIS_TEMPLATES.keys():
            result = generate_analysis_insight(
                dataset=dataset,
                analysis_type=analysis_type,
                client=client,
                model=args.model,
                standard_only=args.standard_only,
                enable_reflection=args.reflect,
                reflection_model=args.reflection_model,
                max_iterations=args.max_iterations
            )
            
            # Save chart code
            output_file = output_dir / f"{analysis_type}.py"
            with open(output_file, "w") as f:
                f.write(f"# {result['title']}\n")
                f.write(f"# {result['description']}\n")
                if result.get('reflection_enabled'):
                    f.write(f"# Generated with reflection ({len(result.get('critique_history', []))} iterations)\n")
                f.write("\n")
                f.write(result["chart_code"])
            
            print(f"Saved: {output_file}")
            
            # Display critique summary if reflection was used
            if result.get('reflection_enabled') and result.get('critique_history'):
                final_critique = result['critique_history'][-1]
                print(f"  Final quality: {final_critique.get('overall_quality', 'N/A')}")
    
    else:
        result = generate_analysis_insight(
            dataset=dataset,
            analysis_type=args.analysis,
            client=client,
            model=args.model,
            standard_only=args.standard_only,
            enable_reflection=args.reflect,
            reflection_model=args.reflection_model,
            max_iterations=args.max_iterations
        )
        
        output_file = output_dir / f"{args.analysis}.py"
        with open(output_file, "w") as f:
            f.write(f"# {result['title']}\n")
            f.write(f"# {result['description']}\n\n")
            f.write(result["chart_code"])
        
        print(f"\nSaved chart code to: {output_file}")
    
    print(f"\n{'='*60}")
    print("Analysis complete!")
    print(f"{'='*60}")
    print(f"\nGenerated files in: {output_dir}")
    print("\nTo execute the charts:")
    print(f"  python {output_dir}/high_alternative_splicing.py")
    print(f"  python {output_dir}/splice_site_genomic_view.py")
    print(f"  # ... or any other generated .py file")
    
    dataset.close()


if __name__ == "__main__":
    main()
