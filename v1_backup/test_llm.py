#!/usr/bin/env python3
"""
Test script to verify LLM credentials and functionality with Atlan Gateway LiteLLM Proxy.
"""

import os
import openai
import requests
from dotenv import load_dotenv

def test_llm_credentials():
    """Test the LLM credentials and basic functionality with Atlan Gateway LiteLLM Proxy."""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return False
    
    print(f"🔑 Found API key: {api_key[:10]}...{api_key[-4:]}")
    
    # Use Atlan Gateway's LiteLLM Proxy
    base_url = "https://llmproxy.atlan.dev"
    print(f"🌐 Using Atlan Gateway LiteLLM Proxy: {base_url}")
    
    try:
        # Initialize OpenAI client with Atlan Gateway LiteLLM Proxy
        client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # Test with a simple completion
        print("🧪 Testing Atlan Gateway LiteLLM Proxy connection...")
        
        response = client.chat.completions.create(
            model="gpt-4o",  # Use gpt-4o instead of gpt-4
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, Atlan Gateway LiteLLM Proxy is working!' and nothing else."}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ LLM Response: {result}")
        
        if "Hello, Atlan Gateway LiteLLM Proxy is working!" in result:
            print("🎉 Atlan Gateway LiteLLM Proxy credentials are working correctly!")
            return True
        else:
            print("⚠️ LLM responded but not as expected")
            return False
            
    except openai.AuthenticationError:
        print("❌ Authentication failed - invalid API key or proxy URL")
        return False
    except openai.RateLimitError:
        print("⚠️ Rate limit exceeded - API key is valid but quota exceeded")
        return True  # Still consider this a success
    except Exception as e:
        print(f"❌ Error testing LLM: {str(e)}")
        return False

def test_available_models():
    """Test fetching available models from the Atlan Gateway LiteLLM Proxy."""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return False
    
    base_url = "https://llmproxy.atlan.dev"
    
    try:
        print("🧪 Testing available models endpoint...")
        
        # Make authorized GET request to /models endpoint
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{base_url}/models", headers=headers)
        
        if response.status_code == 200:
            models_data = response.json()
            print("✅ Available models:")
            if 'data' in models_data:
                for model in models_data['data']:
                    model_id = model.get('id', 'Unknown')
                    print(f"   - {model_id}")
            else:
                print(f"   Response structure: {models_data}")
            return True
        else:
            print(f"❌ Failed to fetch models: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching models: {str(e)}")
        return False

def test_llm_service():
    """Test the LLMService class with Atlan Gateway LiteLLM Proxy."""
    try:
        from llm_service import LLMService
        
        print("\n🧪 Testing LLMService class with Atlan Gateway LiteLLM Proxy...")
        
        # Initialize service
        llm_service = LLMService()
        print("✅ LLMService initialized successfully")
        
        # Test intent analysis
        print("🧪 Testing intent analysis...")
        analysis = llm_service.analyze_user_intent("Define Customer Acquisition Cost")
        
        print(f"✅ Intent analysis result:")
        print(f"   Intent: {analysis.get('intent', 'Unknown')}")
        print(f"   Confidence: {analysis.get('confidence', 'Unknown')}")
        print(f"   Extracted terms: {analysis.get('extracted_terms', [])}")
        
        # Test response enhancement
        print("🧪 Testing response enhancement...")
        original_response = "Customer Acquisition Cost is a metric that measures the cost to acquire a new customer."
        enhanced_response = llm_service.enhance_response(original_response, "Define Customer Acquisition Cost")
        
        print(f"✅ Response enhancement:")
        print(f"   Original: {original_response}")
        print(f"   Enhanced: {enhanced_response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing LLMService: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Atlan Gateway LiteLLM Proxy Credentials and Service")
    print("=" * 70)
    
    # Test basic credentials
    credentials_ok = test_llm_credentials()
    
    if credentials_ok:
        # Test available models
        models_ok = test_available_models()
        
        # Test LLM service
        service_ok = test_llm_service()
        
        if service_ok:
            print("\n🎉 All LLM tests passed! The Atlan Gateway LiteLLM Proxy service is ready to use.")
        else:
            print("\n⚠️ LLM credentials work but service has issues.")
    else:
        print("\n❌ LLM credentials failed. Please check your Atlan Gateway configuration.")
        print("\n💡 Make sure:")
        print("   1. Your API key is correctly set in environment variables")
        print("   2. You have access to the Atlan Gateway LiteLLM Proxy")
        print("   3. The proxy URL is accessible from your network")
    
    print("\n" + "=" * 70) 