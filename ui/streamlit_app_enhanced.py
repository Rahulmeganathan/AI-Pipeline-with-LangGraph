#!/usr/bin/env python3
"""
Enhanced Streamlit app with dynamic PDF upload functionality.
"""

import streamlit as st
import os
import sys
import tempfile
import shutil
from pathlib import Path
import time
from typing import Dict, Any
import uuid
from langsmith.run_helpers import traceable
from langsmith import Client

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.graph.agent_graph import create_agent_graph
from src.rag.rag_service import RAGService
from src.evaluation.evaluator import ResponseEvaluator
from src.config import get_settings
from src.langsmith_integration import init_langsmith, is_langsmith_enabled

# Initialize LangSmith tracing
init_langsmith()

# Initialize LangSmith client
client = Client()


def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "agent" not in st.session_state:
        st.session_state.agent = None
    
    if "rag_service" not in st.session_state:
        st.session_state.rag_service = None
    
    if "evaluator" not in st.session_state:
        st.session_state.evaluator = None
    
    if "system_initialized" not in st.session_state:
        st.session_state.system_initialized = False
    
    if "uploaded_documents" not in st.session_state:
        st.session_state.uploaded_documents = []
    
    if "user_data_dir" not in st.session_state:
        st.session_state.user_data_dir = None


def create_user_data_directory():
    """Create a unique data directory for the current session."""
    if not st.session_state.user_data_dir:
        # Create unique directory for this session
        session_id = str(uuid.uuid4())[:8]
        user_data_dir = f"temp_data_{session_id}"
        
        # Create directory
        Path(user_data_dir).mkdir(exist_ok=True)
        st.session_state.user_data_dir = user_data_dir
    
    return st.session_state.user_data_dir


def handle_pdf_upload(uploaded_files):
    """Handle PDF file uploads and process them."""
    if not uploaded_files:
        return {"success": False, "message": "No files uploaded"}
    
    try:
        # Create user data directory
        user_data_dir = create_user_data_directory()
        
        uploaded_docs = []
        
        for uploaded_file in uploaded_files:
            if uploaded_file.type == "application/pdf":
                # Save uploaded PDF to user data directory
                file_path = Path(user_data_dir) / uploaded_file.name
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                uploaded_docs.append({
                    "name": uploaded_file.name,
                    "size": uploaded_file.size,
                    "path": str(file_path)
                })
                
                st.success(f"✅ Uploaded: {uploaded_file.name}")
        
        # Update session state
        st.session_state.uploaded_documents.extend(uploaded_docs)
        
        # Process documents with RAG service
        if st.session_state.rag_service and uploaded_docs:
            with st.spinner("Processing uploaded documents..."):
                init_result = st.session_state.rag_service.initialize_documents(user_data_dir)
                
                if init_result["success"]:
                    st.success(f"✅ Processed {len(uploaded_docs)} documents successfully!")
                    return {
                        "success": True,
                        "message": f"Processed {len(uploaded_docs)} documents",
                        "documents": uploaded_docs,
                        "rag_result": init_result
                    }
                else:
                    st.error(f"❌ Failed to process documents: {init_result['error']}")
                    return {
                        "success": False,
                        "message": f"Failed to process documents: {init_result['error']}"
                    }
        
        return {"success": True, "message": f"Uploaded {len(uploaded_docs)} documents"}
        
    except Exception as e:
        st.error(f"❌ Error uploading documents: {str(e)}")
        return {"success": False, "message": f"Error: {str(e)}"}


def initialize_system():
    """Initialize the AI system components."""
    try:
        with st.spinner("Initializing AI system..."):
            # Initialize settings
            settings = get_settings()
            
            # Debugging: Verify settings attributes
            print(settings.dict())
            
            # Initialize agent
            agent = create_agent_graph()
            st.session_state.agent = agent
            
            # Initialize RAG service
            rag_service = RAGService()
            st.session_state.rag_service = rag_service
            
            # Initialize evaluator
            evaluator = ResponseEvaluator()
            st.session_state.evaluator = evaluator
            
            st.session_state.system_initialized = True
            
            return {
                "success": True,
                "agent_info": agent.get_agent_info(),
                "settings": {
                    "model": settings.gemini_model if settings.google_api_key else settings.openai_model,
                    "temperature": settings.temperature,
                    "max_tokens": settings.max_tokens
                }
            }
            
    except Exception as e:
        st.error(f"Error initializing system: {str(e)}")
        return {"success": False, "error": str(e)}


