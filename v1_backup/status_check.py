#!/usr/bin/env python3
"""
Status check script to verify all components are working.
"""

import os
from dotenv import load_dotenv
from atlan_client import AtlanClient
from query_processor import QueryProcessor

# Load environment variables
load_dotenv()

def main():
    """Check the status of all components."""
    print("🔍 Data Chat Interface - Status Check")
    print("=" * 50)
    
    # Check environment
    print("\n📋 Environment Check:")
    print(f"  ATLAN_API_TOKEN: {'✅ Set' if os.getenv('ATLAN_API_TOKEN') else '❌ Missing'}")
    print(f"  ATLAN_BASE_URL: {'✅ Set' if os.getenv('ATLAN_BASE_URL') else '⚠️  Using default'}")
    print(f"  OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here' else '❌ Missing or default'}")
    
    # Check Atlan connection
    print("\n🔗 Atlan Connection Check:")
    client = AtlanClient()
    if client.is_connected():
        print("  ✅ Connected to Atlan")
        
        # Test a simple search
        try:
            terms = client.search_glossary_terms("Customer Acquisition Cost")
            if terms:
                print(f"  ✅ Found {len(terms)} terms in glossary")
                print(f"  ✅ First term: {terms[0].get('name', 'Unknown')}")
            else:
                print("  ⚠️  No terms found in glossary")
        except Exception as e:
            print(f"  ❌ Search failed: {e}")
    else:
        print("  ❌ Not connected to Atlan")
    
    # Check query processor
    print("\n🧠 Query Processor Check:")
    try:
        processor = QueryProcessor(client)
        print("  ✅ Query processor initialized")
        
        # Test a simple query
        result = processor.process_query("define Customer Acquisition Cost")
        if result and 'content' in result:
            print("  ✅ Query processing working")
            print(f"  ✅ Response length: {len(result['content'])} characters")
            if "Customer Acquisition Cost" in result['content']:
                print("  ✅ Correct term found in response")
            else:
                print("  ⚠️  Expected term not found in response")
        else:
            print("  ❌ Query processing failed")
    except Exception as e:
        print(f"  ❌ Query processor failed: {e}")
    
    print("\n🎯 Summary:")
    print("  If all checks show ✅, the application should be working correctly.")
    print("  If you see ❌, check the configuration and try again.")
    print("\n🌐 Access the application at: http://localhost:8504")

if __name__ == "__main__":
    main() 