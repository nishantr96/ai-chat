#!/usr/bin/env python3
"""
Test script to verify the clarification response fix.
"""

import os
from dotenv import load_dotenv
from atlan_client import AtlanClient
from query_processor import QueryProcessor

# Load environment variables
load_dotenv()

def main():
    """Test the clarification response fix."""
    print("🧪 Testing Clarification Response Fix")
    print("=" * 50)
    
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
        'previous_queries': []
    }
    
    # Test the clarification response handling
    print("\n🔍 Testing clarification response for 'Customer Acquisition Cost (CAC)'")
    
    # Simulate the clarification response
    original_term = "customer acquisition cost"
    user_response = "Customer Acquisition Cost (CAC)"
    original_intent = "definition"
    
    print(f"Original term: {original_term}")
    print(f"User response: {user_response}")
    print(f"Original intent: {original_intent}")
    
    # Process the clarification response
    result = processor.handle_clarification_response(
        original_term, user_response, original_intent, context
    )
    
    print(f"\n📝 Result:")
    print(f"Content: {result.get('content', 'No content')[:200]}...")
    print(f"Requires clarification: {result.get('requires_clarification', False)}")
    print(f"Context updates: {result.get('context_updates', 'None')}")
    print(f"Updated context: {context}")
    
    # Test follow-up question
    print("\n🔍 Testing follow-up question after clarification")
    follow_up_query = "What assets use this term?"
    
    print(f"Follow-up query: {follow_up_query}")
    print(f"Context before: {context}")
    
    # Process the follow-up query
    follow_up_result = processor.process_query(follow_up_query, context)
    
    print(f"\n📝 Follow-up result:")
    print(f"Content: {follow_up_result.get('content', 'No content')[:200]}...")
    print(f"Requires clarification: {follow_up_result.get('requires_clarification', False)}")
    print(f"Context updates: {follow_up_result.get('context_updates', 'None')}")
    print(f"Updated context: {context}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main() 