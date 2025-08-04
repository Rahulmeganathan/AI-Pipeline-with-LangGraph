#!/usr/bin/env python3
"""Test script to verify the updated RAG service."""

import os
from src.rag.rag_service import RAGService

def test_rag_service():
    """Test the updated RAG service."""
    try:
        rag_service = RAGService()
        
        # Test with simulated context (like what would come from vector store)
        test_context = [
            {
                "page_content": "LangChain, LangGraph, Hugging Face, LoRA (PEFT), RAG, FAISS, Prompt Engineering, Data Visualization, MLflow",
                "metadata": {"source": "resume"}
            },
            {
                "page_content": "Samsung R&D Institute India - Software Engineer, Machine Learning Engineer",
                "metadata": {"source": "resume"}
            }
        ]
        
        print("Testing RAG service with updated LLM integration...")
        response = rag_service.generate_rag_response("What technical skills does Rahul have?", test_context)
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_service()
