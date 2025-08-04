#!/usr/bin/env python3
"""Test script to verify improved Gemini integration."""

import os
from src.llm.llm_service import LLMService

def test_comprehensive_query():
    """Test with a more comprehensive query."""
    try:
        llm_service = LLMService()
        
        # Test with more comprehensive context
        test_context = [
            {
                "page_content": "LangChain, LangGraph, Hugging Face, LoRA (PEFT), RAG, FAISS, Prompt Engineering, Data Visualization, MLflow",
                "metadata": {"source": "skills"}
            },
            {
                "page_content": "Samsung R&D Institute India - Software Engineer, Machine Learning Engineer",
                "metadata": {"source": "experience"}
            },
            {
                "page_content": "Deep Learning, Computer Vision, AWS EC2, GPU acceleration, real-time analytics",
                "metadata": {"source": "projects"}
            }
        ]
        
        queries = [
            "What technical skills does Rahul have?",
            "Tell me about Rahul's work experience", 
            "What projects has Rahul worked on?"
        ]
        
        for query in queries:
            print(f"\n--- Testing: {query} ---")
            response = llm_service.process_query_with_context(query, test_context)
            print(f"Response: {response}")
            print("-" * 50)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_comprehensive_query()
