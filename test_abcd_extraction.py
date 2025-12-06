#!/usr/bin/env python3
"""
Test script for ABCD dataset extraction with Extractify backend
"""
import json
import requests
import sys
import time

BACKEND_URL = "http://localhost:8000"

def test_abcd_extraction(file_path, num_conversations=None):
    """Test the ABCD dataset extraction"""
    
    print(f"\n📚 Testing ABCD Dataset Extraction")
    print(f"{'=' * 50}")
    print(f"File: {file_path}")
    
    try:
        # Load the JSON file
        print(f"Loading dataset...")
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Get conversations
        conversations = data.get('train', data if isinstance(data, list) else [])
        if num_conversations:
            conversations = conversations[:num_conversations]
        
        print(f"✓ Loaded {len(conversations)} conversations")
        
        # Prepare request
        print(f"Sending to backend for extraction...")
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/extract-bulk",
            json={
                "text": json.dumps({"train": conversations}),
                "fileName": file_path.split('/')[-1]
            },
            timeout=300  # 5 minute timeout
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            results = response.json()
            print(f"✓ Extraction completed in {elapsed:.1f}s")
            print(f"\nResults Summary:")
            print(f"  Total conversations: {results.get('total', 0)}")
            print(f"  Format detected: {results.get('format', 'unknown')}")
            print(f"  Dataset: {results.get('dataset', 'N/A')}")
            
            # Show sample results
            conversations_results = results.get('conversations', [])
            if conversations_results:
                print(f"\n📊 Sample Extractions (First 3):")
                for i, res in enumerate(conversations_results[:3], 1):
                    print(f"\n  Conversation {i}:")
                    print(f"    Email: {res.get('email', 'NA')}")
                    print(f"    Phone: {res.get('phone', 'NA')}")
                    print(f"    ZIP Code: {res.get('zipCode', 'NA')}")
                    print(f"    Order ID: {res.get('orderId', 'NA')}")
                    
                    metadata = res.get('metadata', {})
                    if 'conversation_id' in metadata:
                        print(f"    Conv ID: {metadata['conversation_id']}")
            
            # Save results to file
            output_file = file_path.replace('.json', '_results.json')
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n✓ Results saved to: {output_file}")
            
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"  Message: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to backend at {BACKEND_URL}")
        print(f"  Make sure FastAPI server is running: python3 backend/main.py")
        return False
    except FileNotFoundError:
        print(f"✗ File not found: {file_path}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("=" * 50)
    print("🚀 Extractify ABCD Dataset Test")
    print("=" * 50)
    
    # Check backend health
    print(f"\n🔍 Checking backend at {BACKEND_URL}...")
    try:
        health = requests.get(f"{BACKEND_URL}/health")
        if health.status_code == 200:
            print(f"✓ Backend is healthy")
        else:
            print(f"✗ Backend returned: {health.status_code}")
    except:
        print(f"✗ Backend is not responding")
        print(f"   Start it with: python3 backend/main.py")
        return
    
    # Test with samples
    samples = [
        ('sample-data/abcd_sample_10.json', 10),
        ('sample-data/abcd_sample_50.json', 50),
    ]
    
    for file_path, count in samples:
        success = test_abcd_extraction(file_path)
        if not success:
            print(f"\n⚠️  Test failed, skipping larger samples")
            break
        print(f"\n{'=' * 50}\n")

if __name__ == '__main__':
    main()
