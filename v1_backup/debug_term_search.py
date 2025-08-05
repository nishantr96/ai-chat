#!/usr/bin/env python3
"""
Debug script to test term search functionality.
"""

import os
from dotenv import load_dotenv
from atlan_client import AtlanClient

# Load environment variables
load_dotenv()

def main():
    """Test term search functionality."""
    print("🔍 Testing Atlan Term Search...")
    
    # Initialize client
    client = AtlanClient()
    
    if not client.is_connected():
        print("❌ Not connected to Atlan")
        return
    
    print("✅ Connected to Atlan")
    
    # Test search for Customer Acquisition Cost
    test_terms = [
        "Customer Acquisition Cost",
        "Customer Acquisition Cost (CAC)",
        "customer acquisition cost",
        "CAC"
    ]
    
    for term in test_terms:
        print(f"\n🔍 Searching for: '{term}'")
        print("-" * 50)
        
        try:
            results = client.search_glossary_terms(term)
            print(f"Found {len(results)} results")
            
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"  Name: {result.get('name', 'N/A')}")
                print(f"  GUID: {result.get('guid', 'N/A')}")
                print(f"  Description: {result.get('description', 'N/A')[:100]}...")
                print(f"  Type: {result.get('type_name', 'N/A')}")
                print(f"  Status: {result.get('certificateStatus', 'N/A')}")
                
                # Try to get full details
                if result.get('guid'):
                    print(f"  Getting full details for GUID: {result['guid']}")
                    full_details = client.get_entity_by_guid(result['guid'])
                    if full_details:
                        print(f"  ✅ Full details retrieved successfully")
                        print(f"  Full description: {full_details.get('description', 'N/A')}")
                    else:
                        print(f"  ❌ Failed to get full details")
                
        except Exception as e:
            print(f"❌ Error searching for '{term}': {e}")

if __name__ == "__main__":
    main() 