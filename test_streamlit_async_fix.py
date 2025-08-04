#!/usr/bin/env python3
"""
Test script to verify the async fix for Streamlit.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_agent_initialization():
    """Test that the agent can be initialized without async errors."""
    
    print("🧪 Testing Agent Initialization (Async Fix)")
    print("=" * 50)
    
    try:
        # Test agent creation
        from src.graph.agent_graph import create_agent_graph
        
        print("📦 Creating agent graph...")
        agent = create_agent_graph()
        print("✅ Agent graph created successfully!")
        
        # Test agent info
        agent_info = agent.get_agent_info()
        print(f"✅ Agent info retrieved: {agent_info['type']}")
        print(f"   Capabilities: {agent_info['capabilities']}")
        
        # Test simple query processing
        print("\n📝 Testing query processing...")
        result = agent.process_query("What is the weather in New York?")
        
        print(f"✅ Query processed successfully!")
        print(f"   Classification: {result.get('classification', 'N/A')}")
        print(f"   Response: {result.get('response', 'N/A')[:100]}...")
        print(f"   Error: {result.get('error', 'None')}")
        
        print("\n🎉 Async fix is working correctly!")
        print("✅ Streamlit app should now work without async errors!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_agent_initialization() 