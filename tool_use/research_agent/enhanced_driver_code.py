"""
Enhanced Driver Code for Research Agent Notebook

This is the enhanced version that uses notebook_helpers and inspect_utils
for a more streamlined and feature-rich workflow.

Copy this into a new notebook cell to use it.
"""

# ============================================================================
# OPTION 1: Quick Research - All-in-One Workflow
# ============================================================================
"""
from notebook_helpers import quick_research, save_research_results

# Complete workflow in one call
topic = "Radio observations of recurrent novae"
results = quick_research(topic, parallel=True, show_html=True)

# Save all outputs (including PDF)
save_research_results(results, "recurrent_novae_2024")
"""

# ============================================================================
# OPTION 2: Step-by-Step with Enhanced Visualization
# ============================================================================
"""
from notebook_helpers import open_html_in_browser, save_research_results
import inspect_utils

# Step 1: Research with tools (with parallel execution)
topic = "Radio observations of recurrent novae"
print(f"🔬 Researching: {topic}\n")

preliminary_report = generate_research_report_with_tools(
    topic,
    # Note: If you updated generate_research_report_with_tools to support parallel,
    # you can pass parallel=True here
)

# Display preliminary report nicely
inspect_utils.display_research_report(
    preliminary_report, 
    title="Preliminary Research Report"
)

# Step 2: Reflection and rewrite
print("\n" + "="*80)
print("REFLECTION & REVISION")
print("="*80)

reflection_result = reflection_and_rewrite(preliminary_report)

# Inspect reflection with rich formatting
inspect_utils.inspect_reflection_output(reflection_result, max_length=1000)

# Compare original vs revised
inspect_utils.compare_reports(preliminary_report, reflection_result)

# Step 3: Convert to HTML
print("\n" + "="*80)
print("HTML CONVERSION")
print("="*80)

html = convert_report_to_html(reflection_result["revised_report"])
print("✅ HTML generated")

# Display HTML in notebook
display(HTML(html))

# Step 4: Save all outputs (including PDF)
results = {
    "preliminary_report": preliminary_report,
    "reflection": reflection_result["reflection"],
    "revised_report": reflection_result["revised_report"],
    "html": html
}

save_research_results(results, "recurrent_novae_2024", generate_pdf=True)

# Optional: Open HTML in browser
# open_html_in_browser("research_outputs/recurrent_novae_2024_report.html")
"""

# ============================================================================
# OPTION 3: Comparison Mode - Side-by-Side Analysis
# ============================================================================
"""
from notebook_helpers import research_and_compare

# Research with automatic comparison view
topic = "Radio observations of recurrent novae"
results = research_and_compare(topic, parallel=True)

# The function automatically displays:
# - Comparison statistics
# - Preliminary report
# - Revised report
"""

# ============================================================================
# OPTION 4: Custom Workflow with Full Control
# ============================================================================
"""
import inspect_utils
from notebook_helpers import save_research_results

# Step 1: Generate report
topic = "Radio observations of recurrent novae"
report = generate_research_report_with_tools(topic)

# Step 2: Multiple reflection passes (iterative improvement)
print("🔄 Pass 1: Initial reflection")
result1 = reflection_and_rewrite(report)
inspect_utils.inspect_reflection_simple(result1)

print("\n🔄 Pass 2: Second reflection")
result2 = reflection_and_rewrite(result1["revised_report"])
inspect_utils.inspect_reflection_simple(result2)

# Step 3: Convert final version to HTML
html = convert_report_to_html(result2["revised_report"])

# Step 4: Save everything
results = {
    "preliminary_report": report,
    "reflection": result2["reflection"],
    "revised_report": result2["revised_report"],
    "html": html
}

save_research_results(results, "recurrent_novae_iterative", generate_pdf=True)

# Display final report
inspect_utils.display_research_report(
    result2["revised_report"],
    title="Final Report (After 2 Reflection Passes)"
)
"""

# ============================================================================
# OPTION 5: Batch Processing Multiple Topics
# ============================================================================
"""
from notebook_helpers import quick_research, save_research_results
from datetime import datetime

topics = [
    "Radio observations of recurrent novae",
    "CRISPR gene editing applications",
    "Quantum computing error correction"
]

for i, topic in enumerate(topics, 1):
    print(f"\n{'='*80}")
    print(f"Processing {i}/{len(topics)}: {topic}")
    print(f"{'='*80}\n")
    
    try:
        # Generate report
        results = quick_research(topic, parallel=True, show_html=False)
        
        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{topic.replace(' ', '_')[:30]}"
        save_research_results(results, filename)
        
        print(f"✅ Completed: {topic}\n")
    
    except Exception as e:
        print(f"❌ Error processing '{topic}': {str(e)}\n")
        continue

print("\n" + "="*80)
print(f"✅ Batch processing complete! Processed {len(topics)} topics")
print("="*80)
"""
