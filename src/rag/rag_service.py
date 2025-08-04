from typing import List, Dict, Any, Optional, Union
import nest_asyncio
from src.config import get_settings
from src.rag.document_processor import DocumentProcessor
from src.rag.vector_store import VectorStore
from src.llm.llm_service import LLMService

# Apply nest_asyncio to handle nested event loops
nest_asyncio.apply()


class RAGService:
    """RAG (Retrieval-Augmented Generation) service."""
    
    def __init__(self):
        self.settings = get_settings()
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        
        # Use our fixed LLM service instead of separate Gemini instance
        self.llm_service = LLMService()
    
    def initialize_documents(self, data_dir: str = "data") -> Dict[str, Any]:
        """Initialize the RAG system by processing and storing documents."""
        try:
            print("Initializing RAG system...")
            
            # Process documents
            chunks = self.document_processor.process_documents(data_dir)
            
            if not chunks:
                return {
                    "success": False,
                    "error": "No documents found to process",
                    "summary": {}
                }
            
            # Store in vector database
            success = self.vector_store.store_documents(chunks)
            
            if not success:
                return {
                    "success": False,
                    "error": "Failed to store documents in vector database",
                    "summary": {}
                }
            
            # Get summary
            summary = self.document_processor.get_document_summary(chunks)
            collection_info = self.vector_store.get_collection_info()
            
            return {
                "success": True,
                "summary": summary,
                "collection_info": collection_info,
                "message": f"Successfully processed {len(chunks)} document chunks"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "summary": {}
            }
    
    def is_rag_query(self, query: str) -> bool:
        """Determine if a query should be handled by RAG."""
        # Simple keyword-based classification
        # In a real application, you might use a more sophisticated classifier
        rag_keywords = [
            "what is", "explain", "tell me about", "how does", "define",
            "describe", "information about", "details about", "learn about"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in rag_keywords)
    
    def generate_rag_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generate a RAG response based on retrieved context."""
        try:
            if not context:
                return "I don't have enough information to answer your question. Please try rephrasing or ask about something else."
            
            # Prepare context text with validation
            context_parts = []
            for item in context:
                if isinstance(item, dict):
                    content = item.get('content', item.get('page_content', ''))
                    source = item.get('metadata', {}).get('source', 'Unknown')
                    if content and content.strip():  # Only add non-empty content
                        context_parts.append(f"Source: {source}\nContent: {content}")
                else:
                    # Handle case where item might be a Document object
                    if hasattr(item, 'page_content') and item.page_content.strip():
                        source = getattr(item, 'metadata', {}).get('source', 'Unknown')
                        context_parts.append(f"Source: {source}\nContent: {item.page_content}")
            
            if not context_parts:
                return "I found some relevant documents but couldn't extract readable content. Please try rephrasing your question."
            
            context_text = "\n\n".join(context_parts)
            
            # Validate inputs before calling LLM
            if not query.strip():
                return "Please provide a valid question."
            
            if not context_text.strip():
                return "I found relevant documents but couldn't extract meaningful content."
            
            # Generate response using our fixed LLM service
            response = self.llm_service.process_query_with_context(query, context)
            
            # Validate the response
            if not response or not response.strip():
                return "I was able to find relevant information but had trouble generating a response. Please try rephrasing your question."
            
            return response
            
        except Exception as e:
            print(f"Error generating RAG response: {str(e)}")
            return f"I encountered an error while processing your question: {str(e)}. Please try again with a different question."
    
    def process_rag_query(self, query: str) -> Dict[str, Any]:
        """Process a RAG query and return the response."""
        try:
            # Search for relevant documents
            search_results = self.vector_store.search_documents(query, k=3)
            
            print(f"DEBUG: Search results count: {len(search_results)}")
            if search_results:
                print(f"DEBUG: First result keys: {list(search_results[0].keys())}")
                print(f"DEBUG: First result content preview: {str(search_results[0])[:200]}...")
            
            if not search_results:
                return {
                    "success": False,
                    "response": "I couldn't find any relevant information to answer your question. Please try rephrasing your query or ask about a different topic.",
                    "sources": [],
                    "error": "No relevant documents found"
                }
            
            # Generate response
            response = self.generate_rag_response(query, search_results)
            
            # Extract sources
            sources = [
                item.get('metadata', {}).get('source', 'Unknown')
                for item in search_results
            ]
            
            return {
                "success": True,
                "response": response,
                "sources": sources,
                "context": search_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"Error processing RAG query: {str(e)}",
                "sources": [],
                "error": str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the current status of the RAG system."""
        try:
            collection_info = self.vector_store.get_collection_info()
            
            return {
                "status": "operational",
                "model": self.settings.gemini_model,
                "provider": "Google Gemini",
                "collection_info": collection_info,
                "vector_store_initialized": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "vector_store_initialized": False
            } 