#!/usr/bin/env python3
"""
Test script to verify query processor functionality.
"""

import os
from dotenv import load_dotenv
from atlan_client import AtlanClient
from query_processor import QueryProcessor

# Load environment variables
load_dotenv()

def main():
    """Test query processor functionality."""
    print("🧪 Testing Query Processor...")
    
    # Initialize client and processor
    client = AtlanClient()
    processor = QueryProcessor(client)
    
    if not client.is_connected():
        print("❌ Not connected to Atlan")
        return
    
    print("✅ Connected to Atlan")
    
    # Test queries
    test_queries = [
        "define Customer Acquisition Cost",
        "define Customer Acquisition Cost (CAC)",
        "what is Customer Acquisition Cost",
        "define CAC"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 60)
        
        try:
            # Process the query
            result = processor.process_query(query)
            
            print(f"Response type: {type(result)}")
            if isinstance(result, dict):
                print(f"Response keys: {list(result.keys())}")
                if 'content' in result:
                    print(f"Content length: {len(result['content'])}")
                    print(f"Content preview: {result['content'][:200]}...")
                else:
                    print(f"Full response: {result}")
            else:
                print(f"Response: {result}")
                
        except Exception as e:
            print(f"❌ Error processing query: {e}")

if __name__ == "__main__":
    main() 