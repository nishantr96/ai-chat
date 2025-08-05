import re
from typing import Dict, Any, List, Optional, Tuple
import json
import os

from atlan_client import AtlanClient
from snowflake_client import SnowflakeClient
from chart_generator import ChartGenerator
from llm_service import LLMService


class QueryProcessor:
    """Process user queries and route to appropriate handlers with optional LLM enhancement."""
    
    def __init__(self, atlan_client: AtlanClient):
        """Initialize the query processor."""
        self.atlan_client = atlan_client
        
        # Try to initialize LLM service, but don't fail if it's not available
        try:
            from llm_service import LLMService
            self.llm_service = LLMService()
            self.llm_available = True
            print("✅ LLM Service initialized successfully")
        except Exception as e:
            print(f"⚠️ LLM Service not available: {str(e)}")
            self.llm_service = None
            self.llm_available = False
        
        # Intent patterns for classification
        self.patterns = {
            'definition': [
                r'\b(?:define|definition|what is|how is|meaning of|explain|tell me about)\b',
                r'\b(?:what does|how does|describe|elaborate on)\b'
            ],
            'asset_usage': [
                r'\b(?:which assets use|what assets use|find assets|search assets)\b',
                r'\b(?:what uses|which uses|assets that use|tables that use)\b',
                r'\b(?:columns using|tables using|views using|queries using)\b',
                r'\b(?:where is.*used|how is.*used|in which.*is.*used)\b',
                # Context-aware patterns for follow-up questions
                r'\b(?:assets use|uses this|uses that|uses it)\b',
                r'\b(?:what.*assets|which.*assets|find.*assets)\b'
            ],
            'list_terms': [
                r'\b(?:list.*terms|show.*terms|all terms|available terms)\b',
                r'\b(?:what terms|which terms|glossary terms|business terms)\b',
                r'\b(?:search terms|find terms|browse terms)\b'
            ],
            'analytical_chart': [
                r'\b(?:chart|graph|visualization|plot|diagram)\b',
                r'\b(?:create.*chart|generate.*graph|show.*plot)\b',
                r'\b(?:analytics|analysis|trend|comparison)\b'
            ],
            'data_query': [
                r'\b(?:query.*data|get.*data|fetch.*data|retrieve.*data)\b',
                r'\b(?:select.*from|show.*data|display.*data)\b',
                r'\b(?:data.*query|sql.*query|database.*query)\b'
            ],
            'chart_request': [
                r'\b(?:create.*chart|generate.*chart|make.*chart)\b',
                r'\b(?:chart.*request|visualization.*request)\b',
                r'\b(?:plot.*data|graph.*data|visualize.*data)\b'
            ],
            'table_search': [
                r'\b(?:find.*table|search.*table|locate.*table)\b',
                r'\b(?:table.*search|table.*find|table.*locate)\b',
                r'\b(?:which.*table|what.*table|table.*name)\b'
            ]
        }
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a user query with optional LLM enhancement.
        
        Args:
            query: The user's query
            context: Optional context about previous interactions
            
        Returns:
            Dictionary with response content and metadata
        """
        # Use LLM analysis if available
        if self.llm_available and self.llm_service:
            try:
                llm_analysis = self.llm_service.analyze_user_intent(query, context)
                intent = self._determine_intent_with_llm(query, llm_analysis)
            except Exception as e:
                print(f"⚠️ LLM analysis failed, falling back to pattern matching: {str(e)}")
                intent = self._determine_intent_with_patterns(query)
        else:
            intent = self._determine_intent_with_patterns(query)
        
        try:
            if intent == 'definition':
                response, requires_clarification = self._handle_definition_query(query, context)
                result = {"content": response, "requires_clarification": requires_clarification}
                
                # Add context updates if a term was discussed
                if context and context.get('last_discussed_term'):
                    result['context_updates'] = {
                        'last_discussed_term': context['last_discussed_term']
                    }
                
                return result
            elif intent == 'list_terms':
                return self._handle_list_terms_query(query)
            elif intent == 'asset_usage':
                result = self._handle_asset_usage_query(query, context)
                
                # Add context updates if a term was discussed
                if context and context.get('last_discussed_term'):
                    if 'context_updates' not in result:
                        result['context_updates'] = {}
                    result['context_updates']['last_discussed_term'] = context['last_discussed_term']
                
                return result
            elif intent == 'analytical_chart':
                return self._handle_analytical_chart_query(query)
            elif intent == 'data_query':
                return self._handle_data_query(query)
            elif intent == 'chart_request':
                return self._handle_chart_request(query)
            elif intent == 'table_search':
                return self._handle_table_search(query)
            else:
                return self._handle_general_query(query)
                
        except Exception as e:
            error_response = f"❌ **Error Processing Query:** {str(e)}"
            if self.llm_available and self.llm_service:
                try:
                    enhanced_error = self.llm_service.enhance_response(error_response, query, context)
                    return {"content": enhanced_error}
                except:
                    return {"content": error_response}
            else:
                return {"content": error_response}
    
    def _determine_intent_with_llm(self, query: str, llm_analysis: Dict[str, Any]) -> str:
        """Determine intent using both pattern matching and LLM analysis."""
        query_lower = query.lower()
        
        # Use LLM intent if confidence is high
        if llm_analysis.get('confidence') == 'high':
            llm_intent = llm_analysis.get('intent', '')
            if llm_intent in self.patterns:
                return llm_intent
        
        # Fallback to pattern matching
        return self._determine_intent_with_patterns(query)
    
    def _determine_intent_with_patterns(self, query: str) -> str:
        """Determine intent using pattern matching."""
        query_lower = query.lower()
        
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
        
        return 'general_query'
    
    def _handle_definition_query(self, query: str, context: Dict[str, Any] = None) -> Tuple[str, bool]:
        """
        Handle definition queries for glossary terms.
        
        Args:
            query: The user's query
            context: Optional conversation context
            
        Returns:
            Tuple of (response, requires_clarification)
        """
        try:
            # Extract term from query with context
            term = self._extract_term_from_query(query, context)
            if not term:
                return "I couldn't identify a specific term to define. Please specify which term you'd like me to look up in the glossary.", False
            
            # Search for the term in Atlan
            terms = self.atlan_client.search_glossary_terms(term)
            
            if not terms:
                return f"I couldn't find the term '{term}' in the Atlan glossary. Please check the spelling or try a different term.", False
            
            # Check for exact match first with flexible matching
            exact_match = None
            term_lower = term.lower()
            
            for t in terms:
                term_name = t.get('name', '').lower()
                
                # Try exact match first
                if term_name == term_lower:
                    exact_match = t
                    break
                
                # Try match ignoring parenthetical content (e.g., "Customer Acquisition Cost (CAC)" matches "customer acquisition cost")
                term_base = term_name.split('(')[0].strip()
                if term_base == term_lower:
                    exact_match = t
                    break
                
                # Try match where extracted term is contained in the glossary term name
                if term_lower in term_name and len(term_lower) > 3:  # Avoid matching very short terms
                    exact_match = t
                    break
            
            if not exact_match:
                # If no exact match, show similar terms and ask for clarification
                similar_terms = [t.get('name', 'Unknown') for t in terms[:5]]
                clarification_msg = f"I found several similar terms in Atlan, but no exact match for '{term}'. Did you mean one of these?\n\n"
                clarification_msg += "\n".join([f"• {t}" for t in similar_terms])
                clarification_msg += "\n\nPlease specify which term you'd like me to define."
                return clarification_msg, True
            
            # Store the discussed term in context for future reference
            if context:
                context['last_discussed_term'] = exact_match.get('name', term)
            
            # Format the response
            formatted_response = self._format_glossary_term(exact_match)
            
            # For definition queries, return the Atlan data directly without LLM enhancement
            # to prevent hallucinations and ensure accuracy
            return formatted_response, False
            
            # Enhance with LLM if available (DISABLED for definitions to prevent hallucinations)
            # if self.llm_available and self.llm_service:
            #     try:
            #         enhanced_response = self.llm_service.enhance_response(
            #             formatted_response, 
            #             f"define {exact_match.get('name', term)}",
            #             context
            #         )
            #         return enhanced_response, False
            #     except Exception as e:
            #         print(f"Response enhancement failed: {e}")
            #         return formatted_response, False
        except Exception as e:
            print(f"Error handling definition query: {e}")
            return f"I encountered an error while looking up the definition for '{term}'. Please try again.", False
    
    def _handle_asset_usage_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle queries about which assets use a specific term.
        
        Args:
            query: The user's query
            context: Optional conversation context
            
        Returns:
            Response dictionary
        """
        try:
            # Extract term from query with context
            term = self._extract_term_from_query(query, context)
            if not term:
                return {
                    "content": "I couldn't identify a specific term to search for. Please specify which term you'd like me to find assets for."
                }
            
            # First, find the term in the glossary
            terms = self.atlan_client.search_glossary_terms(term)
            
            if not terms:
                return {
                    "content": f"I couldn't find the term '{term}' in the Atlan glossary. Please check the spelling or try a different term."
                }
            
            # Check for exact match first with flexible matching (same logic as definition handler)
            exact_match = None
            term_lower = term.lower()
            
            for t in terms:
                term_name = t.get('name', '').lower()
                
                # Try exact match first
                if term_name == term_lower:
                    exact_match = t
                    break
                
                # Try match ignoring parenthetical content (e.g., "Customer Acquisition Cost (CAC)" matches "customer acquisition cost")
                term_base = term_name.split('(')[0].strip()
                if term_base == term_lower:
                    exact_match = t
                    break
                
                # Try match where extracted term is contained in the glossary term name
                if term_lower in term_name and len(term_lower) > 3:  # Avoid matching very short terms
                    exact_match = t
                    break
            
            if not exact_match:
                # If no exact match, show similar terms and ask for clarification
                similar_terms = [t.get('name', 'Unknown') for t in terms[:5]]
                clarification_msg = f"I found several similar terms in Atlan, but no exact match for '{term}'. Did you mean one of these?\n\n"
                clarification_msg += "\n".join([f"• {t}" for t in similar_terms])
                clarification_msg += "\n\nPlease specify which term you'd like me to find assets for."
                return {
                    "content": clarification_msg,
                    "requires_clarification": True,
                    "original_intent": "asset_usage",
                    "original_term": term
                }
            
            # Store the discussed term in context for future reference
            if context:
                context['last_discussed_term'] = exact_match.get('name', term)
            
            # Now find assets that use this term
            assets = self.atlan_client.find_assets_with_term(exact_match.get('guid'), exact_match.get('name', term))
            
            if not assets or len(assets) == 0:
                # If no assets found, provide a helpful message with the term definition
                response = f"**Assets using '{exact_match.get('name', term)}':**\n\n"
                response += "No assets are currently directly linked to this term in Atlan. This could mean:\n"
                response += "• The term exists in the glossary but hasn't been assigned to specific assets yet\n"
                response += "• Assets using this term might not have formal semantic assignments\n"
                response += "• You may need to manually assign this term to relevant assets\n\n"
                response += f"💡 **Suggestion:** You can search for assets by name using: 'Find assets with {exact_match.get('name', term)}'"
            else:
                # Group assets by type for better presentation
                assets_by_type = {}
                for asset in assets[:20]:  # Limit to 20 assets
                    asset_type = asset.get('__typeName', 'Unknown')
                    if asset_type not in assets_by_type:
                        assets_by_type[asset_type] = []
                    assets_by_type[asset_type].append(asset)
                
                response = f"**Assets using '{exact_match.get('name', term)}':**\n\n"
                
                for asset_type, type_assets in assets_by_type.items():
                    response += f"**{asset_type} ({len(type_assets)}):**\n"
                    for asset in type_assets[:5]:  # Show max 5 per type
                        name = asset.get('name', asset.get('displayName', 'Unnamed Asset'))
                        description = asset.get('description', asset.get('userDescription', ''))
                        if description and len(description) > 80:
                            description = description[:80] + "..."
                        
                        if description:
                            response += f"• **{name}** - {description}\n"
                        else:
                            response += f"• **{name}**\n"
                    
                    if len(type_assets) > 5:
                        response += f"  ... and {len(type_assets) - 5} more {asset_type.lower()}s\n"
                    response += "\n"
                
                total_assets = len(assets)
                if total_assets > 20:
                    response += f"... and {total_assets - 20} more assets\n\n"
            
            result = {"content": response}
            
            # Add context updates
            if context and context.get('last_discussed_term'):
                result['context_updates'] = {
                    'last_discussed_term': context['last_discussed_term']
                }
            
            if self.llm_available:
                try:
                    enhanced_response = self.llm_service.enhance_response(
                        response,
                        f"User asked: {query}",
                        context
                    )
                    result["content"] = enhanced_response
                    return result
                except Exception as e:
                    print(f"Response enhancement failed: {e}")
            
            return result
            
        except Exception as e:
            print(f"Error handling asset usage query: {e}")
            return {
                "content": f"I encountered an error while searching for assets using '{term}' in Atlan. Please try again or contact support if the issue persists."
            }
    
    def _handle_analytical_chart_query(self, query: str) -> Dict[str, Any]:
        """Handle analytical chart requests."""
        # Extract term from query
        term = self._extract_term_from_query(query)
        
        if not term:
            return {
                "content": "❓ **Could you clarify which term you'd like to analyze?**\n\nFor example:\n• 'Give me a bar chart by connector type of assets that use Customer Acquisition Cost'\n• 'Show me a graph by asset type of assets that use Annual Revenue'"
            }
        
        # Search for the term in the glossary first
        glossary_terms = self.atlan_client.search_glossary_terms(term)
        if not glossary_terms:
            response = f"🔍 **Term Not Found:** '{term}' was not found in the glossary."
            
            if self.llm_available and self.llm_service:
                try:
                    enhanced_response = self.llm_service.enhance_response(response, query)
                    return {"content": enhanced_response}
                except:
                    return {"content": response}
            else:
                return {"content": response}
        
        # Get assets using the term
        glossary_term = glossary_terms[0]
        term_guid = glossary_term.get('guid')
        assets = self.atlan_client.find_assets_with_term(term_guid)
        
        if not assets:
            response = f"📊 **No Data to Chart:** No assets found using '{term}'."
            
            if self.llm_available and self.llm_service:
                try:
                    enhanced_response = self.llm_service.enhance_response(response, query)
                    return {"content": enhanced_response}
                except:
                    return {"content": response}
            else:
                return {"content": response}
        
        # Analyze the query to determine grouping
        query_lower = query.lower()
        group_by = 'connectorName'  # Default
        
        if 'connector' in query_lower:
            group_by = 'connectorName'
        elif 'asset type' in query_lower or 'type' in query_lower:
            group_by = 'typeName'
        elif 'owner' in query_lower:
            group_by = 'ownerUsers'
        
        # Group assets by the specified dimension
        from collections import Counter
        counts = Counter()
        
        for asset in assets:
            if group_by == 'connectorName':
                connector = asset.get('connectorName', 'Unknown')
                counts[connector] += 1
            elif group_by == 'typeName':
                asset_type = asset.get('typeName', 'Unknown')
                counts[asset_type] += 1
            elif group_by == 'ownerUsers':
                owners = asset.get('ownerUsers', [])
                if owners:
                    for owner in owners:
                        counts[owner] += 1
                else:
                    counts['No Owner'] += 1
        
        if not counts:
            return {
                "content": f"📊 **No Data to Chart:** Found {len(assets)} assets using '{term}' but couldn't extract {group_by.replace('_', ' ')} information for charting."
            }
        
        # Create chart data
        import pandas as pd
        chart_data = pd.DataFrame([
            {'Category': k, 'Count': v, 'Percentage': round(v/len(assets)*100, 1)}
            for k, v in counts.most_common()
        ])
        
        # Generate chart
        from chart_generator import ChartGenerator
        chart_generator = ChartGenerator()
        
        # Determine chart type from query
        chart_type = 'bar'
        if 'pie' in query_lower:
            chart_type = 'pie'
        elif 'line' in query_lower:
            chart_type = 'line'
        
        chart = chart_generator.generate_chart(chart_data, chart_type, 
                                             title=f"Assets Using '{term}' by {group_by.replace('_', ' ').title()}")
        
        # Create response
        response = f"📊 **Analytical Chart: Assets Using '{term}' by {group_by.replace('_', ' ').title()}**\n\n"
        response += f"Found **{len(assets)} total assets** using this term.\n\n"
        response += "**Breakdown:**\n"
        for _, row in chart_data.iterrows():
            response += f"• {row['Category']}: {row['Count']} assets ({row['Percentage']}%)\n"
        
        # Enhance response with LLM if available
        if self.llm_available and self.llm_service:
            try:
                enhanced_response = self.llm_service.enhance_response(response, query)
                return {
                    "content": enhanced_response,
                    "chart": chart
                }
            except:
                return {
                    "content": response,
                    "chart": chart
                }
        else:
            return {
                "content": response,
                "chart": chart
            }
    
    def _handle_data_query(self, query: str) -> Dict[str, Any]:
        """Handle data queries."""
        response = "🔍 **Data Query Feature Coming Soon**\n\nThis feature will allow you to query actual data from Snowflake based on your glossary terms."
        
        if self.llm_available and self.llm_service:
            try:
                enhanced_response = self.llm_service.enhance_response(response, query)
                return {"content": enhanced_response}
            except:
                return {"content": response}
        else:
            return {"content": response}
    
    def _handle_chart_request(self, query: str) -> Dict[str, Any]:
        """Handle chart requests."""
        response = "📊 **Chart Generation Feature Coming Soon**\n\nThis feature will allow you to create visualizations from your data."
        
        if self.llm_available and self.llm_service:
            try:
                enhanced_response = self.llm_service.enhance_response(response, query)
                return {"content": enhanced_response}
            except:
                return {"content": response}
        else:
            return {"content": response}
    
    def _handle_table_search(self, query: str) -> Dict[str, Any]:
        """Handle table search."""
        response = "🔍 **Table Search Feature Coming Soon**\n\nThis feature will help you find specific tables in your data catalog."
        
        if self.llm_available and self.llm_service:
            try:
                enhanced_response = self.llm_service.enhance_response(response, query)
                return {"content": enhanced_response}
            except:
                return {"content": response}
        else:
            return {"content": response}
    
    def _handle_general_query(self, query: str) -> Dict[str, Any]:
        """Handle general queries."""
        general_response = "🤔 **I'm not sure how to help with that request.**\n\nI can help you with:\n• Finding glossary term definitions\n• Discovering which assets use specific terms\n• Creating analytical charts\n• Querying data\n\nCould you please rephrase your question?"
        
        if self.llm_available and self.llm_service:
            try:
                enhanced_response = self.llm_service.enhance_response(general_response, query)
                return {"content": enhanced_response}
            except:
                return {"content": general_response}
        else:
            return {"content": general_response}
    
    def _handle_list_terms_query(self, query: str) -> Dict[str, Any]:
        """Handle list terms queries."""
        try:
            terms = self.atlan_client.get_all_glossary_terms()
            
            if not terms:
                response = "📚 **No Glossary Terms Found**\n\nYour glossary appears to be empty."
                
                if self.llm_available and self.llm_service:
                    try:
                        enhanced_response = self.llm_service.enhance_response(response, query)
                        return {"content": enhanced_response}
                    except:
                        return {"content": response}
                else:
                    return {"content": response}
            
            response = f"📚 **Found {len(terms)} Glossary Terms:**\n\n"
            
            # Group terms by category if available
            categories = {}
            for term in terms[:20]:  # Limit to first 20
                category = term.get('anchor', {}).get('displayText', 'Uncategorized')
                if category not in categories:
                    categories[category] = []
                categories[category].append(term.get('name', 'Unknown'))
            
            for category, term_names in categories.items():
                response += f"**{category}:**\n"
                for name in term_names:
                    response += f"• {name}\n"
                response += "\n"
            
            if len(terms) > 20:
                response += f"... and {len(terms) - 20} more terms.\n\n"
            
            response += "💡 **Tip:** Ask me to define any specific term, or search for assets that use a term!"
            
            if self.llm_available and self.llm_service:
                try:
                    enhanced_response = self.llm_service.enhance_response(response, query)
                    return {"content": enhanced_response}
                except:
                    return {"content": response}
            else:
                return {"content": response}
                
        except Exception as e:
            error_response = f"❌ **Error retrieving glossary terms:** {str(e)}"
            
            if self.llm_available and self.llm_service:
                try:
                    enhanced_response = self.llm_service.enhance_response(error_response, query)
                    return {"content": enhanced_response}
                except:
                    return {"content": error_response}
            else:
                return {"content": error_response}
    
    def _extract_term_from_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Extract term name from various query formats with improved precision and context awareness."""
        # Remove common question words and patterns
        clean_query = query.lower().strip()
        
        # Handle common abbreviations first
        abbreviation_mappings = {
            'cac': 'customer acquisition cost',
            'ltv': 'lifetime value',
            'cpa': 'cost per acquisition',
            'cpc': 'cost per click',
            'cpm': 'cost per mille',
            'roi': 'return on investment',
            'kpi': 'key performance indicator'
        }
        
        # Check if the query is just an abbreviation
        for abbrev, full_term in abbreviation_mappings.items():
            if clean_query.strip() == abbrev:
                return full_term
        
        # Check for context-based references first
        if context and context.get('last_discussed_term'):
            # Look for pronouns and context words that refer to the last discussed term
            context_words = ['this term', 'that term', 'it', 'the term', 'this', 'that']
            for word in context_words:
                if word in clean_query:
                    return context['last_discussed_term']
            
            # Check for "assets use this term" or similar patterns
            if any(phrase in clean_query for phrase in ['assets use', 'what uses', 'which assets', 'find assets']):
                return context['last_discussed_term']
        
        # Patterns to extract terms from definition queries (more precise)
        patterns = [
            # Direct quotes
            r'["\']([^"\']+)["\']',
            # After "define" or "definition of"
            r'(?:define|definition of)\s+(.+?)(?:\s*\?|$)',
            # After "what is" or "how is"
            r'(?:what is|how is)\s+(.+?)(?:\s+defined|mean|means|\?|$)',
            # After "meaning of"
            r'meaning of\s+(.+?)(?:\s*\?|$)',
            # After "tell me about" or "explain"
            r'(?:tell me about|explain)\s+(.+?)(?:\s*\?|$)',
            # After "which assets use" or "what uses"
            r'(?:which assets use|what uses)\s+(.+?)(?:\s*\?|$)',
            # After "find" or "search for"
            r'(?:find|search for)\s+(.+?)(?:\s*\?|$)',
            # Handle abbreviations in context (e.g., "what is CAC")
            r'(?:what is|define|explain)\s+([A-Z]{2,4})(?:\s*\?|$)',
            # General term extraction (fallback)
            r'\b([A-Z][a-zA-Z\s]+(?:Cost|Revenue|Rate|Value|Metric|KPI|Data|Table|Column))\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, clean_query)
            if match:
                term = match.group(1).strip()
                # Clean up the term
                term = re.sub(r'\s+', ' ', term)  # Normalize whitespace
                term = term.strip('?.,!')  # Remove punctuation
                
                # Check if it's an abbreviation and expand it
                if len(term) <= 4 and (term.isupper() or term.islower()):
                    for abbrev, full_term in abbreviation_mappings.items():
                        if term.lower() == abbrev:
                            return full_term
                
                if len(term) > 2:  # Ensure it's not too short
                    return term
        
        # NEW: Try to extract multi-word business terms
        # Look for meaningful capitalized phrases or business terminology
        business_term_patterns = [
            # Multi-word capitalized terms (like "Customer Acquisition Cost")
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Cost|Rate|Value|Metric|Score|Index|Ratio|Count|Amount|Price|Revenue|Profit|Loss|Margin|Performance|Indicator|Analysis|Report|Dashboard|Data|Table|Column))?)\b',
            # Terms with parentheses (like "Customer Acquisition Cost (CAC)")
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+[A-Z][a-z]+)*)\s*\([A-Z]{2,5}\)',
            # Business terms ending with common suffixes
            r'\b([a-z]+(?:\s+[a-z]+)*(?:\s+(?:cost|rate|value|metric|score|index|ratio|count|amount|price|revenue|profit|loss|margin|performance|indicator|analysis|report|dashboard|data|table|column)))\b'
        ]
        
        for pattern in business_term_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                # Return the longest match (most specific)
                longest_match = max(matches, key=len)
                if len(longest_match.split()) > 1:  # Only multi-word terms
                    return longest_match.strip()
        
        # If no multi-word term found, fall back to individual words but prioritize longer combinations
        words = clean_query.split()
        stop_words = ['the', 'and', 'for', 'with', 'what', 'is', 'are', 'how', 'why', 'when', 'where', 'define', 'definition', 'of', 'explain', 'tell', 'me', 'about']
        meaningful_words = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # Try combinations of 2-4 words first
        for length in range(min(4, len(meaningful_words)), 0, -1):
            for i in range(len(meaningful_words) - length + 1):
                term_candidate = ' '.join(meaningful_words[i:i+length])
                # Check if it's an abbreviation and expand it
                if length == 1 and (term_candidate.isupper() or term_candidate.islower()) and len(term_candidate) <= 4:
                    for abbrev, full_term in abbreviation_mappings.items():
                        if term_candidate.lower() == abbrev:
                            return full_term
                if length > 1:  # Prefer multi-word terms
                    return term_candidate
        
        # Finally, return single words if nothing else works
        if meaningful_words:
            first_word = meaningful_words[0]
            # Check if it's an abbreviation
            if (first_word.isupper() or first_word.islower()) and len(first_word) <= 4:
                for abbrev, full_term in abbreviation_mappings.items():
                    if first_word.lower() == abbrev:
                        return full_term
            return first_word
        
        return ""
    
    def _format_glossary_term(self, term: Dict[str, Any]) -> str:
        """Format glossary term response with rich metadata."""
        name = term.get('name', 'Unknown')
        description = term.get('description') or term.get('user_description', 'No description available')
        certificate_status = term.get('certificate_status', 'UNKNOWN')
        owners = term.get('owner_users', [])
        owner_groups = term.get('owner_groups', [])
        announcement = term.get('announcement_message')
        examples = term.get('examples', [])
        abbreviation = term.get('abbreviation')
        categories = term.get('categories', [])
        qualified_name = term.get('qualified_name', 'Unknown')
        
        # Build response
        response = f"📚 **{name}**\n\n"
        
        # Certificate status with emoji
        status_emoji = "✅" if certificate_status == "VERIFIED" else "📝" if certificate_status == "DRAFT" else "⚠️"
        response += f"{status_emoji} **Status:** {certificate_status}\n\n"
        
        # Description
        response += f"📖 **Definition:** {description}\n\n"
        
        # Owners
        if owners and isinstance(owners, list) and len(owners) > 0:
            owner_list = ", ".join([f"@{owner}" for owner in owners if owner])
            if owner_list:
                response += f"👥 **Owners:** {owner_list}\n\n"
        
        if owner_groups and isinstance(owner_groups, list) and len(owner_groups) > 0:
            group_list = ", ".join([f"@{group}" for group in owner_groups if group])
            if group_list:
                response += f"🏢 **Owner Groups:** {group_list}\n\n"
        
        # Announcement
        if announcement:
            response += f"📢 **Announcement:** {announcement}\n\n"
        
        # Examples
        if examples and isinstance(examples, list) and len(examples) > 0:
            # Filter out None/empty examples
            valid_examples = [ex for ex in examples if ex]
            if valid_examples:
                response += f"💡 **Examples:** {', '.join(valid_examples)}\n\n"
        
        # Abbreviation
        if abbreviation:
            response += f"🔤 **Abbreviation:** {abbreviation}\n\n"
        
        # Categories
        if categories and isinstance(categories, list) and len(categories) > 0:
            category_list = ", ".join([str(cat) for cat in categories if cat])
            response += f"📂 **Category:** {category_list}\n\n"
        else:
            response += f"📂 **Category:** Uncategorized\n\n"
        
        # Qualified name (technical reference)
        response += f"🔗 **Technical Reference:** {qualified_name}\n\n"
        
        # Follow-up suggestions
        response += "💡 **Follow-up options:**\n"
        response += f"• Ask 'Which assets use {name}?' to see where this term is applied\n"
        response += "• Ask about related terms or explore the glossary further"
        
        return response
    
    def handle_clarification_response(self, original_term: str, user_response: str, original_intent: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle user response to intent clarification."""
        if original_intent == 'definition':
            # User is responding to a definition clarification
            user_response_lower = user_response.lower().strip()
            
            # First, check if they provided a specific term name (more than 2 characters)
            if len(user_response.strip()) > 2:
                # Check if they're selecting a number from the options
                if user_response.strip().isdigit():
                    return {
                        "content": f"❓ **Please specify the exact term name**: You selected option {user_response.strip()}. Please type the full term name instead of the number."
                    }
                
                # Search for the exact term they specified
                new_results = self.atlan_client.search_glossary_terms(user_response)
                if new_results:
                    # Look for exact match first
                    exact_match = None
                    for result in new_results:
                        if result.get('name', '').lower() == user_response.lower():
                            exact_match = result
                            break
                    
                    if exact_match:
                        # Update context with the discussed term
                        if context:
                            context['last_discussed_term'] = exact_match.get('name', user_response)
                        
                        formatted_response = self._format_glossary_term(exact_match)
                        
                        result = {"content": formatted_response}
                        
                        # Add context updates
                        if context and context.get('last_discussed_term'):
                            result['context_updates'] = {
                                'last_discussed_term': context['last_discussed_term']
                            }
                        
                        if self.llm_available and self.llm_service:
                            try:
                                enhanced_response = self.llm_service.enhance_response(formatted_response, f"define {user_response}")
                                result["content"] = enhanced_response
                                return result
                            except:
                                return result
                        else:
                            return result
                    else:
                        # Show the first result as a suggestion
                        first_result = new_results[0]
                        suggestion_response = f"🤔 **Did you mean '{first_result.get('name', 'Unknown')}'?**\n\nI found a similar term. Is this what you were looking for?"
                        
                        if self.llm_available and self.llm_service:
                            try:
                                enhanced_response = self.llm_service.enhance_response(suggestion_response, f"define {user_response}")
                                return {
                                    "content": enhanced_response,
                                    "requires_clarification": True,
                                    "original_intent": "definition",
                                    "original_term": user_response
                                }
                            except:
                                return {
                                    "content": suggestion_response,
                                    "requires_clarification": True,
                                    "original_intent": "definition",
                                    "original_term": user_response
                                }
                        else:
                            return {
                                "content": suggestion_response,
                                "requires_clarification": True,
                                "original_intent": "definition",
                                "original_term": user_response
                            }
                else:
                    not_found_response = f"🔍 **Term Not Found:** '{user_response}' was not found in the glossary."
                    
                    if self.llm_available and self.llm_service:
                        try:
                            enhanced_response = self.llm_service.enhance_response(not_found_response, f"define {user_response}")
                            return {"content": enhanced_response}
                        except:
                            return {"content": not_found_response}
                    else:
                        return {"content": not_found_response}
            
            # Check for confirmation responses (only if they didn't provide a specific term)
            confirmation_words = ['yes', 'y', 'yeah', 'yep', 'correct', 'right', 'that\'s right', 'exactly']
            if any(user_response_lower == word or user_response_lower.startswith(word + ' ') or user_response_lower.endswith(' ' + word) or ' ' + word + ' ' in user_response_lower for word in confirmation_words):
                # User confirmed - search for the original term again and provide definition
                results = self.atlan_client.search_glossary_terms(original_term)
                
                if results:
                    # Use the first result (should be the one we showed in clarification)
                    term = results[0]
                    
                    # Update context with the discussed term
                    if context:
                        context['last_discussed_term'] = term.get('name', original_term)
                    
                    formatted_response = self._format_glossary_term(term)
                    
                    result = {"content": formatted_response}
                    
                    # Add context updates
                    if context and context.get('last_discussed_term'):
                        result['context_updates'] = {
                            'last_discussed_term': context['last_discussed_term']
                        }
                    
                    if self.llm_available and self.llm_service:
                        try:
                            enhanced_response = self.llm_service.enhance_response(formatted_response, f"define {original_term}")
                            result["content"] = enhanced_response
                            return result
                        except:
                            return result
                    else:
                        return result
                else:
                    error_response = f"❌ **Error:** Could not find definition for '{original_term}'"
                    
                    if self.llm_available and self.llm_service:
                        try:
                            enhanced_response = self.llm_service.enhance_response(error_response, f"define {original_term}")
                            return {"content": enhanced_response}
                        except:
                            return {"content": error_response}
                    else:
                        return {"content": error_response}
            
            # If we get here, the response wasn't clear
            return {
                "content": "I'm not sure how to interpret your response. Please specify the exact term name you'd like me to define."
            }
        
        elif original_intent == 'asset_usage':
            # Handle asset usage clarification
            if len(user_response.strip()) > 2:
                new_results = self.atlan_client.search_glossary_terms(user_response)
                if new_results:
                    exact_match = None
                    for result in new_results:
                        if result.get('name', '').lower() == user_response.lower():
                            exact_match = result
                            break
                    
                    if exact_match:
                        # Update context with the discussed term
                        if context:
                            context['last_discussed_term'] = exact_match.get('name', user_response)
                        
                        # Now find assets that use this term
                        assets = self.atlan_client.find_assets_with_term(exact_match.get('guid'), exact_match.get('name', term))
                        
                        if not assets:
                            response = f"I couldn't find any assets in Atlan that currently use the term '{exact_match.get('name', user_response)}'."
                        else:
                            response = f"**Assets using '{exact_match.get('name', user_response)}':**\n\n"
                            for asset in assets[:10]:  # Limit to 10
                                name = asset.get('name', 'Unknown')
                                description = asset.get('description', 'No description available')
                                if description and len(description) > 100:
                                    description = description[:100] + "..."
                                response += f"• **{name}** - {description}\n"
                            
                            if len(assets) > 10:
                                response += f"\n... and {len(assets) - 10} more assets"
                        
                        result = {"content": response}
                        
                        # Add context updates
                        if context and context.get('last_discussed_term'):
                            result['context_updates'] = {
                                'last_discussed_term': context['last_discussed_term']
                            }
                        
                        return result
                    else:
                        return {
                            "content": f"I found similar terms but no exact match for '{user_response}'. Please try a different term."
                        }
                else:
                    return {
                        "content": f"I couldn't find the term '{user_response}' in the glossary. Please check the spelling or try a different term."
                    }
            else:
                return {
                    "content": "Please specify the exact term name you'd like me to find assets for."
                }
        
        else:
            return {
                "content": "I'm not sure how to handle that clarification. Please try asking your question again."
            } 