# Leveraging LLMs for Insightful Domain-Specific Visualizations

## The Challenge

For complex domain-specific datasets (e.g., genomic splice sites with 50+ columns), asking LLMs to "plot something interesting" is too vague and often produces generic or irrelevant visualizations.

**Problem:**
- Too many variables → LLM overwhelmed
- Domain knowledge required → Generic LLM lacks context
- Open-ended prompts → Unpredictable results

## The Solution: Guided Insight Generation

We use a **three-tier strategy** to leverage LLMs effectively:

### Tier 1: Template-Based Analysis (Recommended)
**Best for:** Known analysis patterns, production use

**Strategy:**
1. Domain experts create analysis templates
2. Templates include:
   - SQL query for data preparation
   - Domain context for LLM
   - Specific visualization requirements
   - Expected insights to highlight
3. LLM generates implementation code

**Example:** `analyze_splice_sites.py`

```python
ANALYSIS_TEMPLATES = {
    "high_alternative_splicing": {
        "data_query": "SELECT gene, COUNT(isoforms) ...",
        "chart_prompt": """
            {domain_context}
            
            Create horizontal bar chart showing top 20 genes...
            Highlight: Which genes have most complex splicing?
        """
    }
}
```

**Advantages:**
- ✅ Predictable, reproducible results
- ✅ Domain knowledge embedded in templates
- ✅ Works with smaller models (gpt-4o-mini)
- ✅ Fast execution
- ✅ Easy to review and validate

**Disadvantages:**
- ❌ Requires upfront template creation
- ❌ Less flexible for novel questions

---

### Tier 2: Two-Step Exploratory Analysis
**Best for:** Research questions, novel insights

**Strategy:**
1. **Step 1:** LLM analyzes question and suggests:
   - SQL query to answer it
   - Appropriate chart type
   - Key insights to highlight
2. **Step 2:** LLM generates visualization code

**Example:**

```python
# User asks: "Which genes show tissue-specific splicing patterns?"

# Step 1: LLM suggests
{
    "sql_query": "SELECT gene, tissue, COUNT(DISTINCT isoform) ...",
    "chart_type": "heatmap",
    "reasoning": "Heatmap shows gene x tissue patterns clearly",
    "key_insights": ["Identify tissue-specific genes", "Find ubiquitous vs specific"]
}

# Step 2: Execute query and generate chart
```

**Advantages:**
- ✅ Handles novel questions
- ✅ LLM applies domain reasoning
- ✅ Flexible and adaptive
- ✅ Generates new analysis patterns

**Disadvantages:**
- ❌ Requires stronger model (gpt-4o)
- ❌ Slower (two LLM calls)
- ❌ Less predictable
- ❌ May need validation

---

### Tier 3: Reflection-Enhanced Generation
**Best for:** High-stakes analysis, publication-quality charts

**Strategy:**
1. Generate initial chart (Tier 1 or 2)
2. LLM critiques the chart:
   - Scientific accuracy
   - Visual clarity
   - Domain best practices
3. LLM generates improved version
4. Iterate until quality threshold met

**Example:**

```python
# Initial chart
result = generate_chart(dataset, prompt)

# Reflection
critique = reflect_on_chart(result, domain_criteria={
    "biological_accuracy": "Does it represent biology correctly?",
    "statistical_rigor": "Are error bars/confidence shown?",
    "publication_quality": "Meets journal standards?"
})

# Refinement
improved = refine_chart(result, critique)
```

**Advantages:**
- ✅ Highest quality output
- ✅ Catches errors and issues
- ✅ Publication-ready
- ✅ Enforces domain standards

**Disadvantages:**
- ❌ Slowest (multiple iterations)
- ❌ Most expensive (multiple LLM calls)
- ❌ Requires quality criteria definition

---

## Key Principles for Domain-Specific Insights

### 1. Provide Rich Domain Context

**Bad:**
```python
"Plot the splice site data"
```

**Good:**
```python
"""
DOMAIN CONTEXT: Genomic Splice Sites
- Alternative splicing creates protein diversity
- Donor (5') and acceptor (3') sites
- Confidence scores indicate prediction quality

Create a visualization showing genes with highest
alternative splicing activity (multiple isoforms).
Use genomics visualization best practices.
"""
```

### 2. Separate Data Preparation from Visualization

**Bad:**
```python
# LLM must figure out complex SQL + plotting
"Show genes with high splicing, filtered by confidence > 0.7"
```

**Good:**
```python
# Pre-query data with SQL
df = dataset.query("""
    SELECT gene, COUNT(isoforms) as count
    FROM data WHERE confidence > 0.7
    GROUP BY gene HAVING count > 5
""")

# LLM focuses on visualization
"Create bar chart from this pre-aggregated data"
```

