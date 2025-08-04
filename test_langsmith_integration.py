#!/usr/bin/env python3
"""Test script to verify LangSmith integration."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.langsmith_integration import init_langsmith, is_langsmith_enabled, get_langsmith_config
from src.llm.llm_service import LLMService
from src.graph.agent_graph import AgentGraph
from src.evaluation.evaluator import ResponseEvaluator


def test_langsmith_config():
    """Test LangSmith configuration."""
    print("🔍 Testing LangSmith Configuration...")
    
    # Test configuration
    config = get_langsmith_config()
    print(f"  API Key Present: {'Yes' if config['api_key'] else 'No'}")
    print(f"  Project Name: {config['project']}")
    print(f"  Tracing Enabled: {config['tracing_enabled']}")
    
    # Test initialization
    success = init_langsmith()
    print(f"  Initialization: {'✅ Success' if success else '❌ Failed'}")
    
    return success


def test_langsmith_integration():
    """Test LangSmith integration in components."""
    print("\n🔍 Testing LangSmith Integration in Components...")
    
    try:
        # Test LLM Service
        print("  Testing LLM Service...")
        llm_service = LLMService()
        print(f"    LangSmith enabled: {llm_service.langsmith_enabled}")
        
        # Test Agent Graph
        print("  Testing Agent Graph...")
        agent_graph = AgentGraph()
        print(f"    LangSmith enabled: {agent_graph.langsmith_enabled}")
        
        # Test Evaluator
        print("  Testing Response Evaluator...")
        evaluator = ResponseEvaluator()
        print(f"    LangSmith client configured: {evaluator.client is not None}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Error: {str(e)}")
        return False


def test_langsmith_tracing():
    """Test LangSmith tracing with a simple query."""
    print("\n🔍 Testing LangSmith Tracing with Sample Query...")
    
    try:
        if not is_langsmith_enabled():
            print("    ⚠️ LangSmith not enabled - skipping tracing test")
            return True
        
        # Initialize agent
        agent = AgentGraph()
        
        # Test query
        test_query = "What are Rahul's technical skills?"
        print(f"    Query: {test_query}")
        
        # This should be traced in LangSmith if enabled
        result = agent.process_query(test_query)
        print(f"    Response generated: {'✅ Yes' if result else '❌ No'}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Error during tracing test: {str(e)}")
        return False


def test_evaluation_integration():
    """Test evaluation integration with LangSmith."""
    print("\n🔍 Testing Evaluation Integration...")
    
    try:
        evaluator = ResponseEvaluator()
        
        # Test evaluation
        test_data = {
            "query": "What programming languages does Rahul know?",
            "response": "Rahul is proficient in Python, JavaScript, and C++.",
            "context": {"source": "resume"}
        }
        
        evaluation = evaluator.evaluate_response(
            test_data["query"], 
            test_data["response"], 
            test_data["context"]
        )
        
        print(f"    Evaluation successful: {'✅ Yes' if evaluation.get('success') else '❌ No'}")
        
        if evaluation.get("success"):
            print(f"    Overall score: {evaluation.get('overall_score', 0):.2f}")
            
        return evaluation.get('success', False)
        
    except Exception as e:
        print(f"    ❌ Error during evaluation test: {str(e)}")
        return False


def main():
    """Run all LangSmith integration tests."""
    print("🚀 LangSmith Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_langsmith_config),
        ("Component Integration", test_langsmith_integration),
        ("Tracing", test_langsmith_tracing),
        ("Evaluation", test_evaluation_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with error: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All LangSmith integration tests passed!")
    else:
        print("⚠️ Some tests failed. Check your LangSmith configuration.")


if __name__ == "__main__":
    main()
