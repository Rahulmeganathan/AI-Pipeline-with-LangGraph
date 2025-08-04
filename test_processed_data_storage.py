#!/usr/bin/env python3
"""
Test script to verify that processed data (final responses) are stored in vector database.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_processed_data_storage():
    """Test that processed data is stored in vector database."""
    
    print("🧪 Testing Processed Data Storage in Vector Database")
    print("=" * 60)
    
    # Check environment variables
    google_api_key = os.getenv("GOOGLE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not google_api_key and not openai_api_key:
        print("❌ No API keys found!")
        print("Please set either GOOGLE_API_KEY or OPENAI_API_KEY in your .env file")
        return False
    
    print(f"✅ Google API Key: {'Set' if google_api_key else 'Not set'}")
    print(f"✅ OpenAI API Key: {'Set' if openai_api_key else 'Not set'}")
    
    try:
        # Test agent graph
        from src.graph.agent_graph import create_agent_graph
        agent = create_agent_graph()
        print(f"✅ Agent Graph initialized successfully")
        
        # Test queries that should generate processed data
        test_queries = [
            "What's the weather like in New York?",
            "Tell me about machine learning from the documents",
            "How hot is it in London today?"
        ]
        
        print(f"\n🔍 Testing {len(test_queries)} queries...")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Test {i}: {query[:50]}... ---")
            
            try:
                result = agent.process_query(query)
                
                print(f"✅ Query processed successfully")
                print(f"   - Classification: {result.get('classification', 'N/A')}")
                print(f"   - Response length: {len(result.get('response', ''))} chars")
                print(f"   - Stored in vector DB: {result.get('stored_in_vector_db', False)}")
                print(f"   - Error: {result.get('error', 'None')}")
                
                if result.get('stored_in_vector_db'):
                    print("   ✅ Processed data stored in vector database!")
                else:
                    print("   ⚠️  Processed data NOT stored (may be due to error)")
                
            except Exception as e:
                print(f"❌ Error processing query: {str(e)}")
        
        # Test vector store to see stored data
        print(f"\n🔍 Checking vector database for stored processed data...")
        try:
            from src.rag.vector_store import VectorStore
            vector_store = VectorStore()
            
            # Search for processed responses
            results = vector_store.search_similar("processed_response", k=10)
            
            processed_responses = [r for r in results if r.get('metadata', {}).get('source') == 'processed_response']
            
            print(f"✅ Found {len(processed_responses)} processed responses in vector database")
            
            for i, result in enumerate(processed_responses[:3], 1):
                metadata = result.get('metadata', {})
                print(f"   {i}. Query: {metadata.get('query', 'N/A')[:30]}...")
                print(f"      Classification: {metadata.get('classification', 'N/A')}")
                print(f"      Model: {metadata.get('model', 'N/A')}")
                print(f"      Timestamp: {metadata.get('timestamp', 'N/A')}")
                print(f"      Content length: {len(result.get('content', ''))} chars")
            
        except Exception as e:
            print(f"❌ Error checking vector database: {str(e)}")
        
        print(f"\n🎉 Processed data storage test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_processed_data_storage() 