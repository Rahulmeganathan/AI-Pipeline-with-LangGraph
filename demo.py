#!/usr/bin/env python3
"""
Demo script for the AI Pipeline with LangChain, LangGraph, and LangSmith.
This script demonstrates the core functionality without requiring all API keys.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.graph.agent_graph import create_agent_graph
from src.rag.rag_service import RAGService
from src.weather.weather_service import WeatherService
from src.llm.llm_service import LLMService


def demo_without_api_keys():
    """Demo the system components without requiring API keys."""
    print("🤖 AI Pipeline Demo (Without API Keys)")
    print("=" * 50)
    
    # Test weather service
    print("\n1. Testing Weather Service...")
    weather_service = WeatherService()
    
    # Test location extraction
    test_queries = [
        "What's the weather in New York?",
        "Temperature in London",
        "Weather forecast for Tokyo",
        "What is machine learning?"  # Non-weather query
    ]
    
    for query in test_queries:
        location = weather_service.extract_location_from_query(query)
        print(f"Query: '{query}' -> Location: {location}")
    
    # Test RAG service
    print("\n2. Testing RAG Service...")
    rag_service = RAGService()
    
    # Test query classification
    rag_test_queries = [
        "What is machine learning?",
        "Explain neural networks",
        "How does deep learning work?",
        "What's the weather in Paris?"  # Non-RAG query
    ]
    
    for query in rag_test_queries:
        is_rag = rag_service.is_rag_query(query)
        print(f"Query: '{query}' -> RAG Query: {is_rag}")
    
    # Test LLM service
    print("\n3. Testing LLM Service...")
    llm_service = LLMService()
    
    # Test query classification
    for query in test_queries + rag_test_queries:
        try:
            classification = llm_service.classify_query(query)
            print(f"Query: '{query}' -> Classification: {classification}")
        except Exception as e:
            print(f"Query: '{query}' -> Classification: Error (API key required)")
    
    print("\n✅ Demo completed successfully!")
    print("\nTo run the full system, you need to:")
    print("1. Set up your API keys in a .env file")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the Streamlit UI: streamlit run ui/streamlit_app.py")


def demo_with_mocks():
    """Demo with mocked API responses."""
    print("🤖 AI Pipeline Demo (With Mocked Responses)")
    print("=" * 50)
    
    # Mock weather data
    from src.weather.weather_service import WeatherData
    
    mock_weather_data = WeatherData(
        location="New York",
        temperature=22.5,
        description="partly cloudy",
        humidity=65,
        wind_speed=4.2,
        pressure=1013,
        feels_like=24.0,
        visibility=10
    )
    
    print("\n1. Mock Weather Response:")
    weather_service = WeatherService()
    formatted_response = weather_service.format_weather_response(mock_weather_data)
    print(formatted_response)
    
    # Mock RAG response
    print("\n2. Mock RAG Response:")
    mock_rag_context = [
        {
            "content": "Machine learning is a subset of artificial intelligence that enables computers to learn from data.",
            "metadata": {"source": "sample_document.txt"}
        }
    ]
    
    print("Context: Machine learning is a subset of artificial intelligence...")
    print("Query: What is machine learning?")
    print("Response: Machine learning is a field of AI that enables computers to learn from data without being explicitly programmed.")
    
    print("\n✅ Mock demo completed!")


def main():
    """Main demo function."""
    print("🚀 AI Pipeline Demo")
    print("Choose demo mode:")
    print("1. Demo without API keys (tests core functionality)")
    print("2. Demo with mocked responses")
    
    try:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        
        if choice == "1":
            demo_without_api_keys()
        elif choice == "2":
            demo_with_mocks()
        else:
            print("Invalid choice. Running demo without API keys...")
            demo_without_api_keys()
            
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError during demo: {str(e)}")


if __name__ == "__main__":
    main() 