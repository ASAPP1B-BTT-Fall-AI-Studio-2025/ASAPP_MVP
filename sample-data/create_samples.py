#!/usr/bin/env python3
"""
Script to create test files from the ABCD dataset
"""
import json
import sys

def create_test_samples():
    """Create smaller test files from the ABCD dataset"""
    
    # Load the full ABCD dataset
    print("Loading ABCD dataset...")
    with open('abcd_v1.1.json', 'r') as f:
        data = json.load(f)
    
    conversations = data.get('train', [])
    total = len(conversations)
    print(f"Total conversations: {total}")
    
    # Create sample sizes
    samples = {
        'abcd_sample_10.json': 10,
        'abcd_sample_50.json': 50,
        'abcd_sample_100.json': 100,
    }
    
    for filename, count in samples.items():
        sample_data = {
            'train': conversations[:count],
            'metadata': {
                'source': 'ABCD v1.1',
                'total_conversations': count,
                'sample_type': f'First {count} conversations'
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(sample_data, f, indent=2)
        
        print(f"✓ Created {filename} with {count} conversations")
    
    print("\nSample files created successfully!")
    print("Use these for testing the bulk extraction feature")

if __name__ == '__main__':
    try:
        create_test_samples()
    except FileNotFoundError:
        print("Error: abcd_v1.1.json not found in current directory")
        print("Please make sure you've decompressed the .gz file first")
        sys.exit(1)
