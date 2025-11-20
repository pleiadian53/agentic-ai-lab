#!/usr/bin/env python
"""
Test the full Chart Agent workflow: analyze -> execute -> view
"""

import requests
import json
import webbrowser
from pathlib import Path

BASE_URL = "http://localhost:8003"

def test_full_workflow():
    """Test the complete workflow"""
    
    print("=" * 70)
    print("Chart Agent API - Full Workflow Test")
    print("=" * 70)
    
    # Step 1: Generate code
    print("\n📝 Step 1: Generating chart code...")
    analyze_request = {
        "dataset_path": "data/splice_sites_enhanced.tsv",
        "question": "Show the top 20 genes with the most splice sites",
        "context": "Focus on standard chromosomes only. Use publication-ready styling.",
        "model": "gpt-4o-mini"
    }
    
    response = requests.post(f"{BASE_URL}/analyze", json=analyze_request)
    
    if response.status_code != 200:
        print(f"❌ Analysis failed: {response.status_code}")
        print(response.text)
        return False
    
    plan = response.json()
    print(f"✅ Code generated!")
    print(f"   - Length: {len(plan['code'])} characters")
    print(f"   - Explanation: {plan['explanation']}")
    print(f"   - Libraries: {', '.join(plan['libraries_used'])}")
    
    # Step 2: Execute code
    print("\n🎨 Step 2: Executing code to generate plot...")
    execute_request = {
        "code": plan['code'],
        "dataset_path": "data/splice_sites_enhanced.tsv",
        "output_format": "pdf"
    }
    
    response = requests.post(f"{BASE_URL}/execute", json=execute_request)
    
    if response.status_code != 200:
        print(f"❌ Execution failed: {response.status_code}")
        print(response.text)
        return False
    
    result = response.json()
    print(f"✅ Plot generated!")
    print(f"   - Success: {result['success']}")
    print(f"   - Image path: {result.get('image_path', 'N/A')}")
    
    if not result['success']:
        print(f"❌ Execution failed: {result.get('error', 'Unknown error')}")
        print(f"Logs:\n{result.get('logs', '')}")
        return False
    
    # Step 3: Download the plot
    print("\n📥 Step 3: Accessing generated plot...")
    # The image_path is relative, need to construct URL
    image_filename = Path(result['image_path']).name
    plot_url = f"{BASE_URL}/charts/{image_filename}"
    
    response = requests.get(plot_url)
    if response.status_code == 200:
        # Save locally
        output_file = Path("test_output.pdf")
        output_file.write_bytes(response.content)
        print(f"✅ Plot saved to: {output_file.absolute()}")
        
        # Try to open it
        try:
            import subprocess
            subprocess.run(["open", str(output_file)])
            print(f"✅ Opened plot in default viewer")
        except:
            print(f"ℹ️  Open manually: {output_file.absolute()}")
    else:
        print(f"❌ Download failed: {response.status_code}")
        return False
    
    # Step 4: Generate insight
    print("\n💡 Step 4: Generating insight/caption...")
    insight_request = {
        "analysis_title": "Top 20 Genes by Splice Site Count",
        "chart_description": plan['explanation'],
        "data_summary": "Analysis of splice sites across genes in standard chromosomes",
        "model": "gpt-4o-mini"
    }
    
    response = requests.post(f"{BASE_URL}/insight", json=insight_request)
    
    if response.status_code == 200:
        insight = response.json()
        print(f"✅ Insight generated!")
        print(f"\n📊 Chart Caption:")
        print(f"   {insight['caption']}")
        print(f"\n🔍 Key Findings:")
        for finding in insight['key_findings']:
            print(f"   • {finding}")
    else:
        print(f"⚠️  Insight generation skipped (optional)")
    
    print("\n" + "=" * 70)
    print("✅ WORKFLOW COMPLETE!")
    print("=" * 70)
    print(f"\nGenerated plot: {output_file.absolute()}")
    print(f"View in browser: {plot_url}")
    
    return True


if __name__ == "__main__":
    import sys
    success = test_full_workflow()
    sys.exit(0 if success else 1)
