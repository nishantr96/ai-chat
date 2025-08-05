import os
import openai
from typing import Dict, Any, List, Optional
import json

class LLMService:
    """Service for LLM-powered reasoning and user understanding using Atlan Gateway LiteLLM Proxy."""
    
    def __init__(self):
        """Initialize the LLM service with Atlan Gateway LiteLLM Proxy configuration."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            raise ValueError("OPENAI_API_KEY environment variable is required. Please update your .env file with a valid API key.")
        
        # Use Atlan Gateway's LiteLLM Proxy
        self.base_url = "https://llmproxy.atlan.dev"
        
        # Initialize OpenAI client with Atlan Gateway LiteLLM Proxy configuration
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=self.base_url
        )
    
    def analyze_user_intent(self, user_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze user intent using LLM."""
        system_prompt = """You are an AI assistant that analyzes user queries to understand their intent when interacting with a data catalog system.

Your task is to analyze the user's query and determine:
1. Primary intent (definition, asset_usage, data_query, chart_request, table_search, analytical_chart, list_terms, general_query)
2. Confidence level (high, medium, low)
3. Extracted terms or entities
4. Reasoning for your classification
5. Suggested next steps
6. Clarification questions if needed

Available intents:
- definition: User wants to define or understand a glossary term
- asset_usage: User wants to find which assets use a specific term
- data_query: User wants to query actual data from tables
- chart_request: User wants to create visualizations
- table_search: User wants to search for specific tables
- analytical_chart: User wants to create analytical insights or charts based on metadata
- list_terms: User wants to see all available glossary terms
- general_query: General questions or unclear intent

Return your analysis as a JSON object with these fields:
{
    "intent": "string",
    "confidence": "high|medium|low",
    "extracted_terms": ["list", "of", "terms"],
    "reasoning": "explanation of your classification",
    "next_steps": "suggested actions",
    "clarification_questions": ["question1", "question2"]
}"""

        user_prompt = f"User query: {user_query}"
        if context:
            user_prompt += f"\nContext: {json.dumps(context)}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use gpt-4o instead of gpt-4
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "intent": "general_query",
                    "confidence": "low",
                    "extracted_terms": [],
                    "reasoning": "LLM response could not be parsed as JSON",
                    "next_steps": "Use pattern-based intent detection",
                    "clarification_questions": []
                }
                
        except Exception as e:
            print(f"LLM analysis failed: {str(e)}")
            return {
                "intent": "general_query",
                "confidence": "low",
                "extracted_terms": [],
                "reasoning": f"LLM service error: {str(e)}",
                "next_steps": "Use pattern-based intent detection",
                "clarification_questions": []
            }
    
    def enhance_response(self, original_response: str, user_query: str, context: Dict[str, Any] = None) -> str:
        """Enhance a response using LLM."""
        system_prompt = """You are an AI assistant that enhances responses about data governance and business terms.

CRITICAL RULES:
1. NEVER replace factual information from the original response
2. NEVER add definitions or explanations not present in the original
3. ONLY improve formatting, clarity, and readability of existing content
4. If the original response contains data from Atlan (business glossary, metadata, etc.), preserve ALL of it exactly
5. You may only rephrase for better readability while keeping all facts identical

Your task is to improve the given response by:
1. Making it more conversational and engaging in tone
2. Improving formatting and structure
3. Adding helpful transition phrases
4. Suggesting relevant follow-up questions
5. Maintaining 100% of the original factual information

If the original response is from a business glossary or data catalog, treat it as authoritative and do not modify the core content."""

        user_prompt = f"Please enhance this response while preserving ALL factual information:\n\nOriginal response: {original_response}\n\nUser query: {user_query}"
        if context:
            user_prompt += f"\nContext: {json.dumps(context)}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use gpt-4o instead of gpt-4
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Lower temperature for more consistent adherence to rules
                max_tokens=600
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Response enhancement failed: {str(e)}")
            return original_response
    
    def generate_clarification_questions(self, user_query: str, available_options: List[str] = None) -> List[str]:
        """Generate clarification questions using LLM."""
        system_prompt = """You are an AI assistant that generates helpful clarification questions.

Your task is to create 2-3 specific, clear questions that will help clarify the user's intent or help them choose between options.

Make the questions:
1. Specific and actionable
2. Easy to understand
3. Relevant to the user's query
4. Helpful for decision-making"""

        user_prompt = f"User query: {user_query}"
        if available_options:
            user_prompt += f"\nAvailable options: {', '.join(available_options)}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use gpt-4o instead of gpt-4
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            # Split by lines and clean up
            questions = [q.strip() for q in result.split('\n') if q.strip()]
            return questions[:3]  # Return max 3 questions
            
        except Exception as e:
            print(f"Clarification questions generation failed: {str(e)}")
            return ["Could you please clarify your request?"]
    
    def suggest_follow_up_questions(self, current_response: str, user_query: str) -> List[str]:
        """Suggest relevant follow-up questions using LLM."""
        system_prompt = """You are an AI assistant that suggests relevant follow-up questions.

Based on the current response and user query, suggest 2-3 natural follow-up questions that the user might want to ask next.

Make the suggestions:
1. Relevant to the current context
2. Natural and conversational
3. Helpful for further exploration
4. Specific and actionable"""

        user_prompt = f"Current response: {current_response}\nUser query: {user_query}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use gpt-4o instead of gpt-4
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            # Split by lines and clean up
            questions = [q.strip() for q in result.split('\n') if q.strip()]
            return questions[:3]  # Return max 3 questions
            
        except Exception as e:
            print(f"Follow-up questions generation failed: {str(e)}")
            return [] 