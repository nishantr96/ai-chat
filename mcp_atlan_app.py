import streamlit as st
import json
from typing import List, Dict, Any, Optional
import requests

# Page configuration
st.set_page_config(
    page_title="Atlan Data Catalog Explorer",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'search_results' not in st.session_state:
    st.session_state.search_results = []

def search_atlan_terms(query: str = "", limit: int = 20) -> List[Dict[str, Any]]:
    """Search for glossary terms using Atlan MCP"""
    try:
        # This would be replaced with actual MCP call
        # For now, we'll simulate the response structure
        return []
    except Exception as e:
        st.error(f"Error searching Atlan: {e}")
        return []

def get_term_details(guid: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a specific term"""
    try:
        # This would be replaced with actual MCP call
        return None
    except Exception as e:
        st.error(f"Error getting term details: {e}")
        return None

def search_assets_by_term(term_guid: str) -> List[Dict[str, Any]]:
    """Search for assets linked to a specific term"""
    try:
        # This would be replaced with actual MCP call
        return []
    except Exception as e:
        st.error(f"Error searching assets: {e}")
        return []

# Main app interface
st.title("🔍 Atlan Data Catalog Explorer")
st.markdown("Direct access to your Atlan data catalog without LLM dependencies")

# Sidebar for search options
with st.sidebar:
    st.header("Search Options")
    
    search_type = st.selectbox(
        "Search Type",
        ["Glossary Terms", "Assets", "All"]
    )
    
    search_limit = st.slider("Results Limit", 5, 50, 20)
    
    if st.button("Clear Results"):
        st.session_state.search_results = []
        st.session_state.messages = []
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
            with st.spinner("Searching Atlan..."):
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"Searching for: {search_query}"
                })
                
                # Perform search based on type
                if search_type == "Glossary Terms":
                    results = search_atlan_terms(search_query, search_limit)
                elif search_type == "Assets":
                    results = search_assets_by_term(search_query)
                else:
                    # Search both
                    term_results = search_atlan_terms(search_query, search_limit)
                    asset_results = search_assets_by_term(search_query)
                    results = term_results + asset_results
                
                st.session_state.search_results = results
                
                # Add assistant response
                if results:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Found {len(results)} results for '{search_query}'"
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"No results found for '{search_query}'"
                    })
                
                st.rerun()

with col2:
    st.header("Quick Actions")
    
    if st.button("📋 List All Terms"):
        with st.spinner("Fetching all terms..."):
            results = search_atlan_terms("", 50)
            st.session_state.search_results = results
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Found {len(results)} total terms in the catalog"
            })
            st.rerun()
    
    if st.button("🔝 Popular Terms"):
        with st.spinner("Fetching popular terms..."):
            # This would search for terms with high usage/popularity
            results = search_atlan_terms("", 10)  # Limit to 10 for "popular"
            st.session_state.search_results = results
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Found {len(results)} popular terms"
            })
            st.rerun()

# Display search results
if st.session_state.search_results:
    st.header("Search Results")
    
    for i, result in enumerate(st.session_state.search_results):
        with st.expander(f"📋 {result.get('name', 'Unknown')}", expanded=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Name:** {result.get('name', 'Unknown')}")
                st.markdown(f"**Type:** {result.get('typeName', 'Unknown')}")
                
                if result.get('userDescription'):
                    st.markdown(f"**Description:** {result.get('userDescription')}")
                
                if result.get('certificateStatus'):
                    status_color = "🟢" if result.get('certificateStatus') == "VERIFIED" else "🟡"
                    st.markdown(f"**Status:** {status_color} {result.get('certificateStatus')}")
                
                if result.get('ownerUsers'):
                    st.markdown(f"**Owners:** {', '.join(result.get('ownerUsers', []))}")
                
                if result.get('guid'):
                    st.code(f"GUID: {result.get('guid')}")
            
            with col2:
                if st.button(f"🔍 Details", key=f"details_{i}"):
                    # Get detailed information
                    details = get_term_details(result.get('guid'))
                    if details:
                        st.json(details)
                
                if st.button(f"📊 Assets", key=f"assets_{i}"):
                    # Search for linked assets
                    assets = search_assets_by_term(result.get('guid'))
                    if assets:
                        st.markdown(f"**Linked Assets ({len(assets)}):**")
                        for asset in assets[:5]:  # Show first 5
                            st.markdown(f"- {asset.get('name', 'Unknown')}")
                    else:
                        st.info("No linked assets found")

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
    <p>No LLM dependencies - Pure Atlan data</p>
</div>
""", unsafe_allow_html=True) 