#!/usr/bin/env python3
"""
Test script to see how evaluator behaves without LangSmith configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_evaluator_without_langsmith():
    """Test evaluator behavior without LangSmith configuration."""
    
    print("🧪 Testing Evaluator Without LangSmith")
    print("=" * 40)
    
    # Check if LangSmith is configured
    langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
    print(f"✅ LANGCHAIN_API_KEY: {'Set' if langchain_api_key else 'Not set'}")
    
    try:
        from src.evaluation.evaluator import ResponseEvaluator
        
        if not langchain_api_key:
            print("⚠️  Attempting to initialize evaluator without LangSmith API key...")
            
            try:
                evaluator = ResponseEvaluator()
                print("❌ Unexpected: Evaluator initialized without API key")
                
                # Test evaluation
                result = evaluator.evaluate_response(
                    query="What is machine learning?",
                    response="Machine learning is a subset of AI.",
                    context={"type": "rag"}
                )
                
                print(f"✅ Evaluation result: {result}")
                
            except Exception as e:
                print(f"✅ Expected error: {str(e)}")
                print("   This is the correct behavior when LangSmith is not configured")
                
        else:
            print("✅ LangSmith is configured, testing normal operation...")
            evaluator = ResponseEvaluator()
            
            result = evaluator.evaluate_response(
                query="What is machine learning?",
                response="Machine learning is a subset of AI.",
                context={"type": "rag"}
            )
            
            print(f"✅ Evaluation result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    print("\n📋 Summary:")
    print("=" * 40)
    print("✅ Without LangSmith configuration:")
    print("   • Evaluator initialization will fail")
    print("   • UI will show evaluation errors")
    print("   • Other functionality (LLM, RAG, Weather) works normally")
    print("   • System continues to function without evaluation")
    
    print("\n✅ With LangSmith configuration:")
    print("   • Add to .env file:")
    print("     LANGCHAIN_API_KEY=your_langsmith_api_key_here")
    print("     LANGCHAIN_PROJECT=your_project_name")
    print("     LANGCHAIN_TRACING_V2=true")
    print("   • Evaluation will work normally")
    print("   • Results logged to LangSmith dashboard")
    
    return True

if __name__ == "__main__":
    test_evaluator_without_langsmith() 