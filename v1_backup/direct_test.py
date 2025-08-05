#!/usr/bin/env python3
"""
Direct test of the simplified implementation
"""

import sys
import os

# Add current directory to path
sys.path.append('.')

def test_simplified_implementation():
    """Test the simplified implementation directly"""
    print("🧪 Testing simplified implementation directly...")
    
    try:
        from atlan_client import AtlanClient
        
        # Create client
        client = AtlanClient()
        
        # Test the CAC term
        term_guid = "af6a32d4-936b-4a59-9917-7082c56ba443"
        term_name = "Customer Acquisition Cost (CAC)"
        
        print(f"🔍 Testing with term GUID: {term_guid}")
        print(f"🏷️  Term name: {term_name}")
        
        # Call the method directly
        assets = client.find_assets_with_term(term_guid, term_name)
        
        print(f"✅ Found {len(assets)} assets")
        
        for i, asset in enumerate(assets, 1):
            print(f"  {i}. {asset.get('name', 'Unknown')} ({asset.get('typeName', 'Unknown')})")
            print(f"     GUID: {asset.get('guid', 'Unknown')}")
            print(f"     Description: {asset.get('description', 'No description')}")
            print()
        
        if len(assets) == 3:
            print("✅ SUCCESS: Simplified implementation is working correctly!")
            return True
        else:
            print(f"❌ FAILED: Expected 3 assets, got {len(assets)}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_simplified_implementation()
    sys.exit(0 if success else 1) 