### 3. Specify Visualization Requirements

**Vague:**
```python
"Make a chart"
```

**Specific:**
```python
"""
- Chart type: Horizontal bar chart
- X-axis: Isoform count
- Y-axis: Gene symbols (sorted)
- Color: By confidence score (colormap)
- Style: Professional genomics paper
- Include: Title, legend, grid
"""
```

### 4. Guide Expected Insights

**Generic:**
```python
"Plot the data"
```

**Insightful:**
```python
"""
Highlight these insights:
- Which genes have most complex splicing?
- Is there correlation between isoform count and confidence?
- Are certain gene families over-represented?
"""
```

### 5. Use SQL for Complex Aggregations

**Inefficient:**
```python
# Let LLM write pandas aggregation code
"Group by gene and count isoforms"
```

**Efficient:**
```python
# Use DuckDB for fast aggregation
df = dataset.query("""
    SELECT gene, COUNT(DISTINCT isoform) as count
    FROM data GROUP BY gene
""")
```

---

## Practical Workflow

### For Known Analysis Patterns:

```python
# 1. Create template (once)
template = {
    "data_query": "SELECT ...",
    "chart_prompt": "{context}\n\nCreate visualization..."
}

# 2. Execute query
df = dataset.query(template["data_query"])

# 3. Generate chart
result = generate_chart_code(df, template["chart_prompt"])

# 4. Execute and save
exec(result["code"])
plt.savefig("output.png")
```

### For Research Questions:

```python
# 1. Ask LLM for analysis approach
analysis = llm_suggest_analysis(
    dataset_schema,
    research_question="Which genes show tissue-specific splicing?"
)

# 2. Execute suggested query
df = dataset.query(analysis["sql_query"])

# 3. Generate visualization
result = generate_chart_code(
    df,
    prompt=f"{domain_context}\n{analysis['reasoning']}\n..."
)

# 4. Optional: Reflect and refine
if needs_improvement:
    result = reflect_and_refine(result)
```

---

## Examples from `analyze_splice_sites.py`

### Template-Based: High Alternative Splicing

```python
# Pre-defined analysis
result = generate_analysis_insight(
    dataset,
    analysis_type="high_alternative_splicing",
    client=client
)

# Produces: Bar chart of top 20 genes by isoform count
# Colored by confidence, with domain-appropriate styling
```

### Exploratory: Custom Question

```python
# Novel research question
result = generate_exploratory_insight(
    dataset,
    research_question="Do splice sites cluster near exon boundaries?",
    client=client
)

# LLM suggests:
# 1. Query: Calculate distance to nearest exon
# 2. Chart: Histogram of distances
# 3. Insight: Look for clustering patterns
```

### Genomic Position View (SpliceAI Style)

```python
# Domain-specific visualization
result = generate_analysis_insight(
    dataset,
    analysis_type="splice_site_genomic_view",
    client=client
)

# Produces: Vertical bars at genomic positions
# Height = confidence, color = splice type
# Professional genomics paper style
```

---

## Best Practices Summary

### DO:
✅ Provide domain context in prompts  
✅ Use SQL for data preparation  
✅ Specify chart requirements explicitly  
✅ Guide expected insights  
✅ Use templates for known patterns  
✅ Use two-step for novel questions  
✅ Add reflection for high-stakes work  

### DON'T:
❌ Ask vague "plot something" prompts  
❌ Overload LLM with raw data  
❌ Expect LLM to infer domain knowledge  
❌ Skip data preparation step  
❌ Use weak models for complex analysis  
❌ Ignore domain visualization standards  

---

## Extending to Other Domains

This strategy works for any complex domain:

### Proteomics:
```python
templates = {
    "protein_abundance": "Show top expressed proteins by tissue",
    "ptm_sites": "Visualize post-translational modification sites",
    "interaction_network": "Network graph of protein interactions"
}
```

### Financial Data:
```python
templates = {
    "portfolio_performance": "Compare returns across asset classes",
    "risk_analysis": "VaR and CVaR distributions",
    "correlation_matrix": "Asset correlation heatmap"
}
```

### Clinical Data:
```python
templates = {
    "patient_outcomes": "Survival curves by treatment group",
    "biomarker_distribution": "Biomarker levels across cohorts",
    "adverse_events": "Frequency and severity of AEs"
}
```

---

## Conclusion

**Key Insight:** LLMs excel at **implementation** when given clear requirements, but struggle with **open-ended discovery** in complex domains.

**Winning Strategy:**
1. **Human expertise** → Define meaningful questions and analysis patterns
2. **SQL/DuckDB** → Prepare data efficiently
3. **LLM** → Generate visualization code with domain context
4. **Reflection** → Refine for quality (optional)

This approach combines human domain knowledge with LLM coding capabilities for maximum insight generation.
