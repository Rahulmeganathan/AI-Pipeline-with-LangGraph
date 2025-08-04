#!/usr/bin/env python3
"""
Test script to check LangSmith configuration requirements.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_langsmith_config():
    """Test LangSmith configuration requirements."""
    
    print("🧪 Testing LangSmith Configuration")
    print("=" * 40)
    
    # Check current environment variables
    langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
    langchain_project = os.getenv("LANGCHAIN_PROJECT", "ai_pipeline_demo")
    langchain_tracing_v2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
    
    print(f"✅ LANGCHAIN_API_KEY: {'Set' if langchain_api_key else 'Not set'}")
    print(f"✅ LANGCHAIN_PROJECT: {langchain_project}")
    print(f"✅ LANGCHAIN_TRACING_V2: {langchain_tracing_v2}")
    
    # Test configuration loading
    try:
        from src.config import get_settings
        settings = get_settings()
        print(f"✅ Configuration loaded successfully")
        print(f"   - LangChain API Key: {'Set' if settings.langchain_api_key else 'Not set'}")
        print(f"   - LangChain Project: {settings.langchain_project}")
        print(f"   - LangChain Tracing V2: {settings.langchain_tracing_v2}")
        
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        return False
    
    # Test evaluator initialization
    try:
        from src.evaluation.evaluator import ResponseEvaluator
        
        if not settings.langchain_api_key:
            print("⚠️  LangChain API Key not set - evaluator will fail")
            print("   This is expected behavior when LangSmith is not configured")
            return True
        
        evaluator = ResponseEvaluator()
        print(f"✅ Evaluator initialized successfully")
        
        # Test a simple evaluation
        test_result = evaluator.evaluate_response(
            query="What is machine learning?",
            response="Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
            context={"type": "rag"}
        )
        
        if test_result.get("success"):
            print(f"✅ Evaluation test successful")
            print(f"   - Overall Score: {test_result.get('overall_score', 'N/A')}")
        else:
            print(f"❌ Evaluation test failed: {test_result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Evaluator error: {str(e)}")
        if "api_key" in str(e).lower():
            print("   This is expected when LangSmith API key is not set")
        return False
    
    print("\n📋 LangSmith Configuration Summary:")
    print("=" * 40)
    print("Required for full functionality:")
    print("• LANGCHAIN_API_KEY - Your LangSmith API key")
    print("• LANGCHAIN_PROJECT - Project name (defaults to 'ai_pipeline_demo')")
    print("• LANGCHAIN_TRACING_V2 - Tracing enabled (defaults to 'true')")
    
    print("\n🔧 To enable LangSmith evaluation:")
    print("1. Get API key from https://smith.langchain.com/")
    print("2. Add to your .env file:")
    print("   LANGCHAIN_API_KEY=your_langsmith_api_key_here")
    print("   LANGCHAIN_PROJECT=your_project_name")
    print("   LANGCHAIN_TRACING_V2=true")
    
    print("\n⚠️  Without LangSmith:")
    print("• Evaluation will fail gracefully")
    print("• Other functionality (LLM, RAG, Weather) will work normally")
    print("• UI will show evaluation errors but continue working")
    
    return True

if __name__ == "__main__":
    test_langsmith_config() 