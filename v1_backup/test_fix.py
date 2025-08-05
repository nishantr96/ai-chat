#!/usr/bin/env python3
"""
Test script to verify the fix for term formatting.
"""

import os
from dotenv import load_dotenv
from atlan_client import AtlanClient
from query_processor import QueryProcessor

# Load environment variables
load_dotenv()

def main():
    """Test the fixed term formatting."""
    print("🧪 Testing Fixed Term Formatting")
    print("=" * 50)
    
    # Initialize components
    client = AtlanClient()
    processor = QueryProcessor(client)
    
    if not client.is_connected():
        print("❌ Not connected to Atlan")
        return
    
    print("✅ Connected to Atlan")
    
    # Test the definition query
    query = "define Customer Acquisition Cost (CAC)"
    print(f"\n🔍 Testing query: {query}")
    
    response, requires_clarification = processor._handle_definition_query(query)
    
    print(f"\n📝 Response (requires clarification: {requires_clarification}):")
    print("-" * 50)
    print(response)
    
    # Check if the response contains the expected metadata
    expected_fields = [
        "Status: VERIFIED",
        "Owners: @cameron.kayfish",
        "Owner Groups: @analytics_engineering, @finance",
        "Announcement: More information on the simple and new complex calculation method"
    ]
    
    print(f"\n✅ Verification:")
    for field in expected_fields:
        if field in response:
            print(f"  ✅ Found: {field}")
        else:
            print(f"  ❌ Missing: {field}")

if __name__ == "__main__":
    main() 