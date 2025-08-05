import openai
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        # Use LiteLLM proxy at Atlan Gateway
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://llmproxy.atlan.dev")
        
        self.api_available = False
        if api_key and api_key.strip():  # Accept any non-empty API key
            try:
                self.client = openai.OpenAI(
                    api_key=api_key,
                    base_url=base_url  # Use LiteLLM proxy
                )
                self.api_available = True
                print(f"✅ LLM service initialized with LiteLLM proxy: {base_url}")
            except Exception as e:
                print(f"⚠️ LiteLLM proxy not available: {e}")
        else:
            print("⚠️ No OpenAI API key found, using mock responses")
        
    def test_connection(self) -> bool:
        """Test LiteLLM proxy connection"""
        if not self.api_available:
            return False
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            print(f"❌ LiteLLM proxy connection failed: {e}")
            return False
        
    def analyze_text(self, prompt: str) -> str:
        """Analyze text using LiteLLM proxy"""
        if not self.api_available:
            return self._mock_text_analysis(prompt)
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful data analyst assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ LiteLLM analysis failed: {e}")
            return self._mock_text_analysis(prompt)
        
    def analyze_assets(self, assets: List[Dict[str, Any]], query: str) -> str:
        """Analyze assets using LiteLLM proxy"""
        if not self.api_available:
            return self._mock_asset_analysis(assets, query)
            
        try:
            asset_summary = self._prepare_asset_summary(assets)
            
            prompt = f"""
            Based on the following assets and user query, provide a comprehensive analysis:
            
            User Query: {query}
            
            Assets:
            {asset_summary}
            
            Please provide:
            1. A summary of the relevant assets
            2. How these assets relate to the user's query
            3. Key insights or recommendations
            4. Any data quality or completeness considerations
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a data governance expert. Analyze the provided assets and provide insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ LiteLLM asset analysis failed: {e}")
            return self._mock_asset_analysis(assets, query)
        
    def _mock_text_analysis(self, prompt: str) -> str:
        """Provide mock text analysis when LLM is unavailable"""
        return f"Mock analysis for: {prompt[:100]}...\n\nThis is a placeholder response since the LiteLLM proxy is not available."
        
    def _mock_asset_analysis(self, assets: List[Dict[str, Any]], query: str) -> str:
        """Provide mock asset analysis when LLM is unavailable"""
        asset_count = len(assets)
        asset_names = [asset.get('name', 'Unknown') for asset in assets[:3]]
        
        return f"""
        **Mock Asset Analysis**
        
        Query: {query}
        Assets Found: {asset_count}
        
        **Summary:**
        Found {asset_count} assets related to your query. The main assets include: {', '.join(asset_names)}
        
        **Key Insights:**
        - These assets appear to be relevant to your search criteria
        - Consider reviewing the asset descriptions and metadata for more details
        - Check data quality and freshness indicators
        
        **Recommendations:**
        - Explore the lineage and relationships between these assets
        - Review any associated documentation or readme files
        - Consider the data governance and certification status
        
        *Note: This is a mock analysis. For real AI-powered insights, ensure the LiteLLM proxy is properly configured.*
        """
        
    def _prepare_asset_summary(self, assets: List[Dict[str, Any]]) -> str:
        """Prepare a summary of assets for LLM analysis"""
        summary = []
        for i, asset in enumerate(assets[:5], 1):  # Limit to first 5 assets
            name = asset.get('name', 'Unknown')
            asset_type = asset.get('typeName', 'Unknown')
            description = asset.get('description', 'No description available')
            qualified_name = asset.get('qualifiedName', 'Unknown')
            
            summary.append(f"""
            {i}. {name} ({asset_type})
               - Qualified Name: {qualified_name}
               - Description: {description[:200]}{'...' if len(description) > 200 else ''}
            """)
        
        if len(assets) > 5:
            summary.append(f"\n... and {len(assets) - 5} more assets")
            
        return '\n'.join(summary) 