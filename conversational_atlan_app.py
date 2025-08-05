import streamlit as st
import json
from typing import List, Dict, Any, Optional
from atlan_client import AtlanSDKClient
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Conversational Atlan Data Assistant",
    page_icon="💬",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'search_results' not in st.session_state:
    st.session_state.search_results = []

if 'current_context' not in st.session_state:
    st.session_state.current_context = {}

def analyze_intent(user_input: str) -> Dict[str, Any]:
    """Analyze user intent using LLM or fallback to keyword matching"""
    print(f"DEBUG: analyze_intent called with: '{user_input}'")
    
    try:
        # Try LLM-based intent analysis
        print(f"DEBUG: Attempting LLM-based intent analysis...")
        client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an intent analyzer for a data catalog assistant. Analyze the user's intent and return a JSON response with the following structure: {\"intent\": \"define_term|list_terms|find_assets|unknown\", \"entities\": [\"term_name\"], \"confidence\": 0.0-1.0, \"requires_confirmation\": false, \"suggested_phrasing\": null, \"explanation\": \"brief explanation\"}"},
                {"role": "user", "content": f"Analyze the intent of this user input: '{user_input}'"}
            ],
            temperature=0.1
        )
        
        print(f"DEBUG: LLM response received")
        result = json.loads(response.choices[0].message.content)
        print(f"DEBUG: LLM intent result: {result}")
        return result
        
    except Exception as e:
        print(f"DEBUG: LLM analysis failed: {e}")
        print(f"DEBUG: Falling back to keyword-based analysis...")
        # Fallback to keyword-based intent analysis
        return fallback_intent_analysis(user_input)

def fallback_intent_analysis(user_input: str) -> Dict[str, Any]:
    """Fallback intent analysis using keyword matching"""
    print(f"DEBUG: fallback_intent_analysis called with: '{user_input}'")
    input_lower = user_input.lower()
    print(f"DEBUG: input_lower: '{input_lower}'")
    
    # Check for list_terms intent first
    if any(word in input_lower for word in ["list", "show", "what terms", "available terms", "all terms", "terms available"]):
        print(f"DEBUG: Detected list_terms intent")
        return {
            "intent": "list_terms",
            "entities": [],
            "confidence": 0.9,
            "requires_confirmation": False,
            "suggested_phrasing": None,
            "explanation": "Detected intent to list terms using keyword matching"
        }
    
    # Check for define_term intent
    define_keywords = ["define", "what is", "meaning of", "definition of", "tell me about"]
    if any(word in input_lower for word in define_keywords):
        print(f"DEBUG: Found define keyword in input")
        for keyword in define_keywords:
            if keyword in input_lower:
                term_part = user_input[input_lower.find(keyword) + len(keyword):].strip()
                print(f"DEBUG: Extracted term_part: '{term_part}'")
                if term_part:
                    return {
                        "intent": "define_term",
                        "entities": [term_part.strip('?')],
                        "confidence": 0.8,
                        "requires_confirmation": False,
                        "suggested_phrasing": None,
                        "explanation": f"Detected intent to define term '{term_part}' using keyword matching"
                    }
    
    # Check for find_assets intent
    asset_keywords = ["assets for", "data for", "show assets", "find assets", "related to"]
    if any(word in input_lower for word in asset_keywords):
        print(f"DEBUG: Found asset keyword in input")
        for keyword in asset_keywords:
            if keyword in input_lower:
                term_part = user_input[input_lower.find(keyword) + len(keyword):].strip()
                print(f"DEBUG: Extracted term_part: '{term_part}'")
                if term_part:
                    return {
                        "intent": "find_assets",
                        "entities": [term_part.strip('?')],
                        "confidence": 0.8,
                        "requires_confirmation": False,
                        "suggested_phrasing": None,
                        "explanation": f"Detected intent to find assets for '{term_part}' using keyword matching"
                    }
    
    print(f"DEBUG: No intent detected, returning unknown")
    # Default to unknown
    return {
        "intent": "unknown",
        "entities": [],
        "confidence": 0.5,
        "requires_confirmation": False,
        "suggested_phrasing": "I'm not sure how to help with that. Can you rephrase?",
        "explanation": "Could not determine intent from keywords."
    }

def format_linked_assets_table(assets: List[Dict[str, Any]]) -> str:
    """Format linked assets as a markdown table with clickable links"""
    if not assets:
        return "*No linked assets found*"
    
    table = "| Name | Asset Type | Source Name |\n"
    table += "|------|------------|-------------|\n"
    
    for asset in assets:
        name = asset.get('name', 'Unknown')
        asset_type = asset.get('typeName', 'Unknown')
        # Prioritize connectionName over connectorName for source identification
        source_name = asset.get('connectionName') or asset.get('connectorName') or 'Unknown'
        asset_guid = asset.get('guid', '')
        
        # Clean up the data for display
        name_display = str(name)[:50] + "..." if len(str(name)) > 50 else str(name)
        asset_type_display = str(asset_type)[:20] + "..." if len(str(asset_type)) > 20 else str(asset_type)
        source_name_display = str(source_name)[:20] + "..." if len(str(source_name)) > 20 else str(source_name)
        
        # Create clickable link for asset name if we have a GUID
        if asset_guid and asset_guid != 'Unknown':
            # Construct Atlan asset URL - this is a best guess based on typical Atlan URL patterns
            atlan_asset_url = f"https://home.atlan.com/asset/{asset_guid}"
            name_link = f"[{name_display}]({atlan_asset_url})"
        else:
            name_link = name_display
        
        table += f"| {name_link} | {asset_type_display} | {source_name_display} |\n"
    
    return table

