#!/usr/bin/env python3
"""
Debug script to examine the actual term data structure.
"""

import os
from dotenv import load_dotenv
from atlan_client import AtlanClient

# Load environment variables
load_dotenv()

def main():
    """Examine the term data structure."""
    print("🔍 Examining Term Data Structure for Customer Acquisition Cost (CAC)")
    print("=" * 70)
    
    # Initialize client
    client = AtlanClient()
    
    if not client.is_connected():
        print("❌ Not connected to Atlan")
        return
    
    print("✅ Connected to Atlan")
    
    # Search for the term
    terms = client.search_glossary_terms("Customer Acquisition Cost (CAC)")
    
    if not terms:
        print("❌ No terms found")
        return
    
    print(f"✅ Found {len(terms)} terms")
    
    # Examine the first term in detail
    term = terms[0]
    print(f"\n📋 Term Name: {term.get('name', 'Unknown')}")
    print(f"📋 Term Type: {term.get('__typeName', 'Unknown')}")
    print(f"📋 GUID: {term.get('guid', 'Unknown')}")
    
    print("\n🔍 All Available Fields:")
    print("-" * 40)
    for key, value in term.items():
        if key.startswith('__'):
            continue  # Skip internal fields
        print(f"{key}: {value}")
    
    print("\n🔍 Key Metadata Fields:")
    print("-" * 40)
    key_fields = [
        'certificateStatus', 'description', 'userDescription', 
        'ownerUsers', 'ownerGroups', 'announcementMessage',
        'examples', 'abbreviation', 'anchor', 'qualifiedName',
        'displayName', 'shortDescription', 'longDescription'
    ]
    
    for field in key_fields:
        value = term.get(field)
        if value is not None:
            print(f"{field}: {value}")
        else:
            print(f"{field}: None/Not found")

if __name__ == "__main__":
    main() 