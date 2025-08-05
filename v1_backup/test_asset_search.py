#!/usr/bin/env python3
"""
Test script to verify asset search functionality.
"""

import os
from dotenv import load_dotenv
from atlan_client import AtlanClient

def test_asset_search():
    """Test finding assets that use a specific term."""
    
    # Load environment variables
    load_dotenv()
    
    # Set API key
    os.environ['OPENAI_API_KEY'] = "sk-S_N3-OI2h814ONFCxnDw5w"
    
    # Initialize client
    client = AtlanClient()
    
    if not client.is_connected():
        print("❌ Failed to connect to Atlan")
        return
    
    print("✅ Connected to Atlan successfully")
    
    # Test 1: Search for the Customer Acquisition Cost term
    print("\n🔍 Testing: Search for 'Customer Acquisition Cost' term...")
    terms = client.search_glossary_terms("Customer Acquisition Cost")
    
    if not terms:
        print("❌ No terms found")
        return
    
    print(f"✅ Found {len(terms)} terms")
    
    # Find the exact term
    target_term = None
    for term in terms:
        if term.get('name', '').lower() == 'customer acquisition cost (cac)':
            target_term = term
            break
    
    if not target_term:
        print("❌ Could not find 'Customer Acquisition Cost (CAC)' term")
        return
    
    print(f"✅ Found target term: {target_term.get('name')}")
    print(f"   GUID: {target_term.get('guid')}")
    
    # Test 2: Find assets using this term
    print(f"\n🔍 Testing: Find assets using term '{target_term.get('name')}'...")
    assets = client.find_assets_with_term(target_term.get('guid'))
    
    if assets:
        print(f"✅ Found {len(assets)} assets using the term:")
        for i, asset in enumerate(assets[:10]):  # Show first 10
            print(f"   {i+1}. {asset.get('name', 'Unknown')} ({asset.get('type_name', 'Unknown')})")
        if len(assets) > 10:
            print(f"   ... and {len(assets) - 10} more")
    else:
        print("❌ No assets found using the term")
    
    # Test 3: Try a different approach - search for assets with similar names
    print(f"\n🔍 Testing: Search for assets with 'customer acquisition' in name/description...")
    similar_assets = client.search_by_text("customer acquisition", ["Table", "View", "Column"])
    
    if similar_assets:
        print(f"✅ Found {len(similar_assets)} similar assets:")
        for i, asset in enumerate(similar_assets[:5]):  # Show first 5
            print(f"   {i+1}. {asset.get('name', 'Unknown')} ({asset.get('type_name', 'Unknown')})")
    else:
        print("❌ No similar assets found")

if __name__ == "__main__":
    print("🚀 Testing Asset Search Functionality")
    print("=" * 50)
    test_asset_search()
    print("\n" + "=" * 50) 