def format_rich_term_display(term: Dict[str, Any], linked_assets: List[Dict[str, Any]] = None) -> str:
    """Format a term with the exact display format requested by the user"""
    response = f"## 📋 **{term.get('name', 'Unknown')}**\n\n"
    
    # 2. Description
    description = term.get('userDescription') or term.get('description') or term.get('longDescription')
    if description:
        response += f"### 📖 Description\n{description}\n\n"
    else:
        response += f"### 📖 Description\n*No description available*\n\n"
    
    # 3. Categories
    categories = []
    if term.get('assetTags'):
        categories.extend(term.get('assetTags', []))
    if term.get('termType'):
        categories.append(term.get('termType'))
    
    if categories:
        response += f"### 🏷️ Categories\n"
        for category in categories:
            response += f"• **{category}**\n"
        response += "\n"
    else:
        response += f"### 🏷️ Categories\n*No categories assigned*\n\n"
    
    # 4. Certificate
    if term.get('certificateStatus'):
        status_emoji = "🟢" if term.get('certificateStatus') == "VERIFIED" else "🟡" if term.get('certificateStatus') == "DRAFT" else "🔴"
        response += f"### ✅ Certificate\n{status_emoji} **{term.get('certificateStatus')}**\n\n"
    else:
        response += f"### ✅ Certificate\n*No certificate status*\n\n"
    
    # 5. Owners
    owners = []
    if term.get('ownerUsers'):
        owners.extend(term.get('ownerUsers', []))
    if term.get('ownerGroups'):
        owners.extend(term.get('ownerGroups', []))
    
    if owners:
        response += f"### 👥 Owners\n"
        for owner in owners:
            response += f"• **{owner}**\n"
        response += "\n"
    else:
        response += f"### 👥 Owners\n*No owners assigned*\n\n"
    
    # 6. Score (if available)
    if term.get('viewScore'):
        response += f"### 📊 Score\n**{term.get('viewScore')}**\n\n"
    elif term.get('popularityScore'):
        response += f"### 📊 Popularity Score\n**{term.get('popularityScore')}**\n\n"
    
    if term.get('starredCount'):
        response += f"### ⭐ Popularity\n**Starred {term.get('starredCount')} times**\n\n"
    
    # 7. Link to Atlan glossary term
    if term.get('qualifiedName'):
        # Construct Atlan URL - this is a best guess based on typical Atlan URL patterns
        atlan_url = f"https://home.atlan.com/glossary/{term.get('guid', '')}"
        response += f"### 🔗 Atlan Glossary Term\n[View in Atlan]({atlan_url})\n\n"
    
    # 8. Linked Assets Table
    response += f"### 📊 Linked Assets"
    if linked_assets:
        response += f" ({len(linked_assets)} total)\n"
        response += format_linked_assets_table(linked_assets)
    else:
        response += " (0 total)\n"
        response += "*No linked assets found*\n"
    response += "\n"
    
    # Show technical details for debugging
    if term.get('qualifiedName') or term.get('guid'):
        response += f"---\n**Technical Details:**\n"
        if term.get('qualifiedName'):
            response += f"• **Qualified Name:** `{term.get('qualifiedName')}`\n"
        if term.get('guid'):
            response += f"• **GUID:** `{term.get('guid')}`\n"
    
    return response

def handle_define_term(term_name: str, atlan_client: AtlanSDKClient) -> str:
    """Handle defining a glossary term"""
    print(f"DEBUG: handle_define_term called with term_name: {term_name}")
    
    try:
        # Search for the term
        print(f"DEBUG: Searching for term: {term_name}")
        terms = atlan_client.search_terms_by_name(term_name)
        print(f"DEBUG: search_terms_by_name returned {len(terms)} terms")
        
        if not terms:
            return f"❌ No glossary term found for '{term_name}'. Please check the spelling or try a different term."
        
        # Get the first matching term
        term = terms[0]
        print(f"DEBUG: Selected term: {term.get('name', 'Unknown')}")
        print(f"DEBUG: Term data keys: {list(term.keys())}")
        
        # Get linked assets
        print(f"DEBUG: Getting linked assets for term GUID: {term.get('guid', 'No GUID')}")
        linked_assets = atlan_client.find_assets_with_term(term.get('guid', ''), term.get('name', ''))
        print(f"DEBUG: Found {len(linked_assets)} linked assets")
        
        # Format the response
        response = format_rich_term_display(term, linked_assets)
        print(f"DEBUG: Formatted response length: {len(response)}")
        return response
        
    except Exception as e:
        print(f"DEBUG: Error in handle_define_term: {e}")
        return f"❌ Error retrieving term information: {str(e)}"

