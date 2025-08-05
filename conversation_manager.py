#!/usr/bin/env python3
"""
Conversation Manager for Atlan Data Chat
Handles intent recognition, conversation history, and user interactions
"""

import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from llm_service import LLMService

@dataclass
class Message:
    """Represents a single message in the conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    intent: Optional[str] = None
    entities: Optional[List[str]] = None
    confidence: Optional[float] = None
    requires_confirmation: bool = False
    confirmed: bool = False

@dataclass
class ConversationContext:
    """Maintains conversation context and state"""
    messages: List[Message]
    current_term: Optional[str] = None
    current_term_guid: Optional[str] = None
    last_intent: Optional[str] = None
    pending_confirmation: bool = False
    pending_query: Optional[str] = None

class ConversationManager:
    """Manages conversation flow, intent recognition, and context"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.context = ConversationContext(messages=[])
        
    def add_message(self, role: str, content: str, **kwargs) -> Message:
        """Add a message to the conversation history"""
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            **kwargs
        )
        self.context.messages.append(message)
        return message
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history as a list of dictionaries"""
        return [asdict(msg) for msg in self.context.messages]
    
    def clear_conversation(self):
        """Clear the conversation history"""
        self.context = ConversationContext(messages=[])
    
    def analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """Use LLM to analyze user intent and extract entities"""
        
        # If LLM is not available, use fallback immediately
        if not self.llm_service.api_available:
            return self._fallback_intent_analysis(user_input)
        
        # Build context from conversation history
        conversation_context = self._build_context_for_llm()
        
        prompt = f"""
You are an intent recognition system for a data glossary assistant. Analyze the user's input and determine their intent.

Conversation History:
{conversation_context}

User Input: "{user_input}"

IMPORTANT: For entity extraction, extract the FULL term name, not just individual words.
- "Customer Acquisition Cost" should be extracted as ["Customer Acquisition Cost"], not ["Customer", "Acquisition", "Cost"]
- "CAC" should be extracted as ["CAC"]
- "Customer Lifetime Value" should be extracted as ["Customer Lifetime Value"]
- "CLV" should be extracted as ["CLV"]

Analyze the intent and extract entities. Return a JSON response with:
{{
    "intent": "define_term|find_assets|list_terms|clarify|unknown",
    "entities": ["extracted_terms"],
    "confidence": 0.0-1.0,
    "requires_confirmation": true/false,
    "reasoning": "brief explanation"
}}

Intent types:
- define_term: User wants to know what a term means
- find_assets: User wants to find assets linked to a term
- list_terms: User wants to see available terms
- clarify: Intent is unclear, needs clarification
- unknown: Cannot determine intent

Examples:
- "define customer acquisition cost" → {{"intent": "define_term", "entities": ["Customer Acquisition Cost"], "confidence": 0.9, "requires_confirmation": false}}
- "which assets use CAC" → {{"intent": "find_assets", "entities": ["CAC"], "confidence": 0.95, "requires_confirmation": false}}
- "what terms are available" → {{"intent": "list_terms", "entities": [], "confidence": 0.8, "requires_confirmation": false}}

