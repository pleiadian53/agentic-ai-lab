"""
Test client for Chart Agent API

Demonstrates the complete workflow:
1. Generate chart code
2. Critique the code
3. Execute to produce plot
4. Generate insights
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8003"


def test_health():
    """Test health endpoint"""
    print("="*60)
    print("Testing Health Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()


def test_list_datasets():
    """Test dataset listing"""
    print("="*60)
    print("Listing Available Datasets")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/datasets")
    data = response.json()
    
    print(f"Total datasets: {data['total']}")
    print(f"Cached: {data['cached']}")
    print("\nDatasets:")
    for ds in data['datasets']:
        print(f"  - {ds['name']} ({ds['size_mb']:.2f} MB)")
    print()


def test_analyze(dataset_path: str, question: str, model: str = "gpt-4o-mini"):
    """Test code generation"""
    print("="*60)
    print("Generating Chart Code")
    print("="*60)
    print(f"Dataset: {dataset_path}")
    print(f"Question: {question}")
    print(f"Model: {model}")
    print()
    
    response = requests.post(f"{BASE_URL}/analyze", json={
        "dataset_path": dataset_path,
        "question": question,
        "context": "Focus on standard chromosomes. Use publication-ready styling.",
        "model": model
    })
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
    plan = response.json()
    
    print(f"✓ Code generated ({len(plan['code'])} chars)")
    print(f"Libraries: {', '.join(plan['libraries_used'])}")
    print(f"\nExplanation:\n{plan['explanation']}")
    print(f"\nCode preview (first 500 chars):\n{plan['code'][:500]}...")
    print()
    
    return plan


def test_critique(code: str, model: str = "gpt-4o-mini"):
    """Test code critique"""
    print("="*60)
    print("Critiquing Code")
    print("="*60)
    print(f"Model: {model}")
    print()
    
    response = requests.post(f"{BASE_URL}/critique", json={
        "code": code,
        "domain_context": "Genomic splice site analysis. Dataset: MANE splice sites (GRCh38).",
        "model": model
    })
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
    critique = response.json()
    
    print(f"Quality: {critique['quality']}")
    print(f"Strengths: {len(critique['strengths'])}")
    for strength in critique['strengths']:
        print(f"  ✓ {strength}")
    
    print(f"\nIssues: {len(critique['issues'])}")
    for issue in critique['issues']:
        print(f"  [{issue['severity']}] {issue['issue']}")
        if 'suggestion' in issue:
            print(f"      → {issue['suggestion']}")
    
    print(f"\nNeeds refinement: {critique['needs_refinement']}")
    print()
    
    return critique


def test_execute(code: str, dataset_path: str, output_format: str = "pdf"):
    """Test code execution"""
    print("="*60)
    print("Executing Code")
    print("="*60)
    print(f"Output format: {output_format}")
    print()
    
    response = requests.post(f"{BASE_URL}/execute", json={
        "code": code,
        "dataset_path": dataset_path,
        "output_format": output_format
    })
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
    result = response.json()
    
    if result['success']:
        print(f"✓ Execution successful")
        print(f"Image path: {result['image_path']}")
        print(f"Full URL: {BASE_URL}{result['image_path']}")
    else:
        print(f"✗ Execution failed")
        print(f"Error: {result['error']}")
    
    print(f"\nLogs:\n{result['logs']}")
    print()
    
    return result


def test_insight(analysis_title: str, image_path: str, model: str = "gpt-5.1-codex-mini"):
    """Test insight generation"""
    print("="*60)
    print("Generating Insights")
    print("="*60)
    print(f"Title: {analysis_title}")
    print(f"Model: {model}")
    print()
    
    response = requests.post(f"{BASE_URL}/insight", json={
        "analysis_title": analysis_title,
        "image_path": image_path,
        "dataset_context": "MANE splice sites (369,918 sites from 18,200 genes, GRCh38)",
        "model": model
    })
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
    insight = response.json()
    
    print(f"Caption:\n{insight['caption']}")
    print(f"\nKey Insights:")
    for i, insight_text in enumerate(insight['key_insights'], 1):
        print(f"  {i}. {insight_text}")
    print()
    
    return insight


def main():
    """Run complete workflow"""
    print("\n" + "="*60)
    print("Chart Agent API Test Client")
    print("="*60 + "\n")
    
    # Check health
    test_health()
    
    # List datasets
    test_list_datasets()
    
    # Test workflow
    dataset_path = "data/splice_sites_enhanced.tsv"
    question = "Show the top 20 genes with the most splice sites, colored by exon complexity"
    
    # Step 1: Generate code
    plan = test_analyze(dataset_path, question, model="gpt-4o-mini")
    if not plan:
        print("Failed to generate code. Exiting.")
        return
    
    # Step 2: Critique (optional)
    critique = test_critique(plan['code'], model="gpt-4o-mini")
    
    # Step 3: Execute
    result = test_execute(plan['code'], dataset_path, output_format="pdf")
    if not result or not result['success']:
        print("Failed to execute code. Exiting.")
        return
    
    # Step 4: Generate insights
    insight = test_insight(
        analysis_title="Genes with Most Splice Sites",
        image_path=result['image_path'],
        model="gpt-4o-mini"  # Using gpt-4o-mini for faster testing
    )
    
    print("="*60)
    print("Workflow Complete!")
    print("="*60)
    print(f"✓ Code generated")
    print(f"✓ Code critiqued (quality: {critique['quality'] if critique else 'N/A'})")
    print(f"✓ Chart created: {BASE_URL}{result['image_path']}")
    print(f"✓ Insights generated")
    print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        if test_name == "health":
            test_health()
        elif test_name == "datasets":
            test_list_datasets()
        elif test_name == "analyze":
            dataset = sys.argv[2] if len(sys.argv) > 2 else "data/splice_sites_enhanced.tsv"
            question = sys.argv[3] if len(sys.argv) > 3 else "Show splice site distribution"
            test_analyze(dataset, question)
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: health, datasets, analyze")
    else:
        # Run full workflow
        main()
