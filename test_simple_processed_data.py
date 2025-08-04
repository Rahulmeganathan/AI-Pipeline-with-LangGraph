#!/usr/bin/env python3
"""
Simple test to verify processed data storage in vector database.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_simple_processed_data():
    """Test processed data storage without enhancement."""
    
    print("🧪 Simple Test: Processed Data Storage")
    print("=" * 50)
    
    # Check environment variables
    google_api_key = os.getenv("GOOGLE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not google_api_key and not openai_api_key:
        print("❌ No API keys found!")
        return False
    
    try:
        # Test vector store directly
        from src.rag.vector_store import VectorStore
        from langchain.schema import Document
        from datetime import datetime
        
        vector_store = VectorStore()
        print("✅ Vector Store initialized")
        
        # Create a test processed response document
        test_document = Document(
            page_content="This is a test processed response about weather in New York. The temperature is 72°F with sunny conditions.",
            metadata={
                "source": "processed_response",
                "query": "What's the weather in New York?",
                "classification": "weather",
                "timestamp": datetime.now().isoformat(),
                "type": "ai_response",
                "model": "gemini-1.5-flash"
            }
        )
        
        # Store the document
        print("📝 Storing test processed response...")
        success = vector_store.store_documents([test_document])
        
        if success:
            print("✅ Test processed response stored successfully!")
            
            # Try to search for it
            print("🔍 Searching for stored processed response...")
            results = vector_store.search_similar("processed response", k=5)
            
            processed_responses = [r for r in results if r.get('metadata', {}).get('source') == 'processed_response']
            
            if processed_responses:
                print(f"✅ Found {len(processed_responses)} processed responses in vector database")
                for i, result in enumerate(processed_responses, 1):
                    metadata = result.get('metadata', {})
                    print(f"   {i}. Query: {metadata.get('query', 'N/A')}")
                    print(f"      Classification: {metadata.get('classification', 'N/A')}")
                    print(f"      Model: {metadata.get('model', 'N/A')}")
                    print(f"      Content: {result.get('content', '')[:100]}...")
            else:
                print("⚠️  No processed responses found in search results")
        else:
            print("❌ Failed to store test processed response")
            
        return success
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_simple_processed_data() 