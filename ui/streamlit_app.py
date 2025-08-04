import streamlit as st
import os
import sys
from pathlib import Path
import time
from typing import Dict, Any

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.graph.agent_graph import create_agent_graph
from src.rag.rag_service import RAGService
from src.evaluation.evaluator import ResponseEvaluator
from src.config import get_settings


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


def initialize_system():
    """Initialize the AI system components."""
    try:
        with st.spinner("Initializing AI system..."):
            # Initialize settings
            settings = get_settings()
            
            # Initialize agent
            agent = create_agent_graph()
            st.session_state.agent = agent
            
            # Initialize RAG service
            rag_service = RAGService()
            st.session_state.rag_service = rag_service
            
            # Initialize documents
            init_result = rag_service.initialize_documents("data")
            
            # Initialize evaluator
            evaluator = ResponseEvaluator()
            st.session_state.evaluator = evaluator
            
            st.session_state.system_initialized = True
            
            return {
                "success": True,
                "agent_info": agent.get_agent_info(),
                "rag_init": init_result,
                "settings": {
                    "model": settings.openai_model,
                    "temperature": settings.temperature,
                    "max_tokens": settings.max_tokens
                }
            }
            
    except Exception as e:
        st.error(f"Error initializing system: {str(e)}")
        return {"success": False, "error": str(e)}


def process_query(query: str) -> Dict[str, Any]:
    """Process a user query through the agent pipeline."""
    try:
        if not st.session_state.agent:
            return {"error": "Agent not initialized"}
        
        # Process query
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
                    classification=result.get("classification", ""),
                    evaluation_results=evaluation
                )
        
        return {
            "success": True,
            "result": result,
            "evaluation": evaluation
        }
        
    except Exception as e:
        return {"error": str(e)}


def display_system_status():
    """Display system status and information."""
    st.sidebar.header("🤖 System Status")
    
    if st.session_state.system_initialized:
        st.sidebar.success("✅ System Initialized")
        
        # Agent info
        if st.session_state.agent:
            agent_info = st.session_state.agent.get_agent_info()
            st.sidebar.subheader("Agent Information")
            st.sidebar.write(f"**Type:** {agent_info['type']}")
            st.sidebar.write(f"**Model:** {agent_info['model_info']['model']}")
            st.sidebar.write(f"**Temperature:** {agent_info['model_info']['temperature']}")
        
        # RAG status
        if st.session_state.rag_service:
            rag_status = st.session_state.rag_service.get_system_status()
            st.sidebar.subheader("RAG System")
            st.sidebar.write(f"**Vector Store:** {rag_status.get('vector_store_status', 'Unknown')}")
            if rag_status.get('collection_info'):
                st.sidebar.write(f"**Documents:** {rag_status['collection_info'].get('vectors_count', 0)}")
        
        # Evaluation metrics
        if st.session_state.evaluator:
            eval_metrics = st.session_state.evaluator.get_evaluation_metrics()
            st.sidebar.subheader("Evaluation Metrics")
            st.sidebar.write(f"**Total Evaluations:** {eval_metrics.get('total_evaluations', 0)}")
            st.sidebar.write(f"**Project:** {eval_metrics.get('project', 'N/A')}")
    
    else:
        st.sidebar.warning("⚠️ System Not Initialized")


def display_evaluation_results(evaluation: Dict[str, Any]):
    """Display evaluation results in an expander."""
    if not evaluation or not evaluation.get("success"):
        return
    
    with st.expander("📊 Response Evaluation", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if "relevance" in evaluation.get("evaluations", {}):
                relevance_score = evaluation["evaluations"]["relevance"].score
                st.metric("Relevance", f"{relevance_score:.2f}")
        
        with col2:
            if "accuracy" in evaluation.get("evaluations", {}):
                accuracy_score = evaluation["evaluations"]["accuracy"].score
                st.metric("Accuracy", f"{accuracy_score:.2f}")
        
        with col3:
            if "helpfulness" in evaluation.get("evaluations", {}):
                helpfulness_score = evaluation["evaluations"]["helpfulness"].score
                st.metric("Helpfulness", f"{helpfulness_score:.2f}")
        
        if "overall_score" in evaluation:
            st.progress(evaluation["overall_score"] / 10.0)  # Assuming 10-point scale
            st.caption(f"Overall Score: {evaluation['overall_score']:.2f}/10")


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="AI Pipeline - LangChain & LangGraph",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🤖 AI Pipeline with LangChain & LangGraph")
    st.markdown("""
    This application demonstrates an AI pipeline that combines:
    - **Weather Data Fetching** using OpenWeatherMap API
    - **RAG (Retrieval-Augmented Generation)** for document-based Q&A
    - **Intelligent Query Routing** using LangGraph
    - **Response Evaluation** using LangSmith
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Initialize system button
        if not st.session_state.system_initialized:
            if st.button("🚀 Initialize System", type="primary"):
                init_result = initialize_system()
                if init_result["success"]:
                    st.success("System initialized successfully!")
                    st.rerun()
                else:
                    st.error(f"Initialization failed: {init_result.get('error', 'Unknown error')}")
        
        # Display system status
        display_system_status()
        
        # Settings
        if st.session_state.system_initialized:
            st.subheader("📋 Settings")
            st.write("**Model:** GPT-3.5-turbo")
            st.write("**Temperature:** 0.7")
            st.write("**Max Tokens:** 1000")
            
            # Clear chat button
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.rerun()
    
    # Main content area
    if not st.session_state.system_initialized:
        st.info("👆 Please initialize the system using the button in the sidebar.")
        return
    
    # Chat interface
    st.header("💬 Chat Interface")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Display evaluation if available
            if message.get("evaluation"):
                display_evaluation_results(message["evaluation"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything (weather or document questions)..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Process query
        with st.chat_message("assistant"):
            with st.spinner("Processing your query..."):
                result = process_query(prompt)
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    response = result["result"]["response"]
                    st.write(response)
                    
                    # Display classification
                    classification = result["result"].get("classification", "")
                    if classification:
                        st.caption(f"📊 Query classified as: **{classification.upper()}**")
                    
                    # Display sources for RAG queries
                    if classification == "rag" and result["result"].get("rag_result", {}).get("sources"):
                        sources = result["result"]["rag_result"]["sources"]
                        st.caption(f"📚 Sources: {', '.join(sources)}")
                    
                    # Add assistant message to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "evaluation": result.get("evaluation")
                    })
                    
                    # Display evaluation
                    if result.get("evaluation"):
                        display_evaluation_results(result["evaluation"])
    
    # Example queries
    st.markdown("---")
    st.subheader("💡 Example Queries")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🌤️ Weather Queries:**")
        st.markdown("- What's the weather in New York?")
        st.markdown("- Temperature in London")
        st.markdown("- Weather forecast for Tokyo")
    
    with col2:
        st.markdown("**📚 Document Queries:**")
        st.markdown("- What is machine learning?")
        st.markdown("- Explain quantum computing")
        st.markdown("- How does neural networks work?")


if __name__ == "__main__":
    main() 