import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from datetime import datetime

from atlan_client import AtlanClient
from query_processor import QueryProcessor
from chart_generator import ChartGenerator
from llm_service import LLMService

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Data Chat Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .stButton > button {
        width: 100%;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Data Chat Interface</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'query_processor' not in st.session_state:
        try:
            atlan_client = AtlanClient()
            st.session_state.query_processor = QueryProcessor(atlan_client)
            st.session_state.atlan_available = atlan_client.is_connected()
        except Exception as e:
            st.error(f"Failed to initialize Atlan client: {str(e)}")
            st.session_state.query_processor = None
            st.session_state.atlan_available = False
    
    if 'llm_service' not in st.session_state:
        try:
            st.session_state.llm_service = LLMService()
            st.session_state.llm_available = True
        except ValueError as e:
            # Handle missing API key specifically
            st.session_state.llm_service = None
            st.session_state.llm_available = False
            # Don't show error here, we'll show it in the sidebar
        except Exception as e:
            st.error(f"Failed to initialize LLM service: {str(e)}")
            st.session_state.llm_service = None
            st.session_state.llm_available = False
    
    # Initialize conversation context
    if 'conversation_context' not in st.session_state:
        st.session_state.conversation_context = {
            'last_discussed_term': None,
            'previous_queries': [],
            'session_start_time': datetime.now().isoformat()
        }
    
    if 'pending_clarification' not in st.session_state:
        st.session_state.pending_clarification = None
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Settings & Options")
        
        # Connection status
        st.subheader("📡 Connection Status")
        if st.session_state.atlan_available:
            st.success("✅ Connected to Atlan")
        else:
            st.error("❌ Not connected to Atlan")
        
        # LLM Status
        st.subheader("🧠 LLM Status")
        if st.session_state.llm_available:
            st.success("✅ LLM Service Active")
        else:
            st.warning("⚠️ LLM Service Unavailable")
            st.info("To enable LLM features, please:")
            st.info("1. Update your .env file with a valid OPENAI_API_KEY")
            st.info("2. Restart the application")
            st.info("The app will work with pattern-based intent detection instead.")
        
        # Conversation Context
        st.subheader("💬 Conversation Context")
        if st.session_state.conversation_context.get('last_discussed_term'):
            st.info(f"**Last discussed term:** {st.session_state.conversation_context['last_discussed_term']}")
        else:
            st.info("No term discussed yet")
        
        if st.session_state.conversation_context.get('previous_queries'):
            st.info(f"**Recent queries:** {len(st.session_state.conversation_context['previous_queries'])}")
            with st.expander("View recent queries"):
                for i, query in enumerate(st.session_state.conversation_context['previous_queries'][-3:], 1):
                    st.write(f"{i}. {query}")
        
        # Clear context button
        if st.button("🗑️ Clear Context", help="Clear conversation context and start fresh"):
            st.session_state.conversation_context = {
                'last_discussed_term': None,
                'previous_queries': [],
                'session_start_time': datetime.now().isoformat()
            }
            st.rerun()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.pending_clarification = None
            st.session_state.conversation_context = {
                'last_discussed_term': None,
                'previous_queries': [],
                'session_start_time': datetime.now().isoformat()
            }
            st.rerun()
        
        # Example queries
        st.subheader("💡 Example Queries")
        example_queries = [
            "Define Customer Acquisition Cost",
            "Which assets use Customer Acquisition Cost?",
            "Give me a bar chart by connector type of assets that use Customer Acquisition Cost",
            "What glossary terms do you have?",
            "Find tables related to revenue data"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{query}"):
                st.session_state.messages.append({"role": "user", "content": query})
                st.rerun()
    
    # Main chat area
    st.subheader("💬 Chat with Your Data")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                # Display assistant message
                st.write(message["content"])
                
                # Display chart if present
                if "chart" in message:
                    st.plotly_chart(message["chart"], use_container_width=True)
                
                # Display data if present
                if "data" in message:
                    st.dataframe(message["data"])
            else:
                # Display user message
                st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your data..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(prompt)
        
        # Check if this is a response to intent clarification
        if st.session_state.pending_clarification:
            # Handle clarification response
            clarification_context = st.session_state.pending_clarification
            original_intent = clarification_context.get('original_intent')
            original_term = clarification_context.get('original_term')
            
            # Clear the pending clarification
            st.session_state.pending_clarification = None
            
            # Process the clarification response with context
            if original_intent == 'definition':
                response = st.session_state.query_processor.handle_clarification_response(
                    original_term, prompt, original_intent, st.session_state.conversation_context
                )
            else:
                response = {"content": "I'm not sure how to handle that clarification. Please try asking your question again."}
        else:
            # Update conversation context
            st.session_state.conversation_context['previous_queries'].append(prompt)
            if len(st.session_state.conversation_context['previous_queries']) > 5:
                st.session_state.conversation_context['previous_queries'].pop(0)
            
            # Process the query with context
            response = st.session_state.query_processor.process_query(
                prompt, 
                context=st.session_state.conversation_context
            )
            
            # Update context with any new information from the response
            if isinstance(response, dict) and 'context_updates' in response:
                for key, value in response['context_updates'].items():
                    st.session_state.conversation_context[key] = value
        
        # Handle the response format
        if isinstance(response, dict):
            response_content = response.get("content", "No response generated")
            requires_clarification = response.get("requires_clarification", False)
        elif isinstance(response, tuple):
            response_content, requires_clarification = response
        else:
            response_content = str(response)
            requires_clarification = False
        
        # Store clarification context if needed
        if requires_clarification:
            st.session_state.pending_clarification = {
                "original_intent": response.get("original_intent", "definition"),
                "original_term": response.get("original_term", "")
            }
        
        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": response_content})
        
        # Add chart if present
        if "chart" in response:
            st.session_state.messages[-1]["chart"] = response["chart"]
        
        # Add data if present
        if "data" in response:
            st.session_state.messages[-1]["data"] = response["data"]
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.write(response_content)
            
            # Display chart if present
            if "chart" in response:
                st.plotly_chart(response["chart"], use_container_width=True)
            
            # Display data if present
            if "data" in response:
                st.dataframe(response["data"])
        
        # Rerun to update the chat
        st.rerun()

if __name__ == "__main__":
    main() 