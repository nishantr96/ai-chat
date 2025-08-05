#!/usr/bin/env python3
"""
Quick test to verify the clarification response fix is working.
"""

import os
from dotenv import load_dotenv
from atlan_client import AtlanClient
from query_processor import QueryProcessor

# Load environment variables
load_dotenv()

def main():
    """Test the clarification response fix."""
    print("🧪 Quick Test: Clarification Response Fix")
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
    
    # Test the exact scenario from the screenshot
    print("\n🔍 Testing clarification response...")
    
    # Simulate the clarification response
    original_term = "customer acquisition cost"
    user_response = "Customer Acquisition Cost (CAC)"
    original_intent = "definition"
    
    print(f"Original term: {original_term}")
    print(f"User response: {user_response}")
    print(f"Original intent: {original_intent}")
    
    # Test the clarification response handling
    result = processor.handle_clarification_response(
        original_term, user_response, original_intent, context
    )
    
    print(f"\n📝 Result: {result.get('content', 'No content')[:200]}...")
    print(f"📝 Content length: {len(result.get('content', ''))}")
    print(f"📝 Context updated: {context.get('last_discussed_term')}")
    
    if "I'm not sure how to handle that clarification" in result.get('content', ''):
        print("❌ Still showing the old error message!")
    else:
        print("✅ Clarification response fix is working!")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    main() 