Response:"""
        
        try:
            response = self.llm_service.analyze_text(prompt)
            
            # Check if response looks like JSON
            if response.strip().startswith('{') and response.strip().endswith('}'):
                result = json.loads(response)
                
                # Validate the response structure
                required_fields = ["intent", "entities", "confidence", "requires_confirmation"]
                for field in required_fields:
                    if field not in result:
                        result[field] = None if field != "entities" else []
                
                return result
            else:
                # Response doesn't look like JSON, use fallback
                return self._fallback_intent_analysis(user_input)
            
        except (json.JSONDecodeError, Exception) as e:
            # Fallback to basic keyword matching
            return self._fallback_intent_analysis(user_input)
    
    def _build_context_for_llm(self) -> str:
        """Build conversation context for LLM analysis"""
        if not self.context.messages:
            return "No previous conversation."
        
        # Get last 5 messages for context
        recent_messages = self.context.messages[-5:]
        context_lines = []
        
        for msg in recent_messages:
            context_lines.append(f"{msg.role.upper()}: {msg.content}")
            if msg.intent:
                context_lines.append(f"Intent: {msg.intent}")
            if msg.entities:
                context_lines.append(f"Entities: {', '.join(msg.entities)}")
        
        return "\n".join(context_lines)
    
    def _fallback_intent_analysis(self, user_input: str) -> Dict[str, Any]:
        """Fallback intent analysis using keyword matching"""
        input_lower = user_input.lower()
        
        # Check for list_terms intent first
        if any(word in input_lower for word in ["list", "show", "what terms", "available terms", "all terms", "terms available"]):
            return {
                "intent": "list_terms",
                "entities": [],
                "confidence": 0.9,
                "requires_confirmation": False,
                "suggested_phrasing": None,
                "explanation": "Detected intent to list terms using keyword matching"
            }
        
        # Check for define_term intent
        if any(word in input_lower for word in ["define", "what is", "explain", "tell me about", "meaning of", "definition of"]):
            entities = self._extract_entities_fallback(user_input)
            return {
                "intent": "define_term",
                "entities": entities,
                "confidence": 0.8 if entities else 0.6,
                "requires_confirmation": len(entities) == 0,  # Only ask confirmation if no entities found
                "suggested_phrasing": None,
                "explanation": "Detected intent to define a term using keyword matching"
            }
        
        # Check for find_assets intent
        elif any(word in input_lower for word in ["assets", "linked", "use", "which", "what are", "find", "search", "show me"]):
            entities = self._extract_entities_fallback(user_input)
            return {
                "intent": "find_assets",
                "entities": entities,
                "confidence": 0.8 if entities else 0.6,
                "requires_confirmation": len(entities) == 0,  # Only ask confirmation if no entities found
                "suggested_phrasing": None,
                "explanation": "Detected intent to find assets using keyword matching"
            }
        
        # If no clear intent, try to extract entities and make a best guess
        entities = self._extract_entities_fallback(user_input)
        if entities:
            # If we found entities, assume they want to define the term
            return {
                "intent": "define_term",
                "entities": entities,
                "confidence": 0.7,
                "requires_confirmation": True,  # Ask for confirmation since intent is unclear
                "suggested_phrasing": f"Did you want to define '{entities[0]}' or find assets linked to it?",
                "explanation": "Found entities but intent unclear - defaulting to define_term"
            }
        else:
            return {
                "intent": "unknown",
                "entities": [],
                "confidence": 0.3,
                "requires_confirmation": False,
                "suggested_phrasing": "Could you please rephrase your question? For example: 'Define CAC' or 'Which assets use Customer Acquisition Cost?'",
                "explanation": "Intent unclear - needs clarification"
            }
    
    def _extract_entities_fallback(self, user_input: str) -> List[str]:
        """Fallback entity extraction using simple heuristics"""
        # Remove common words and extract potential entities
        common_words = {"define", "what", "is", "are", "the", "which", "assets", "linked", "to", "use", "tell", "me", "about", "show", "find", "search", "list", "get", "give", "provide", "explain", "describe"}
        
        # Handle multi-word terms better
        input_lower = user_input.lower()
        
        # Look for specific patterns first (highest priority)
        if "customer acquisition cost" in input_lower:
            return ["Customer Acquisition Cost"]
        elif "cac" in input_lower:
            return ["CAC"]
        elif "customer lifetime value" in input_lower:
            return ["Customer Lifetime Value"]
        elif "clv" in input_lower:
            return ["CLV"]
        elif "customer acquisition" in input_lower:
            return ["Customer Acquisition"]
        elif "customer lifetime" in input_lower:
            return ["Customer Lifetime"]
        
        # Fallback to word-based extraction with better grouping
        words = user_input.split()
        entities = []
        current_entity = []
        
        for word in words:
            word_lower = word.lower()
            if word_lower not in common_words and len(word) > 2:
                current_entity.append(word)
            elif current_entity:
                # Join accumulated words as a single entity
                entity = " ".join(current_entity)
                if len(entity) > 3:  # Only add if entity is substantial
                    entities.append(entity)
                current_entity = []
        
        # Add any remaining entity
        if current_entity:
            entity = " ".join(current_entity)
            if len(entity) > 3:  # Only add if entity is substantial
                entities.append(entity)
        
        return entities
    
    def should_ask_confirmation(self, intent_analysis: Dict[str, Any]) -> bool:
        """Determine if we should ask for confirmation"""
        confidence = intent_analysis.get("confidence", 0)
        intent = intent_analysis.get("intent")
        
        # Don't ask for confirmation if:
        # 1. Intent is unknown (we'll ask for clarification instead)
        # 2. Confidence is very high (>0.9)
        # 3. User explicitly doesn't want confirmation
        if intent == "unknown" or confidence > 0.9:
            return False
        
        # Only ask for confirmation if confidence is moderate and intent is clear
        return (
            intent_analysis.get("requires_confirmation", False) and
            0.5 <= confidence < 0.9 and
            intent in ["define_term", "find_assets", "list_terms"]
        )
    
    def generate_confirmation_message(self, intent_analysis: Dict[str, Any]) -> str:
        """Generate a confirmation message for the user"""
        intent = intent_analysis.get("intent")
        entities = intent_analysis.get("entities", [])
        explanation = intent_analysis.get("explanation", "")
        
        if intent == "define_term":
            return f"I understand you want to define the term '{', '.join(entities)}'. Is that correct?"
        elif intent == "find_assets":
            return f"I understand you want to find assets linked to '{', '.join(entities)}'. Is that correct?"
        else:
            return f"I think you want to {intent.replace('_', ' ')} for '{', '.join(entities)}'. Is that correct?"
    
    def generate_clarification_message(self, intent_analysis: Dict[str, Any]) -> str:
        """Generate a clarification message when intent is unclear"""
        suggested_phrasing = intent_analysis.get("suggested_phrasing", "")
        explanation = intent_analysis.get("explanation", "")
        
        message = f"I'm not sure what you're asking for. {explanation}"
        if suggested_phrasing:
            message += f"\n\nDid you mean: \"{suggested_phrasing}\"?"
        
        return message
    
    def update_context(self, intent_analysis: Dict[str, Any], confirmed: bool = True):
        """Update conversation context based on intent analysis"""
        if confirmed:
            self.context.last_intent = intent_analysis.get("intent")
            entities = intent_analysis.get("entities", [])
            if entities:
                self.context.current_term = entities[0]  # Use first entity as current term 