@traceable(project_name="Weather+PDF")
def process_query(query: str) -> Dict[str, Any]:
    """Process a user query through the agent pipeline."""
    try:
        if not st.session_state.agent:
            return {"error": "Agent not initialized"}
            result = st.session_state.agent.process_query(query)
            
            # Evaluate response if evaluator is available
            evaluation = None
            if st.session_state.evaluator and result.get("response"):
                evaluation = st.session_state.evaluator.evaluate_response(
                    query=query,
                    response=result["response"],
                    context={
                        "classification": result.get("classification", ""),
                        "weather_result": result.get("weather_result", {}),
                        "rag_result": result.get("rag_result", {})
                    }
                )
                
                # Log evaluation
                if evaluation.get("success"):
                    st.session_state.evaluator.log_evaluation(
                        query=query,
                        response=result["response"],
                        evaluation=evaluation
                    )
            
        result = st.session_state.agent.process_query(query)
        
        # Evaluate response if evaluator is available
        evaluation = None
        if st.session_state.evaluator and result.get("response"):
            evaluation = st.session_state.evaluator.evaluate_response(
                query=query,
                response=result["response"],
                context={
                    "classification": result.get("classification", ""),
                    "weather_result": result.get("weather_result", {}),
                    "rag_result": result.get("rag_result", {})
                }
            )
            
            # Log evaluation
            if evaluation.get("success"):
                st.session_state.evaluator.log_evaluation(
                    query=query,
                    response=result["response"],
                    evaluation=evaluation
                )
        
        return {
            **result,
            "evaluation": evaluation
        }
        
    except Exception as e:
        return {"error": f"Error processing query: {str(e)}"}


def display_system_status():
    """Display system status and information."""
    if st.session_state.system_initialized:
        st.sidebar.success("✅ System Initialized")
        
        # Display agent info
        if st.session_state.agent:
            agent_info = st.session_state.agent.get_agent_info()
            st.sidebar.subheader(" Agent Capabilities")
            for capability in agent_info["capabilities"]:
                st.sidebar.write(f"• {capability}")
        
        # Display uploaded documents
        if st.session_state.uploaded_documents:
            st.sidebar.subheader(" Uploaded Documents")
            for doc in st.session_state.uploaded_documents:
                st.sidebar.write(f"• {doc['name']}")
    else:
        st.sidebar.warning("⚠️ System Not Initialized")


def display_evaluation_results(evaluation: Dict[str, Any]):
    """Display evaluation results."""
    if evaluation and evaluation.get("success"):
        st.subheader("📊 Response Evaluation")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Relevance", f"{evaluation.get('relevance_score', 0):.2f}")
        
        with col2:
            st.metric("Accuracy", f"{evaluation.get('accuracy_score', 0):.2f}")
        
        with col3:
            st.metric("Helpfulness", f"{evaluation.get('helpfulness_score', 0):.2f}")
        
        # Display detailed evaluation
        with st.expander("📋 Detailed Evaluation"):
            st.json(evaluation)


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="AI Pipeline with LangChain, LangGraph, and LangSmith",
        page_icon="",
        layout="wide"
    )
    
    st.title("🤖 AI Pipeline with LangChain, LangGraph, and LangSmith")
    st.markdown("---")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar
    st.sidebar.title("⚙️ System Controls")
    
    # Initialize system
    if not st.session_state.system_initialized:
        if st.sidebar.button("🚀 Initialize System"):
            result = initialize_system()
            if result["success"]:
                st.success("✅ System initialized successfully!")
                st.rerun()
            else:
                st.error(f"❌ Failed to initialize: {result['error']}")
    
    # Display system status
    display_system_status()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Chat Interface")
        
        # PDF Upload Section
        st.markdown("### 📄 Upload PDF Documents")
        uploaded_files = st.file_uploader(
            "Choose PDF files to upload",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload PDF documents to enable RAG queries about their content"
        )
        
        if uploaded_files:
            if st.button("📤 Process Uploaded Documents"):
                result = handle_pdf_upload(uploaded_files)
                if result["success"]:
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result["message"])
        
        # Chat interface
        st.markdown("### 💬 Ask Questions")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Display evaluation if available
                if message.get("evaluation"):
                    display_evaluation_results(message["evaluation"])
        
        # Chat input
        if prompt := st.chat_input("Ask a question about your documents or get weather info..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process query
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    result = process_query(prompt)
                    
                    if result.get("error"):
                        st.error(result["error"])
                    else:
                        response = result.get("response", "No response generated")
                        st.markdown(response)
                        
                        # Add assistant message to chat history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response,
                            "evaluation": result.get("evaluation")
                        })
                        
                        # Display evaluation
                        if result.get("evaluation"):
                            display_evaluation_results(result["evaluation"])
    
    with col2:
        st.subheader("ℹ️ System Information")
        
        if st.session_state.system_initialized:
            # Display system info
            st.info("✅ System is running")
            
            # Display uploaded documents
            if st.session_state.uploaded_documents:
                st.markdown("** Uploaded Documents:**")
                for doc in st.session_state.uploaded_documents:
                    st.write(f"• {doc['name']}")
            
            # Clear chat button
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.rerun()
            
            # Clear documents button
            if st.button("📄 Clear Documents"):
                st.session_state.uploaded_documents = []
                if st.session_state.user_data_dir and Path(st.session_state.user_data_dir).exists():
                    shutil.rmtree(st.session_state.user_data_dir)
                st.session_state.user_data_dir = None
                st.rerun()
        else:
            st.warning("⚠️ System not initialized")


if __name__ == "__main__":
    main()