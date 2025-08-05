#!/usr/bin/env python3
"""
Demo script to showcase the Data Chat Interface components.
This demonstrates how the system works without running the full Streamlit app.
"""

from atlan_client import AtlanClient
from query_processor import QueryProcessor
from chart_generator import ChartGenerator
import pandas as pd
import json

def main():
    print("🚀 Data Chat Interface Demo")
    print("=" * 50)
    
    # Initialize components
    print("\n📊 Initializing components...")
    atlan_client = AtlanClient()
    query_processor = QueryProcessor(atlan_client)
    chart_generator = ChartGenerator()
    
    # Test connection
    print(f"🔗 Atlan connection status: {'✅ Connected' if atlan_client.is_connected() else '❌ Disconnected'}")
    
    # Demo queries
    demo_queries = [
        "How is Customer Acquisition Cost defined?",
        "Which assets use the term revenue?",
        "What tables contain customer data?",
        "Show me the annual revenue from last year"
    ]
    
    print("\n💬 Testing sample queries...")
    print("-" * 40)
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        try:
            response = query_processor.process_query(query)
            print(f"   Response: {response.get('content', 'No response')[:100]}...")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Demo asset search
    print("\n🔍 Testing asset search...")
    print("-" * 30)
    
    try:
        # Search for glossary terms
        terms = atlan_client.search_glossary_terms("revenue")
        print(f"Found {len(terms)} glossary terms for 'revenue':")
        for term in terms[:2]:
            print(f"  • {term.get('name', 'Unknown')}: {term.get('description', 'No description')[:50]}...")
        
        # Search for tables
        tables = atlan_client.search_tables_by_name("customer")
        print(f"\nFound {len(tables)} tables containing 'customer':")
        for table in tables[:2]:
            print(f"  • {table.get('name', 'Unknown')}: {table.get('description', 'No description')[:50]}...")
    
    except Exception as e:
        print(f"Error during asset search: {e}")
    
    # Demo chart generation
    print("\n📈 Testing chart generation...")
    print("-" * 35)
    
    try:
        # Create sample data
        sample_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'Revenue': [10000, 12000, 15000, 13000, 16000],
            'Customers': [100, 120, 150, 130, 160]
        })
        
        # Test chart suggestions
        suggestions = chart_generator.suggest_chart_types(sample_data)
        print(f"Suggested chart types for sample data: {', '.join(suggestions)}")
        
        # Generate a chart
        chart = chart_generator.generate_chart(sample_data, "bar chart")
        if chart:
            print("✅ Successfully generated bar chart")
        else:
            print("❌ Failed to generate chart")
    
    except Exception as e:
        print(f"Error during chart generation: {e}")
    
    print(f"\n🎉 Demo complete! The full application is running at: http://localhost:8501")
    print("📝 Try these example queries in the web interface:")
    for query in demo_queries:
        print(f"   • {query}")

if __name__ == "__main__":
    main() 