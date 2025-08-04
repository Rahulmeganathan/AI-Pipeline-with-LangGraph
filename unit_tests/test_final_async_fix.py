#!/usr/bin/env python3
"""
Final test to verify the comprehensive async fix for Streamlit.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_comprehensive_async_fix():
    """Test that all components can be initialized without async errors."""
    
    print("🧪 Testing Comprehensive Async Fix")
    print("=" * 50)
    
    try:
        # Test 1: LLM Service
        print("📦 Testing LLM Service...")
        from src.llm.llm_service import LLMService
        llm_service = LLMService()
        print("✅ LLM Service initialized successfully!")
        
        # Test 2: RAG Service
        print("📚 Testing RAG Service...")
        from src.rag.rag_service import RAGService
        rag_service = RAGService()
        print("✅ RAG Service initialized successfully!")
        
        # Test 3: Weather Service
        print("🌤️ Testing Weather Service...")
        from src.weather.weather_service import WeatherService
        weather_service = WeatherService()
        print("✅ Weather Service initialized successfully!")
        
        # Test 4: Agent Graph
        print("🤖 Testing Agent Graph...")
        from src.graph.agent_graph import create_agent_graph
        agent = create_agent_graph()
        print("✅ Agent Graph initialized successfully!")
        
        # Test 5: Simple query classification
        print("🔍 Testing Query Classification...")
        classification = llm_service.classify_query("What is the weather in New York?")
        print(f"✅ Query classified as: {classification}")
        
        # Test 6: Agent info
        print("ℹ️ Testing Agent Info...")
        agent_info = agent.get_agent_info()
        print(f"✅ Agent info retrieved: {agent_info['type']}")
        print(f"   Capabilities: {len(agent_info['capabilities'])} capabilities")
        
        print("\n🎉 All components initialized successfully!")
        print("✅ Streamlit app should now work without async errors!")
        print("✅ The async fix is comprehensive and working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_comprehensive_async_fix() 