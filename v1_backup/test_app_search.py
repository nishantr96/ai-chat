#!/usr/bin/env python3
"""
Test script to verify the application search is working correctly.
"""

import os
from dotenv import load_dotenv
from atlan_client import AtlanClient
from query_processor import QueryProcessor

# Load environment variables
load_dotenv()

def main():
    """Test the application search functionality."""
    print("🧪 Testing Application Search Functionality")
    print("=" * 60)
    
    # Initialize components
    client = AtlanClient()
    processor = QueryProcessor(client)
    
    if not client.is_connected():
        print("❌ Not connected to Atlan")
        return
    
    print("✅ Connected to Atlan")
    
    # Test the exact same search that happens in the app
    test_queries = [
        "define Customer Acquisition Cost (CAC)",
        "what is Customer Acquisition Cost",
        "Customer Acquisition Cost definition",
        "define CAC"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 50)
        
        # Process the query exactly like the app does
        response = processor.process_query(query)
        
        if isinstance(response, dict):
            content = response.get("content", "No response")
            requires_clarification = response.get("requires_clarification", False)
        elif isinstance(response, tuple):
            content, requires_clarification = response
        else:
            content = str(response)
            requires_clarification = False
        
        print(f"Response length: {len(content)} characters")
        print(f"Requires clarification: {requires_clarification}")
        print(f"Response preview: {content[:200]}...")
        
        # Check if the response contains the expected term
        if "Customer Acquisition Cost" in content or "CAC" in content:
            print("✅ Found Customer Acquisition Cost in response!")
        else:
            print("❌ Customer Acquisition Cost not found in response")
        
        # Check if the response contains a definition
        if "refers to" in content or "total cost" in content or "acquire" in content:
            print("✅ Response contains definition content!")
        else:
            print("❌ Response doesn't contain definition content")

if __name__ == "__main__":
    main() 