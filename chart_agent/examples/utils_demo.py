"""Demo script for chart_agent utility functions.

This script demonstrates how to use the utility functions for:
- Listing and selecting models
- Displaying results
- Executing generated code
- Validating code quality

Run in Jupyter notebook for best experience with HTML displays.
"""

import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load from .env in current directory or parent directories
except ImportError:
    # dotenv not installed, environment variables must be set manually
    pass

from openai import OpenAI
from chart_agent import (
    display_models_table,
    models_response_to_dataframe,
    save_models_list,
    load_models_list,
    get_recommended_models,
    print_html,
    display_chart_result,
    display_analysis_summary,
    execute_chart_code,
    save_code_to_file,
    validate_chart_code,
    DuckDBDataset,
    generate_chart_code,
)
import pandas as pd


def demo_model_listing():
    """Demonstrate model listing and selection."""
    print("\n" + "="*60)
    print("Demo 1: Model Listing and Selection")
    print("="*60)
    
    client = OpenAI()
    
    # Display all models in a formatted table
    print("\n1. Display all available models:")
    display_models_table(client.models.list())
    
    # Get models as DataFrame for filtering
    print("\n2. Filter models to GPT-4 family:")
    df = models_response_to_dataframe(client.models.list())
    gpt4_models = df[df['id'].str.contains('gpt-4', case=False)]
    print_html(gpt4_models, title="GPT-4 Models")
    
    # Get recommended models by use case
    print("\n3. Get recommended models by use case:")
    recommendations = get_recommended_models(client.models.list())
    for use_case, models in recommendations.items():
        print(f"\n{use_case.replace('_', ' ').title()}:")
        for model in models:
            print(f"  - {model}")
    
    print("\n💡 Tip: Use the latest GPT models for best chart generation quality!")
    print("   Mini models are faster and cheaper but may produce simpler code.")
    
    # Save models list to file
    print("\n4. Save models list to file:")
    filepath = save_models_list(
        client.models.list(),
        output_dir="data/llm",
        filename="available_models.json"
    )
    print(f"   Saved to: {filepath}")
    
    # Load and display
    print("\n5. Load saved models list:")
    saved_data = load_models_list(str(filepath))
    print(f"   Timestamp: {saved_data['timestamp']}")
    print(f"   Total models: {saved_data['total_models']}")
    print(f"   Recommendations included: {len(saved_data['recommendations'])} categories")


def demo_chart_generation():
    """Demonstrate chart generation with result display."""
    print("\n" + "="*60)
    print("Demo 2: Chart Generation with Result Display")
    print("="*60)
    
    # Create sample data
    data = pd.DataFrame({
        'category': ['A', 'B', 'C', 'D', 'E'],
        'value': [23, 45, 12, 67, 34],
        'score': [0.8, 0.6, 0.9, 0.7, 0.85]
    })
    
    print("\n1. Sample data:")
    print_html(data, title="Sample Dataset")
    
    # Generate chart code
    print("\n2. Generating chart code...")
    from chart_agent.data_access import DataFrameDataset
    dataset = DataFrameDataset(data, name="sample")
    
    client = OpenAI()
    result = generate_chart_code(
        dataset=dataset,
        user_request="Create a bar chart showing value by category, colored by score",
        client=client,
        model="gpt-4o-mini",
        preferred_library="matplotlib"
    )
    
    # Display result with metadata
    print("\n3. Display generated result:")
    display_chart_result(
        result,
        show_code=True,
        show_metadata=True,
        execute=False  # Set to True to execute
    )
    
    # Validate the code
    print("\n4. Validate generated code:")
    validation = validate_chart_code(result['code'])
    validation_df = pd.DataFrame([validation])
    print_html(validation_df, title="Code Validation Results")
    
    if validation['warnings']:
        print("\nWarnings:")
        for warning in validation['warnings']:
            print(f"  ⚠️  {warning}")
    
    # Save code to file
    print("\n5. Save code to file:")
    filepath = save_code_to_file(
        result['code'],
        "demo_chart",
        output_dir="output/demo",
        metadata={
            "analysis": "demo",
            "model": "gpt-4o-mini",
            "chart_type": result['chart_type']
        }
    )
    print(f"   Saved to: {filepath}")


