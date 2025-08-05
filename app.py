import streamlit as st
import os
from atlan_client import AtlanSDKClient
from llm_service import LLMService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Atlan Data Chat",
    page_icon="🔍",
    layout="wide"
)

# Mock data for CAC assets (fallback when Atlan API fails)
MOCK_CAC_ASSETS = [
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

# Initialize services
@st.cache_resource
def init_services():
    atlan_client = AtlanSDKClient()
    llm_service = LLMService()
    return atlan_client, llm_service

def get_cac_assets(atlan_client):
    """Get CAC assets, using mock data if Atlan API fails"""
    try:
        CAC_TERM_GUID = "af6a32d4-936b-4a59-9917-7082c56ba443"
        CAC_TERM_NAME = "Customer Acquisition Cost (CAC)"
        
        assets = atlan_client.find_assets_with_term(CAC_TERM_GUID, CAC_TERM_NAME)
        if assets:
            return assets, "live"
        else:
            return MOCK_CAC_ASSETS, "mock"
    except Exception as e:
        st.warning(f"Atlan API failed: {e}. Using mock data for demonstration.")
        return MOCK_CAC_ASSETS, "mock"

def main():
    st.title("🔍 Atlan Data Chat Interface")
    st.markdown("Ask questions about your data assets in Atlan")
    
    # Initialize services
    atlan_client, llm_service = init_services()
    
    # Test connections
    col1, col2 = st.columns(2)
    
    with col1:
        atlan_ok = atlan_client.test_connection()
        if atlan_ok:
            st.success("✅ Atlan API Connected")
        else:
            st.warning("⚠️ Atlan API Unavailable (using mock data)")
    
    with col2:
        try:
            llm_ok = llm_service.test_connection()
            if llm_ok:
                st.success("✅ OpenAI API Connected")
            else:
                st.error("❌ OpenAI API Connection Failed")
        except Exception as e:
            st.error(f"❌ OpenAI API Error: {e}")
            llm_ok = False
    
    st.divider()
    
    # User input
    user_query = st.text_input(
        "Ask a question about Customer Acquisition Cost:",
        placeholder="e.g., Which assets use this term? What tables are linked to CAC?"
    )
    
    if st.button("🔍 Search & Analyze", type="primary"):
        if user_query:
            with st.spinner("Searching Atlan and analyzing with AI..."):
                # Get assets (live or mock)
                assets, data_source = get_cac_assets(atlan_client)
                
                # Display data source info
                if data_source == "mock":
                    st.info("📊 Using mock data for demonstration (Atlan API unavailable)")
                else:
                    st.success("📊 Using live Atlan data")
                
                # Display results
                st.subheader(f"📊 Found {len(assets)} Assets")
                
                if assets:
                    # Show asset details
                    for i, asset in enumerate(assets, 1):
                        with st.expander(f"{i}. {asset['name']} ({asset['typeName']})"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Description:** {asset['description']}")
                                st.write(f"**Status:** {asset['certificateStatus']}")
                                st.write(f"**Owners:** {', '.join(asset['ownerUsers'])}")
                            with col2:
                                st.write(f"**GUID:** {asset['guid']}")
                                st.write(f"**Meanings:** {', '.join(asset['meaningNames'])}")
                    
                    st.divider()
                    
                    # LLM Analysis
                    if llm_ok:
                        st.subheader("🤖 AI Analysis")
                        try:
                            analysis = llm_service.analyze_assets(assets, user_query)
                            st.write(analysis)
                        except Exception as e:
                            st.error(f"LLM analysis failed: {e}")
                            st.info("Here's a summary of the assets found:")
                            for asset in assets:
                                st.write(f"• **{asset['name']}** ({asset['typeName']}): {asset['description']}")
                    else:
                        st.subheader("📋 Asset Summary")
                        st.info("OpenAI API unavailable. Here's a summary of the assets found:")
                        for asset in assets:
                            st.write(f"• **{asset['name']}** ({asset['typeName']}): {asset['description']}")
                    
                else:
                    st.warning("No assets found for Customer Acquisition Cost (CAC)")
        else:
            st.warning("Please enter a question to search and analyze.")

if __name__ == "__main__":
    main() 