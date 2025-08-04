"""LangSmith integration module for tracing and monitoring."""

import os
from typing import Optional
from src.config import get_settings


def init_langsmith() -> bool:
    """Initialize LangSmith tracing."""
    try:
        settings = get_settings()
        
        if settings.langchain_api_key:
            # Set environment variables for LangSmith
            os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
            os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
            os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langchain_tracing_v2).lower()
            
            print(f"✅ LangSmith tracing initialized for project: {settings.langchain_project}")
            return True
        else:
            print("⚠️ LangSmith API key not found. Tracing disabled.")
            return False
            
    except Exception as e:
        print(f"❌ Failed to initialize LangSmith: {e}")
        return False


def get_langsmith_config() -> dict:
    """Get LangSmith configuration."""
    settings = get_settings()
    return {
        "api_key": settings.langchain_api_key,
        "project": settings.langchain_project,
        "tracing_enabled": settings.langchain_tracing_v2 and bool(settings.langchain_api_key)
    }


def is_langsmith_enabled() -> bool:
    """Check if LangSmith is properly configured and enabled."""
    config = get_langsmith_config()
    return config["tracing_enabled"]