def demo_splice_site_analysis():
    """Demonstrate analysis with splice site data."""
    print("\n" + "="*60)
    print("Demo 3: Splice Site Analysis with Utilities")
    print("="*60)
    
    # Load data
    print("\n1. Loading splice site data...")
    dataset = DuckDBDataset(
        "data/splice_sites_enhanced.tsv",
        table_name="splice_sites",
        all_varchar=True
    )
    
    # Run a query
    print("\n2. Running analysis query...")
    query = """
        SELECT 
            gene_name,
            COUNT(*) as splice_site_count,
            MAX(CAST(exon_rank AS INTEGER)) as max_exon_rank
        FROM splice_sites
        WHERE chrom NOT LIKE '%\\_%'
        GROUP BY gene_name
        HAVING splice_site_count > 50
        ORDER BY splice_site_count DESC
        LIMIT 10
    """
    
    result = dataset.query(query)
    
    # Display analysis summary
    print("\n3. Display analysis summary:")
    display_analysis_summary(
        "top_genes_by_splice_sites",
        result,
        show_sample=True,
        sample_rows=10
    )
    
    # Generate visualization
    print("\n4. Generate visualization...")
    from chart_agent.data_access import DataFrameDataset
    query_dataset = DataFrameDataset(result, name="top_genes")
    
    client = OpenAI()
    chart_result = generate_chart_code(
        dataset=query_dataset,
        user_request="Create a horizontal bar chart of genes by splice site count, colored by max exon rank",
        client=client,
        model="gpt-4o-mini"
    )
    
    # Display and execute
    print("\n5. Display generated chart code:")
    display_chart_result(chart_result, show_code=True, show_metadata=True)
    
    # Execute the code
    print("\n6. Execute chart code:")
    exec_result = execute_chart_code(
        chart_result['code'],
        result,
        save_path="output/demo/top_genes_chart.png",
        show_plot=False  # Set to True in notebook
    )
    
    if exec_result['success']:
        print(f"   ✓ Chart saved to: {exec_result['plot_path']}")
        print_html(exec_result['plot_path'], title="Generated Chart", is_image=True)
    else:
        print(f"   ✗ Execution failed: {exec_result['error']}")
    
    dataset.close()


def demo_model_comparison():
    """Compare different models for chart generation."""
    print("\n" + "="*60)
    print("Demo 4: Model Comparison for Chart Generation")
    print("="*60)
    
    # Sample data
    data = pd.DataFrame({
        'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'sales': [100, 120, 95, 140, 130],
        'target': [110, 110, 110, 110, 110]
    })
    
    from chart_agent.data_access import DataFrameDataset
    dataset = DataFrameDataset(data, name="sales")
    
    client = OpenAI()
    
    # Test different models
    models_to_test = ["gpt-4o-mini", "gpt-4o"]  # Add more if available
    
    print("\n1. Testing models:")
    results = {}
    
    for model in models_to_test:
        print(f"\n   Testing {model}...")
        try:
            result = generate_chart_code(
                dataset=dataset,
                user_request="Create a line chart comparing sales vs target by month",
                client=client,
                model=model,
                preferred_library="matplotlib"
            )
            results[model] = result
            print(f"   ✓ {model}: Generated {len(result['code'])} characters of code")
        except Exception as e:
            print(f"   ✗ {model}: Failed - {e}")
    
    # Compare results
    print("\n2. Comparison:")
    comparison_data = []
    for model, result in results.items():
        validation = validate_chart_code(result['code'])
        comparison_data.append({
            'Model': model,
            'Code Length': len(result['code']),
            'Lines': validation['line_count'],
            'Chart Type': result.get('chart_type', 'N/A'),
            'Valid': '✓' if validation['valid'] else '✗',
            'Warnings': len(validation['warnings'])
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    print_html(comparison_df, title="Model Comparison Results")
    
    print("\n💡 Insights:")
    print("   - gpt-4o typically generates more sophisticated visualizations")
    print("   - gpt-4o-mini is faster and cheaper, good for prototyping")
    print("   - Both models can produce valid, executable code")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("Chart Agent Utility Functions Demo")
    print("="*70)
    print("\nThis demo showcases the utility functions available in chart_agent.")
    print("For best experience, run in a Jupyter notebook for HTML displays.")
    
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n❌ Error: OPENAI_API_KEY not found!")
        print("\nPlease set your OpenAI API key:")
        print("  1. Create a .env file with: OPENAI_API_KEY=your-key-here")
        print("  2. Or export it: export OPENAI_API_KEY='your-key-here'")
        print("\nThe .env file should be in the current directory or a parent directory.")
        return
    
    try:
        # Demo 1: Model listing
        demo_model_listing()
        
        # Demo 2: Chart generation with display
        demo_chart_generation()
        
        # Demo 3: Splice site analysis (requires data file)
        try:
            demo_splice_site_analysis()
        except Exception as e:
            print(f"\n⚠️  Skipping Demo 3 (splice site data not available): {e}")
        
        # Demo 4: Model comparison
        demo_model_comparison()
        
        print("\n" + "="*70)
        print("Demo Complete!")
        print("="*70)
        print("\n📚 See chart_agent/utils.py for full API documentation")
        print("💡 Use these utilities in your own notebooks and scripts")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
