#!/usr/bin/env python3
"""
Script to list available Gemini models for LangChain integration.
"""

import os
from typing import List

def list_gemini_models():
    """List available Gemini models for LangChain integration."""
    
    print("Available Gemini Models for LangChain Integration:")
    print("=" * 50)
    
    # Core Gemini models
    print("\n1. Gemini Pro Models:")
    print("   - gemini-pro: General purpose model for text generation")
    print("   - gemini-pro-vision: Multimodal model for text and image")
    
    print("\n2. Gemini Flash Models (Faster, more efficient):")
    print("   - gemini-1.5-flash: Fast and efficient for most tasks")
    print("   - gemini-1.5-flash-exp: Experimental version with extended capabilities")
    
    print("\n3. Gemini Advanced Models:")
    print("   - gemini-1.5-pro: Advanced model with better reasoning")
    print("   - gemini-1.5-pro-exp: Experimental advanced model")
    
    print("\n4. Gemini Ultra Models:")
    print("   - gemini-1.5-ultra: Most capable model (if available)")
    print("   - gemini-1.5-ultra-exp: Experimental ultra model")
    
    print("\nRecommended Models for Different Use Cases:")
    print("=" * 50)
    print("• General Purpose (Chat, Q&A): gemini-1.5-flash")
    print("• Complex Reasoning: gemini-1.5-pro")
    print("• Multimodal (Text + Images): gemini-pro-vision")
    print("• Fast Responses: gemini-1.5-flash")
    print("• Best Performance: gemini-1.5-pro")
    
    print("\nNote: Model availability may depend on your Google AI Studio access level.")
    print("For LangChain integration, you'll need to install: pip install langchain-google-genai")

if __name__ == "__main__":
    list_gemini_models() 