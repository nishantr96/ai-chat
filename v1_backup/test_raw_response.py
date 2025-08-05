#!/usr/bin/env python3
"""
Test script to see the raw response before LLM enhancement.
"""

import os
from dotenv import load_dotenv
from atlan_client import AtlanClient
from query_processor import QueryProcessor

# Load environment variables
load_dotenv()

def main():
    """Test the raw response before LLM enhancement."""
    print("🧪 Testing Raw Response (Before LLM Enhancement)")
    print("=" * 60)
    
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
    
    # Get the raw response without LLM enhancement
    response, requires_clarification = processor._handle_definition_query(query)
    
    print(f"\n📝 Raw Response (requires clarification: {requires_clarification}):")
    print("-" * 60)
    print(response)
    
    # Also test the direct term formatting
    print(f"\n🔍 Direct Term Formatting Test:")
    print("-" * 60)
    
    # Get the term directly
    terms = client.search_glossary_terms("Customer Acquisition Cost (CAC)")
    if terms:
        term = terms[0]
        raw_formatted = processor._format_glossary_term(term)
        print(raw_formatted)

if __name__ == "__main__":
    main() 