def handle_list_terms(atlan_client: AtlanSDKClient) -> str:
    """Handle list terms intent"""
    try:
        terms = atlan_client.search_terms_by_name('')  # Empty string to get all terms
        
        if not terms:
            return "I couldn't find any terms in the Atlan catalog."
        
        response = f"Here are the terms available in the Atlan glossary ({len(terms)} total):\n\n"
        
        for i, term in enumerate(terms[:10], 1):
            response += f"{i}. **{term.get('name', 'Unknown')}**"
            if term.get('displayName') and term.get('displayName') != term.get('name'):
                response += f" ({term.get('displayName')})"
            response += "\n"
            
            if term.get('userDescription'):
                response += f"   {term.get('userDescription')[:80]}...\n"
            response += "\n"
        
        if len(terms) > 10:
            response += f"... and {len(terms) - 10} more terms. You can search for specific terms to get more details."
        
        return response
        
    except Exception as e:
        return f"Sorry, I encountered an error while listing terms: {str(e)}"

def handle_find_assets(term_name: str, atlan_client: AtlanSDKClient) -> str:
    """Handle find assets intent"""
    try:
        # First find the term
        terms = atlan_client.search_terms_by_name(term_name)
        
        if not terms:
            return f"I couldn't find a glossary term called '{term_name}' to search for related assets."
        
        term = terms[0]
        term_guid = term.get('guid')
        term_name_actual = term.get('name', 'Unknown')
        
        assets = atlan_client.find_assets_with_term(term_guid, term_name_actual)
        
        if not assets:
            return f"I found the term '{term_name_actual}' but couldn't find any assets linked to it in the catalog."
        
        response = f"Here are the assets related to **{term_name_actual}**:\n\n"
        
        for i, asset in enumerate(assets[:5], 1):
            response += f"{i}. **{asset.get('name', 'Unknown')}** ({asset.get('typeName', 'Unknown')})\n"
            if asset.get('description'):
                response += f"   {asset.get('description')[:100]}...\n"
            if asset.get('userDescription'):
                response += f"   {asset.get('userDescription')[:100]}...\n"
            response += "\n"
        
        if len(assets) > 5:
            response += f"... and {len(assets) - 5} more assets."
        
        return response
        
    except Exception as e:
        return f"Sorry, I encountered an error while searching for assets: {str(e)}"

def handle_unknown_intent(user_input: str) -> str:
    """Handle unknown intent"""
    return f"I'm not sure how to help with '{user_input}'. You can:\n\n" \
           f"• Ask me to define a term (e.g., 'Define Customer Acquisition Cost')\n" \
           f"• Ask me to list all terms (e.g., 'List all terms')\n" \
           f"• Ask me to find assets related to a term (e.g., 'Show me assets for Revenue')\n" \
           f"• Or just ask me anything about the data catalog!"

# Main app interface
st.title("💬 Conversational Atlan Data Assistant")
st.markdown("Talk to your data catalog naturally - I'll understand what you want and get the information directly from Atlan")

# Initialize Atlan client
atlan_client = AtlanSDKClient()

# Sidebar
with st.sidebar:
    st.header("💡 How to use")
    st.markdown("""
    **Just talk naturally!** Try:
    
    • "Define Customer Acquisition Cost"
    • "What is CAC?"
    • "List all terms"
    • "Show me assets for Revenue"
    • "Tell me about ARR"
    """)
    
    st.markdown("---")
    
    # Test Atlan connection
    if atlan_client.test_connection():
        st.markdown("**Status:** 🟢 Connected to Atlan")
    else:
        st.markdown("**Status:** 🔴 Atlan connection failed")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.search_results = []
        st.session_state.current_context = {}
        st.rerun()

# Main chat interface
st.header("Chat with your data")

# Chat input
user_input = st.chat_input("Ask me anything about your data catalog...")

# Process user input
if user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Analyze intent
    intent_analysis = analyze_intent(user_input)
    
    # Generate response based on intent
    if intent_analysis["intent"] == "define_term":
        entities = intent_analysis.get("entities", [])
        if entities:
            response = handle_define_term(entities[0], atlan_client)
        else:
            response = "I couldn't identify which term you want me to define. Could you please specify the term name?"
    
    elif intent_analysis["intent"] == "list_terms":
        response = handle_list_terms(atlan_client)
    
    elif intent_analysis["intent"] == "find_assets":
        entities = intent_analysis.get("entities", [])
        if entities:
            response = handle_find_assets(entities[0], atlan_client)
        else:
            response = "I couldn't identify which term you want me to find assets for. Could you please specify the term name?"
    
    else:
        response = handle_unknown_intent(user_input)
    
    # Add assistant response to chat
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Footer
st.markdown("---")
st.markdown("*Powered by Atlan - Direct data catalog access*") 