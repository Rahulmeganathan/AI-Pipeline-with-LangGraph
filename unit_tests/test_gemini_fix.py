#!/usr/bin/env python3
"""Test script to verify Gemini integration is working."""

import os
from src.llm.llm_service import LLMService

def test_gemini_simple():
    """Test a simple Gemini call."""
    try:
        llm_service = LLMService()
        
        # Test with simple context
        test_context = [
            {
                "page_content": "LangChain, LangGraph, Hugging Face, LoRA (PEFT), RAG, FAISS, Prompt Engineering, Data Visualization, MLflow",
                "metadata": {"source": "resume"}
            }
        ]
        
        query = "What technical skills does this person have?"
        
        print("Testing Gemini with resume context...")
        response = llm_service.process_query_with_context(query, test_context)
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_simple()
