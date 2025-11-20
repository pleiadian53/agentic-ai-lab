#!/usr/bin/env python
"""
Test the HTTP endpoint directly with requests.
"""

import requests
import json

def test_http_analyze():
    """Test the /analyze endpoint via HTTP"""
    
    url = "http://localhost:8003/analyze"
    
    payload = {
        "dataset_path": "data/splice_sites_enhanced.tsv",
        "question": "Show the top 20 genes with the most splice sites",
        "context": "Focus on standard chromosomes only. Use publication-ready styling with clear labels.",
        "model": "gpt-5.1-codex-mini"
    }
    
    print("=" * 60)
    print("Testing HTTP POST /analyze")
    print("=" * 60)
    print(f"\nURL: {url}")
    print(f"\nPayload:")
    print(json.dumps(payload, indent=2))
    
    print("\nSending request...")
    
    try:
        response = requests.post(url, json=payload)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\n✓ SUCCESS!")
            data = response.json()
            print(f"\nResponse keys: {list(data.keys())}")
            print(f"\nCode length: {len(data.get('code', ''))} chars")
            print(f"Explanation: {data.get('explanation', '')}")
            print(f"Libraries: {data.get('libraries_used', [])}")
            
            print("\nCode preview (first 300 chars):")
            print("-" * 60)
            print(data.get('code', '')[:300])
            print("-" * 60)
            
        else:
            print(f"\n✗ ERROR {response.status_code}")
            print(f"\nResponse body:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"\n✗ Request failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = test_http_analyze()
    sys.exit(0 if success else 1)
