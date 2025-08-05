import streamlit as st
import json
from typing import List, Dict, Any, Optional
from atlan_mcp_integration import atlan_mcp

# Page configuration
st.set_page_config(
    page_title="Atlan MCP Data Explorer",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'search_results' not in st.session_state:
    st.session_state.search_results = []

if 'current_term' not in st.session_state:
    st.session_state.current_term = None

# Main app interface
st.title("🔍 Atlan MCP Data Explorer")
st.markdown("Direct access to your Atlan data catalog using MCP tools")

# Sidebar for search options
with st.sidebar:
    st.header("Search Options")
    
    search_type = st.selectbox(
        "Search Type",
        ["Glossary Terms", "Assets", "All"]
    )
    
    search_limit = st.slider("Results Limit", 5, 50, 20)
    
    st.markdown("---")
    st.markdown("**MCP Status:** 🟢 Connected")
    st.markdown("**Data Source:** Atlan Catalog")
    
    if st.button("Clear Results"):
        st.session_state.search_results = []
        st.session_state.messages = []
        st.session_state.current_term = None
        st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Search Atlan Data Catalog")
    
    # Search input
    search_query = st.text_input(
        "Enter your search query:",
        placeholder="e.g., Customer Acquisition Cost, Revenue, etc."
    )
    
    # Search button
    if st.button("🔍 Search", type="primary"):
        if search_query.strip():
            with st.spinner("Searching Atlan via MCP..."):
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"Searching for: {search_query}"
                })
                
                # Perform search based on type
                if search_type == "Glossary Terms":
                    results = atlan_mcp.search_glossary_terms(search_query, search_limit)
                elif search_type == "Assets":
                    results = atlan_mcp.search_assets_by_term(search_query)
                else:
                    # Search both
                    term_results = atlan_mcp.search_glossary_terms(search_query, search_limit)
                    asset_results = atlan_mcp.search_assets_by_term(search_query)
                    results = term_results + asset_results
                
                st.session_state.search_results = results
                
                # Add assistant response
                if results:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Found {len(results)} results for '{search_query}' using Atlan MCP"
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"No results found for '{search_query}' in Atlan catalog"
                    })
                
                st.rerun()

with col2:
    st.header("Quick Actions")
    
    if st.button("📋 List All Terms"):
        with st.spinner("Fetching all terms via MCP..."):
            results = atlan_mcp.list_all_terms(50)
            st.session_state.search_results = results
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Found {len(results)} total terms in Atlan catalog via MCP"
            })
            st.rerun()
    
    if st.button("🔝 Popular Terms"):
        with st.spinner("Fetching popular terms via MCP..."):
            results = atlan_mcp.get_popular_terms(10)
            st.session_state.search_results = results
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Found {len(results)} popular terms via MCP"
            })
            st.rerun()
    
    if st.button("🔗 Test MCP Connection"):
        with st.spinner("Testing MCP connection..."):
            try:
                # Test the MCP connection
                test_results = atlan_mcp.search_glossary_terms("", 1)
                if test_results:
                    st.success("✅ MCP connection successful!")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "✅ MCP connection to Atlan is working properly"
                    })
                else:
                    st.warning("⚠️ MCP connection returned no results")
            except Exception as e:
                st.error(f"❌ MCP connection failed: {e}")

# Display search results
if st.session_state.search_results:
    st.header("Search Results")
    
    for i, result in enumerate(st.session_state.search_results):
        with st.expander(f"📋 {result.get('displayText', result.get('attributes', {}).get('name', 'Unknown'))}", expanded=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Extract attributes
                attrs = result.get('attributes', {})
                
                st.markdown(f"**Name:** {attrs.get('name', 'Unknown')}")
                st.markdown(f"**Type:** {result.get('typeName', 'Unknown')}")
                
                if attrs.get('userDescription'):
                    st.markdown(f"**Description:** {attrs.get('userDescription')}")
                
                if attrs.get('certificateStatus'):
                    status_color = "🟢" if attrs.get('certificateStatus') == "VERIFIED" else "🟡"
                    st.markdown(f"**Status:** {status_color} {attrs.get('certificateStatus')}")
                
                if attrs.get('ownerUsers'):
                    st.markdown(f"**Owners:** {', '.join(attrs.get('ownerUsers', []))}")
                
                if result.get('guid'):
                    st.code(f"GUID: {result.get('guid')}")
            
            with col2:
                if st.button(f"🔍 Details", key=f"details_{i}"):
                    # Get detailed information
                    details = atlan_mcp.get_term_details(result.get('guid'))
                    if details:
                        st.json(details)
                
                if st.button(f"📊 Assets", key=f"assets_{i}"):
                    # Search for linked assets
                    assets = atlan_mcp.search_assets_by_term(result.get('guid'))
                    if assets:
                        st.markdown(f"**Linked Assets ({len(assets)}):**")
                        for asset in assets[:5]:  # Show first 5
                            st.markdown(f"- {asset.get('name', 'Unknown')} ({asset.get('typeName', 'Unknown')})")
                    else:
                        st.info("No linked assets found")
                
                if st.button(f"🔗 Lineage", key=f"lineage_{i}"):
                    lineage = atlan_mcp.get_lineage(result.get('guid'))
                    if lineage and lineage.get('assets'):
                        st.markdown(f"**Lineage ({lineage.get('direction', 'Unknown')}):**")
                        for asset in lineage['assets'][:3]:  # Show first 3
                            st.markdown(f"- {asset.get('name', 'Unknown')} ({asset.get('relationship', 'Unknown')})")
                    else:
                        st.info("No lineage information available")

# Display conversation history
if st.session_state.messages:
    st.header("Conversation History")
    
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Assistant:** {message['content']}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🔍 Powered by Atlan MCP - Direct data catalog access</p>
    <p>Model Context Protocol integration for real-time data</p>
</div>
""", unsafe_allow_html=True) 