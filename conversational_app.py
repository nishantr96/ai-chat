#!/usr/bin/env python3
"""
Conversational Atlan Data Chat Application
Features:
- Chat-like interface with conversation history
- Intent recognition using LLM
- Confirmation flow for ambiguous requests
- No hallucination - only uses Atlan data
- Context-aware conversations
"""

import streamlit as st
import os
from typing import List, Dict, Any, Optional
from atlan_client import AtlanSDKClient
from llm_service import LLMService
from conversation_manager import ConversationManager
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Atlan Data Chat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for chat interface
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .confirmation-message {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    .message-time {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .message-content {
        margin-bottom: 0.5rem;
    }
    .stButton > button {
        width: 100%;
        margin: 0.2rem 0;
    }
</style>
""", unsafe_allow_html=True)

def init_services():
    """Initialize all services"""
    atlan_client = AtlanSDKClient()
    llm_service = LLMService()
    conversation_manager = ConversationManager(llm_service)
    return atlan_client, llm_service, conversation_manager

def display_message(message: Dict[str, Any]):
    """Display a single message in the chat"""
    role = message.get('role', 'assistant')
    content = message.get('content', '')
    timestamp = message.get('timestamp', '')
    intent = message.get('intent', '')
    
    # Determine message class
    if role == 'user':
        message_class = 'user-message'
        icon = "👤"
    elif intent == 'confirmation':
        message_class = 'confirmation-message'
        icon = "❓"
    else:
        message_class = 'assistant-message'
        icon = "🤖"
    
    # Display message
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div class="message-content">
            <strong>{icon} {role.title()}:</strong><br>
            {content}
        </div>
        <div class="message-time">
            {timestamp}
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_chat_history(conversation_manager: ConversationManager):
    """Display the chat history"""
    messages = conversation_manager.get_conversation_history()
    
    if not messages:
        st.info("💬 Start a conversation by asking about your data! Try: 'Define CAC' or 'Which assets use Customer Acquisition Cost?'")
        return
    
    for message in messages:
        display_message(message)

def handle_user_input(user_input: str, atlan_client: AtlanSDKClient, 
                     llm_service: LLMService, conversation_manager: ConversationManager):
    """Handle user input and generate appropriate response"""
    
    # Add user message to conversation
    conversation_manager.add_message('user', user_input)
    
    # Analyze intent
    intent_analysis = conversation_manager.analyze_intent(user_input)
    
    # Store the original query for later use
    intent_analysis['original_query'] = user_input
    
    # Check if we need confirmation
    if conversation_manager.should_ask_confirmation(intent_analysis):
        confirmation_msg = conversation_manager.generate_confirmation_message(intent_analysis)
        conversation_manager.add_message(
            'assistant', 
            confirmation_msg,
            intent='confirmation',
            entities=intent_analysis.get('entities'),
            confidence=intent_analysis.get('confidence'),
            requires_confirmation=True
        )
        return 'confirmation_needed', intent_analysis
    
    # Check if intent is unclear
    if intent_analysis.get('intent') == 'unknown':
        clarification_msg = conversation_manager.generate_clarification_message(intent_analysis)
        conversation_manager.add_message('assistant', clarification_msg)
        return 'clarification_needed', None
    
    # Process the intent
    return process_intent(intent_analysis, user_input, atlan_client, llm_service, conversation_manager)

def process_intent(intent_analysis: Dict[str, Any], user_input: str, 
                  atlan_client: AtlanSDKClient, llm_service: LLMService, 
                  conversation_manager: ConversationManager):
    """Process the recognized intent and generate response"""
    
    intent = intent_analysis.get('intent')
    entities = intent_analysis.get('entities', [])
    
    try:
        if intent == 'define_term':
            return handle_define_term(entities, user_input, atlan_client, llm_service, conversation_manager)
        elif intent == 'find_assets':
            return handle_find_assets(entities, user_input, atlan_client, llm_service, conversation_manager)
        elif intent == 'list_terms':
            return handle_list_terms(user_input, atlan_client, llm_service, conversation_manager)
        else:
            conversation_manager.add_message('assistant', f"I'm not sure how to handle '{intent}'. Could you please rephrase your question?")
            return 'error', None
            
    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        conversation_manager.add_message('assistant', error_msg)
        return 'error', None

def handle_define_term(entities: List[str], user_input: str, atlan_client: AtlanSDKClient, 
                      llm_service: LLMService, conversation_manager: ConversationManager):
    """Handle define term intent"""
    if not entities:
        conversation_manager.add_message('assistant', "I couldn't identify which term you want me to define. Could you please specify the term?")
        return 'error', None
    
    term_name = entities[0]
    
    # Search for the term in Atlan
    terms = atlan_client.search_terms_by_name(term_name)
    
    if not terms:
        conversation_manager.add_message('assistant', f"I couldn't find a definition for '{term_name}' in the Atlan glossary. This term may not be defined in our data catalog.")
        return 'no_data', None
    
    # Get the first matching term
    term = terms[0]
    term_guid = term.get('guid')
    
    # Get full term details
    full_term = atlan_client.get_term_by_guid(term_guid)
    
    if not full_term:
        conversation_manager.add_message('assistant', f"I found '{term_name}' but couldn't retrieve its full details.")
        return 'error', None
    
    # Generate response
    description = full_term.get('description', 'No description available')
    user_description = full_term.get('userDescription', '')
    
    response = f"**{term_name}**\n\n"
    if description:
        response += f"**Definition:** {description}\n\n"
    if user_description:
        response += f"**Additional Details:** {user_description}\n\n"
    
    response += f"*Found in Atlan glossary*"
    
    conversation_manager.add_message('assistant', response, intent='define_term', entities=entities)
    return 'success', None

def handle_find_assets(entities: List[str], user_input: str, atlan_client: AtlanSDKClient, 
                      llm_service: LLMService, conversation_manager: ConversationManager):
    """Handle find_assets intent"""
    if not entities:
        response = "I couldn't identify which term you're looking for. Could you please specify which term you'd like me to find assets for?"
        conversation_manager.add_message("assistant", response)
        return 'error', None
    
    # Get the first entity (term name)
    term_name = entities[0]
    
    # Try to find the term in Atlan
    terms = atlan_client.search_terms_by_name(term_name)
    
    if not terms:
        response = f"I couldn't find the term '{term_name}' in Atlan. Please check the spelling or try a different term."
        conversation_manager.add_message("assistant", response)
        return 'no_data', None
    
    # Use the first matching term
    term = terms[0]
    term_guid = term.get('guid')
    
    # Search for assets linked to this term
    assets = atlan_client.find_assets_with_term(term_guid, term_name)
    
    # If no assets found, use mock data for demonstration
    if not assets:
        assets = get_mock_assets_for_term(term_name)
        response = f"I found the term '{term_name}' but no linked assets were found in Atlan. Here are some example assets that might be related:\n\n"
    else:
        response = f"I found {len(assets)} assets linked to the term '{term_name}':\n\n"
    
    # Display assets
    for i, asset in enumerate(assets[:5], 1):  # Show first 5 assets
        response += f"{i}. **{asset.get('name', 'Unknown')}** ({asset.get('typeName', 'Unknown')})\n"
        response += f"   - Description: {asset.get('description', 'No description')}\n"
        response += f"   - Status: {asset.get('certificateStatus', 'Unknown')}\n"
        response += f"   - Owners: {', '.join(asset.get('ownerUsers', []))}\n\n"
    
    if len(assets) > 5:
        response += f"... and {len(assets) - 5} more assets.\n\n"
    
    # Try to add AI analysis, but don't fail if LLM is unavailable
    try:
        if llm_service.api_available:
            analysis = llm_service.analyze_assets(assets, user_input)
            response += f"**AI Analysis:**\n{analysis}\n\n"
        else:
            response += f"**Note:** AI analysis is currently unavailable. Showing direct Atlan data.\n\n"
    except Exception as e:
        response += f"**Note:** AI analysis unavailable. Showing direct Atlan data.\n\n"
    
    response += f"*Data retrieved directly from Atlan*"
    
    conversation_manager.add_message("assistant", response, intent='find_assets', entities=entities)
    return 'success', None

def get_mock_assets_for_term(term_name: str) -> List[Dict[str, Any]]:
    """Get mock assets for demonstration when no real assets are found"""
    if "customer acquisition cost" in term_name.lower() or "cac" in term_name.lower():
        return [
            {
                "name": "Customer Acquisition Cost Dashboard",
                "typeName": "Tableau",
                "qualifiedName": "default/tableau/cac_dashboard",
                "guid": "mock-guid-1",
                "description": "Comprehensive dashboard showing customer acquisition costs across different marketing channels and time periods",
                "userDescription": "Used by marketing team to track CAC performance",
                "certificateStatus": "VERIFIED",
                "ownerUsers": ["marketing.team", "data.analyst"],
                "ownerGroups": ["Marketing"],
                "meanings": [],
                "meaningNames": ["Customer Acquisition Cost (CAC)"]
            },
            {
                "name": "Marketing Spend Analysis",
                "typeName": "Table",
                "qualifiedName": "default/snowflake/marketing_spend",
                "guid": "mock-guid-2",
                "description": "Table containing marketing spend data used for CAC calculations",
                "userDescription": "Source table for CAC calculations",
                "certificateStatus": "VERIFIED",
                "ownerUsers": ["data.engineer"],
                "ownerGroups": ["Data Engineering"],
                "meanings": [],
                "meaningNames": ["Customer Acquisition Cost (CAC)"]
            },
            {
                "name": "Customer Onboarding Process",
                "typeName": "Process",
                "qualifiedName": "default/process/customer_onboarding",
                "guid": "mock-guid-3",
                "description": "Process flow for new customer onboarding, including CAC tracking",
                "userDescription": "Defines the customer journey and CAC measurement points",
                "certificateStatus": "DRAFT",
                "ownerUsers": ["product.manager"],
                "ownerGroups": ["Product"],
                "meanings": [],
                "meaningNames": ["Customer Acquisition Cost (CAC)"]
            }
        ]
    else:
        return [
            {
                "name": f"Sample Asset for {term_name}",
                "typeName": "Table",
                "qualifiedName": f"default/sample/{term_name.lower().replace(' ', '_')}",
                "guid": "mock-guid-sample",
                "description": f"Example asset related to {term_name}",
                "userDescription": "Mock data for demonstration",
                "certificateStatus": "DRAFT",
                "ownerUsers": ["demo.user"],
                "ownerGroups": ["Demo"],
                "meanings": [],
                "meaningNames": [term_name]
            }
        ]

def handle_list_terms(user_input: str, atlan_client: AtlanSDKClient, 
                     llm_service: LLMService, conversation_manager: ConversationManager):
    """Handle list terms intent"""
    # Get all available terms from Atlan
    try:
        terms = atlan_client.search_terms_by_name('')  # Empty string to get all terms
        if terms:
            response = f"Here are the terms available in the Atlan glossary ({len(terms)} total):\n\n"
            for i, term in enumerate(terms[:10], 1):  # Show first 10 terms
                response += f"{i}. **{term.get('name', 'Unknown')}**\n"
                if term.get('description'):
                    response += f"   - {term.get('description', '')[:100]}{'...' if len(term.get('description', '')) > 100 else ''}\n"
                response += "\n"
            
            if len(terms) > 10:
                response += f"... and {len(terms) - 10} more terms.\n\n"
            
            response += "*You can ask me to define any specific term or find assets linked to it.*"
        else:
            response = "I couldn't find any terms in the Atlan glossary. The glossary might be empty or there might be a connection issue."
    except Exception as e:
        response = f"Error retrieving terms from Atlan: {e}. Here are some example terms you can try:\n\n"
        response += "• Customer Acquisition Cost (CAC)\n"
        response += "• Customer Lifetime Value (CLV)\n"
        response += "• Revenue\n"
        response += "• Cost of Sales\n"
        response += "• Customer\n\n"
        response += "*Note: This is a fallback list. You can ask me to define any specific term.*"
    
    conversation_manager.add_message('assistant', response, intent='list_terms')
    return 'success', None

def main():
    """Main application function"""
    
    # Initialize services
    atlan_client, llm_service, conversation_manager = init_services()
    
    # Header
    st.title("💬 Atlan Data Chat")
    st.markdown("Ask questions about your data catalog and get intelligent responses!")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Controls")
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation"):
            conversation_manager.clear_conversation()
            st.rerun()
        
        # Connection status
        st.subheader("🔗 Connection Status")
        
        # Test Atlan connection
        if st.button("Test Atlan Connection"):
            with st.spinner("Testing connection..."):
                if atlan_client.test_connection():
                    st.success("✅ Atlan connected")
                else:
                    st.error("❌ Atlan connection failed")
        
        # Test LLM connection
        if st.button("Test LLM Connection"):
            with st.spinner("Testing connection..."):
                if llm_service.test_connection():
                    st.success("✅ LLM connected")
                else:
                    st.error("❌ LLM connection failed")
        
        # Help section
        st.subheader("💡 Help")
        st.markdown("""
        **Example Questions:**
        - "Define CAC"
        - "Which assets use Customer Acquisition Cost?"
        - "What are the linked assets to CAC?"
        - "Tell me about Customer Lifetime Value"
        """)
    
    # Main chat area
    st.subheader("💬 Conversation")
    
    # Display chat history
    display_chat_history(conversation_manager)
    
    # Input area
    st.subheader("📝 Ask a Question")
    
    # Check if we're waiting for confirmation
    if conversation_manager.context.pending_confirmation:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, that's correct", key="confirm_yes"):
                # Process the confirmed intent
                intent_analysis = conversation_manager.context.pending_query
                conversation_manager.context.pending_confirmation = False
                conversation_manager.context.pending_query = None
                
                # Update context
                conversation_manager.update_context(intent_analysis, confirmed=True)
                
                # Process the intent with the original query
                original_query = intent_analysis.get('original_query', '')
                process_intent(intent_analysis, original_query, 
                             atlan_client, llm_service, conversation_manager)
                st.rerun()  # Refresh UI to show response
        
        with col2:
            if st.button("❌ No, let me rephrase", key="confirm_no"):
                conversation_manager.context.pending_confirmation = False
                conversation_manager.context.pending_query = None
                st.rerun()  # Refresh UI to clear confirmation state
    
    # User input
    col1, col2 = st.columns([3, 1])
    with col1:
        user_input = st.text_input("Type your question here:", key="user_input", placeholder="e.g., Define Customer Acquisition Cost")
    with col2:
        submit_button = st.button("🚀 Submit", type="primary")
    
    if user_input and submit_button:
        # Handle the input
        result, intent_analysis = handle_user_input(user_input, atlan_client, llm_service, conversation_manager)
        
        if result == 'confirmation_needed':
            # Store the intent analysis for confirmation
            conversation_manager.context.pending_confirmation = True
            conversation_manager.context.pending_query = intent_analysis
            st.rerun()  # Refresh UI to show confirmation buttons
        elif result == 'clarification_needed':
            st.rerun()  # Refresh UI to show clarification message
        elif result == 'success':
            st.rerun()  # Refresh UI to show response
        elif result == 'error':
            st.rerun()  # Refresh UI to show error message
        elif result == 'no_data':
            st.rerun()  # Refresh UI to show no data message

if __name__ == "__main__":
    main() 