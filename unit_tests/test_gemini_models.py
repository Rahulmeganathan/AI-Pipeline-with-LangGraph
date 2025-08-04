#!/usr/bin/env python3
"""
Script to test and list available Gemini models using LangChain Google GenAI.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def test_gemini_models():
    """Test available Gemini models."""
    
    # Check if GOOGLE_API_KEY is set
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("Please set your Google API key:")
        print("export GOOGLE_API_KEY=your_api_key_here")
        return
    
    print("✅ GOOGLE_API_KEY found")
    
    # List of models to test
    models_to_test = [
        "gemini-1.5-flash",
        "gemini-1.5-pro", 
        "gemini-pro",
        "gemini-pro-vision"
    ]
    
    print("\nTesting Gemini Models:")
    print("=" * 40)
    
    for model in models_to_test:
        try:
            print(f"\n🔍 Testing model: {model}")
            
            # Test chat model
            llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=api_key,
                temperature=0.1,
                max_tokens=100
            )
            
            # Simple test
            response = llm.invoke("Say 'Hello' in one word")
            print(f"✅ {model} - Chat working: {response.content}")
            
        except Exception as e:
            print(f"❌ {model} - Error: {str(e)}")
    
    # Test embeddings
    print("\n🔍 Testing embeddings...")
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        
        # Test embedding
        test_text = "Hello world"
        embedding = embeddings.embed_query(test_text)
        print(f"✅ Embeddings working: {len(embedding)} dimensions")
        
    except Exception as e:
        print(f"❌ Embeddings error: {str(e)}")
    
    print("\n" + "=" * 40)
    print("Recommended models for your AI pipeline:")
    print("• gemini-1.5-flash: Fast and efficient for most tasks")
    print("• gemini-1.5-pro: Better reasoning for complex queries")
    print("• gemini-pro: General purpose (fallback)")
    print("• models/embedding-001: For embeddings")

if __name__ == "__main__":
    test_gemini_models() 