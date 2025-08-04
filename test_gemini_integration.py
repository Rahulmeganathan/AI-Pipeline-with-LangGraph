#!/usr/bin/env python3
"""
Test script to verify Gemini integration with the AI pipeline.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_integration():
    """Test Gemini integration with the AI pipeline."""
    
    print("🧪 Testing Gemini Integration")
    print("=" * 40)
    
    # Check environment variables
    google_api_key = os.getenv("GOOGLE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not google_api_key and not openai_api_key:
        print("❌ No API keys found!")
        print("Please set either GOOGLE_API_KEY or OPENAI_API_KEY in your .env file")
        return False
    
    print(f"✅ Google API Key: {'Set' if google_api_key else 'Not set'}")
    print(f"✅ OpenAI API Key: {'Set' if openai_api_key else 'Not set'}")
    
    # Test configuration
    try:
        from src.config import get_settings
        settings = get_settings()
        print(f"✅ Configuration loaded successfully")
        print(f"   - Gemini Model: {settings.gemini_model}")
        print(f"   - OpenAI Model: {settings.openai_model}")
        
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        return False
    
    # Test LLM service
    try:
        from src.llm.llm_service import LLMService
        llm_service = LLMService()
        print(f"✅ LLM Service initialized with provider: {llm_service.llm_provider}")
        
        # Test simple query
        response = llm_service.classify_query("What's the weather like?")
        print(f"✅ LLM query classification working: {response}")
        
    except Exception as e:
        print(f"❌ LLM Service error: {str(e)}")
        return False
    
    # Test RAG service
    try:
        from src.rag.rag_service import RAGService
        rag_service = RAGService()
        print(f"✅ RAG Service initialized with provider: {rag_service.llm_provider}")
        
    except Exception as e:
        print(f"❌ RAG Service error: {str(e)}")
        return False
    
    # Test vector store
    try:
        from src.rag.vector_store import VectorStore
        vector_store = VectorStore()
        print(f"✅ Vector Store initialized with provider: {vector_store.embedding_provider}")
        print(f"   - Embedding dimension: {vector_store.embedding_dimension}")
        
    except Exception as e:
        print(f"❌ Vector Store error: {str(e)}")
        return False
    
    print("\n🎉 All tests passed! Gemini integration is working correctly.")
    return True

if __name__ == "__main__":
    test_gemini_integration() 