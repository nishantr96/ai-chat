#!/usr/bin/env python3
"""
Test script to verify clarification response context handling.
"""

import os
from dotenv import load_dotenv
from atlan_client import AtlanClient
from query_processor import QueryProcessor

# Load environment variables
load_dotenv()

def main():
    """Test the clarification response context handling."""
    print("🧪 Testing Clarification Response Context Handling")
    print("=" * 60)
    
    # Initialize components
    client = AtlanClient()
    processor = QueryProcessor(client)
    
    if not client.is_connected():
        print("❌ Not connected to Atlan")
        return
    
    print("✅ Connected to Atlan")
    
    # Initialize conversation context
    context = {
        'last_discussed_term': None,
        'previous_queries': [],
        'session_start_time': '2024-01-01T00:00:00'
    }
    
    print(f"\n📋 Initial context: {context.get('last_discussed_term')}")
    
    # Test 1: Clarification response for definition
    print("\n🔍 Test 1: Clarification response for definition")
    print("Original term: 'customer acquisition cost'")
    print("User response: 'Customer Acquisition Cost (CAC)'")
    
    response1 = processor.handle_clarification_response(
        "customer acquisition cost", 
        "Customer Acquisition Cost (CAC)", 
        "definition", 
        context
    )
    
    print(f"Response content: {response1.get('content', 'No content')[:100]}...")
    print(f"Context after clarification: {context.get('last_discussed_term')}")
    print(f"Context updates in response: {response1.get('context_updates', 'None')}")
    
    # Test 2: Follow-up question using context
    print("\n🔍 Test 2: Follow-up question using context")
    print("Query: 'What assets use this term?'")
    
    response2 = processor.process_query("What assets use this term?", context)
    print(f"Response content: {response2.get('content', 'No content')[:100]}...")
    print(f"Context after follow-up: {context.get('last_discussed_term')}")
    
    # Test 3: Another follow-up with pronoun
    print("\n🔍 Test 3: Follow-up with pronoun")
    print("Query: 'Tell me more about it'")
    
    response3 = processor.process_query("Tell me more about it", context)
    print(f"Response content: {response3.get('content', 'No content')[:100]}...")
    print(f"Context after pronoun query: {context.get('last_discussed_term')}")
    
    print("\n✅ Clarification context handling test completed!")

if __name__ == "__main__":
    main() 