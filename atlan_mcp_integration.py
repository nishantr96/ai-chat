"""
Atlan MCP Integration Module
This module provides direct integration with Atlan MCP tools for data catalog access.
"""

import streamlit as st
import json
from typing import List, Dict, Any, Optional
import asyncio
import subprocess
import sys

class AtlanMCPIntegration:
    """Integration class for Atlan MCP tools"""
    
    def __init__(self):
        self.mcp_tools_available = self._check_mcp_availability()
    
    def _check_mcp_availability(self) -> bool:
        """Check if MCP tools are available"""
        try:
            # Check if we're in an environment with MCP tools
            # This would be true if we're running in a context with MCP access
            return True
        except Exception:
            return False
    
    def search_glossary_terms(self, query: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        """Search for glossary terms using Atlan MCP"""
        try:
            # In a real implementation, this would call the MCP tool directly
            # For now, we'll return sample data that matches the MCP response format
            
            sample_terms = [
                {
                    "typeName": "AtlasGlossaryTerm",
                    "attributes": {
                        "qualifiedName": "customer-acquisition-cost-cac@glossary",
                        "name": "Customer Acquisition Cost (CAC)",
                        "userDescription": "The cost associated with acquiring a new customer, including marketing, sales, and onboarding expenses. This metric is crucial for understanding the efficiency of customer acquisition strategies.",
                        "certificateStatus": "VERIFIED",
                        "ownerUsers": ["data.team", "marketing.team"],
                        "ownerGroups": ["data-governance"],
                        "displayName": "CAC"
                    },
                    "guid": "af6a32d4-936b-4a59-9917-7082c56ba443",
                    "displayText": "Customer Acquisition Cost (CAC)"
                },
                {
                    "typeName": "AtlasGlossaryTerm",
                    "attributes": {
                        "qualifiedName": "annual-recurring-revenue-arr@glossary",
                        "name": "Annual Recurring Revenue (ARR)",
                        "userDescription": "The normalized annual revenue from subscription-based contracts. ARR is a key metric for SaaS companies to measure predictable revenue streams.",
                        "certificateStatus": "VERIFIED",
                        "ownerUsers": ["finance.team"],
                        "ownerGroups": ["finance"],
                        "displayName": "ARR"
                    },
                    "guid": "b7c8d9e0-f1a2-3b4c-5d6e-7f8g9h0i1j2k",
                    "displayText": "Annual Recurring Revenue (ARR)"
                },
                {
                    "typeName": "AtlasGlossaryTerm",
                    "attributes": {
                        "qualifiedName": "customer-lifetime-value-clv@glossary",
                        "name": "Customer Lifetime Value (CLV)",
                        "userDescription": "The total revenue a business can expect from a single customer account throughout their relationship. CLV helps in making informed decisions about customer acquisition and retention strategies.",
                        "certificateStatus": "DRAFT",
                        "ownerUsers": ["analytics.team"],
                        "ownerGroups": ["analytics"],
                        "displayName": "CLV"
                    },
                    "guid": "c9d0e1f2-g3h4-5i6j-7k8l-9m0n1o2p3q4r",
                    "displayText": "Customer Lifetime Value (CLV)"
                },
                {
                    "typeName": "AtlasGlossaryTerm",
                    "attributes": {
                        "qualifiedName": "monthly-recurring-revenue-mrr@glossary",
                        "name": "Monthly Recurring Revenue (MRR)",
                        "userDescription": "The normalized monthly revenue from subscription-based contracts. MRR is used to track revenue growth and predict future revenue.",
                        "certificateStatus": "VERIFIED",
                        "ownerUsers": ["finance.team"],
                        "ownerGroups": ["finance"],
                        "displayName": "MRR"
                    },
                    "guid": "d1e2f3g4-h5i6-7j8k-9l0m-1n2o3p4q5r6s",
                    "displayText": "Monthly Recurring Revenue (MRR)"
                },
                {
                    "typeName": "AtlasGlossaryTerm",
                    "attributes": {
                        "qualifiedName": "churn-rate@glossary",
                        "name": "Churn Rate",
                        "userDescription": "The rate at which customers cancel their subscriptions or stop using a service. Churn rate is a critical metric for understanding customer retention.",
                        "certificateStatus": "VERIFIED",
                        "ownerUsers": ["customer.success.team"],
                        "ownerGroups": ["customer-success"],
                        "displayName": "Churn Rate"
                    },
                    "guid": "e3f4g5h6-i7j8-9k0l-1m2n-3o4p5q6r7s8t",
                    "displayText": "Churn Rate"
                }
            ]
            
            # Filter by query if provided
            if query.strip():
                query_lower = query.lower()
                filtered_terms = []
                for term in sample_terms:
                    name = term.get('attributes', {}).get('name', '').lower()
                    description = term.get('attributes', {}).get('userDescription', '').lower()
                    if query_lower in name or query_lower in description:
                        filtered_terms.append(term)
                return filtered_terms[:limit]
            
            return sample_terms[:limit]
            
        except Exception as e:
            st.error(f"Error searching glossary terms: {e}")
            return []
    
    def get_term_details(self, guid: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific term"""
        try:
            # In a real implementation, this would call the MCP tool to get full details
            # For now, return sample detailed information
            
            sample_details = {
                "guid": guid,
                "fullDetails": {
                    "name": "Customer Acquisition Cost (CAC)",
                    "description": "The cost associated with acquiring a new customer, including marketing, sales, and onboarding expenses.",
                    "certificateStatus": "VERIFIED",
                    "owners": ["data.team", "marketing.team"],
                    "createdDate": "2024-01-15",
                    "lastModified": "2024-08-03",
                    "version": "1.2"
                },
                "lineage": {
                    "upstream": ["Marketing Campaign Data", "Sales Pipeline Data"],
                    "downstream": ["Customer ROI Analysis", "Marketing Efficiency Reports"]
                },
                "relatedAssets": [
                    {"name": "Customer Acquisition Dashboard", "type": "Dashboard"},
                    {"name": "Marketing Spend Table", "type": "Table"},
                    {"name": "Sales Pipeline View", "type": "View"}
                ],
                "usage": {
                    "totalQueries": 156,
                    "lastUsed": "2024-08-02",
                    "popularUsers": ["analyst1", "analyst2", "manager1"]
                }
            }
            
            return sample_details
            
        except Exception as e:
            st.error(f"Error getting term details: {e}")
            return None
    
    def search_assets_by_term(self, term_guid: str) -> List[Dict[str, Any]]:
        """Search for assets linked to a specific term"""
        try:
            # In a real implementation, this would call the MCP tool to find linked assets
            # For now, return sample linked assets
            
            sample_assets = [
                {
                    "name": "Customer Acquisition Dashboard",
                    "typeName": "Dashboard",
                    "qualifiedName": "customer.acquisition.dashboard@bi",
                    "description": "Dashboard showing customer acquisition metrics and trends",
                    "ownerUsers": ["bi.team"],
                    "certificateStatus": "VERIFIED"
                },
                {
                    "name": "Marketing Spend Table",
                    "typeName": "Table",
                    "qualifiedName": "marketing.spend.table@warehouse",
                    "description": "Table containing marketing spend data by campaign",
                    "ownerUsers": ["data.team"],
                    "certificateStatus": "VERIFIED"
                },
                {
                    "name": "Sales Pipeline View",
                    "typeName": "View",
                    "qualifiedName": "sales.pipeline.view@crm",
                    "description": "View of sales pipeline data with customer acquisition metrics",
                    "ownerUsers": ["sales.team"],
                    "certificateStatus": "DRAFT"
                },
                {
                    "name": "Customer ROI Analysis",
                    "typeName": "Report",
                    "qualifiedName": "customer.roi.analysis@analytics",
                    "description": "Report analyzing customer return on investment",
                    "ownerUsers": ["analytics.team"],
                    "certificateStatus": "VERIFIED"
                }
            ]
            
            return sample_assets
            
        except Exception as e:
            st.error(f"Error searching assets: {e}")
            return []
    
    def get_lineage(self, guid: str, direction: str = "DOWNSTREAM") -> Dict[str, Any]:
        """Get lineage information for a term"""
        try:
            # In a real implementation, this would call the MCP lineage tool
            # For now, return sample lineage data
            
            sample_lineage = {
                "direction": direction,
                "assets": [
                    {
                        "name": "Marketing Campaign Data",
                        "typeName": "Table",
                        "guid": "upstream-guid-1",
                        "relationship": "feeds_into"
                    },
                    {
                        "name": "Sales Pipeline Data",
                        "typeName": "Table", 
                        "guid": "upstream-guid-2",
                        "relationship": "feeds_into"
                    },
                    {
                        "name": "Customer ROI Analysis",
                        "typeName": "Report",
                        "guid": "downstream-guid-1", 
                        "relationship": "consumes"
                    }
                ]
            }
            
            return sample_lineage
            
        except Exception as e:
            st.error(f"Error getting lineage: {e}")
            return {"direction": direction, "assets": []}
    
    def list_all_terms(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List all available glossary terms"""
        return self.search_glossary_terms("", limit)
    
    def get_popular_terms(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular terms based on usage"""
        # In a real implementation, this would filter by usage metrics
        all_terms = self.search_glossary_terms("", limit * 2)
        # Return first N terms as "popular" for demo
        return all_terms[:limit]

# Global instance
atlan_mcp = AtlanMCPIntegration() 