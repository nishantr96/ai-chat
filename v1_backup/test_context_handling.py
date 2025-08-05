#!/usr/bin/env python3
"""
Test script to verify improved context handling for follow-up questions.
"""

import os
from dotenv import load_dotenv
from atlan_client import AtlanClient
from query_processor import QueryProcessor

# Load environment variables
load_dotenv()

def main():
    """Test the improved context handling."""
    print("🧪 Testing Improved Context Handling")
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
        'previous_queries': [],
        'session_start_time': '2024-01-01T00:00:00'
    }
    
    # Test 1: Initial definition query
    print("\n🔍 Test 1: Initial definition query")
    print("Query: 'define Customer Acquisition Cost (CAC)'")
    
    response1 = processor.process_query("define Customer Acquisition Cost (CAC)", context)
    print(f"Response: {response1.get('content', 'No content')[:200]}...")
    print(f"Context after query: {context.get('last_discussed_term')}")
    
    # Test 2: Follow-up question using context
    print("\n🔍 Test 2: Follow-up question using context")
    print("Query: 'What assets use this term?'")
    
    response2 = processor.process_query("What assets use this term?", context)
    print(f"Response: {response2.get('content', 'No content')[:200]}...")
    print(f"Context after query: {context.get('last_discussed_term')}")
    
    # Test 3: Another follow-up with pronoun
    print("\n🔍 Test 3: Follow-up with pronoun")
    print("Query: 'Tell me more about it'")
    
    response3 = processor.process_query("Tell me more about it", context)
    print(f"Response: {response3.get('content', 'No content')[:200]}...")
    print(f"Context after query: {context.get('last_discussed_term')}")
    
    # Test 4: Context-aware term extraction
    print("\n🔍 Test 4: Testing context-aware term extraction")
    test_queries = [
        "What assets use this term?",
        "Tell me about it",
        "Which assets use that term?",
        "Find assets for this",
        "What uses it?"
    ]
    
    for query in test_queries:
        extracted_term = processor._extract_term_from_query(query, context)
        print(f"Query: '{query}' -> Extracted term: '{extracted_term}'")
    
    print("\n✅ Context handling test completed!")

if __name__ == "__main__":
    main() 