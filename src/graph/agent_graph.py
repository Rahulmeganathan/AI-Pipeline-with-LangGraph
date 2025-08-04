from typing import Dict, Any, List, TypedDict, Annotated
from datetime import datetime
import asyncio
import nest_asyncio
from langgraph.graph import StateGraph, END
from langgraph.graph import START
from langchain.schema import Document
from src.weather.weather_service import WeatherService
from src.rag.rag_service import RAGService
from src.llm.llm_service import LLMService
from src.config import get_settings
from src.langsmith_integration import init_langsmith, is_langsmith_enabled

# Apply nest_asyncio to handle nested event loops
nest_asyncio.apply()


class AgentState(TypedDict):
    """State for the LangGraph agent."""
    query: str
    classification: str
    weather_result: Dict[str, Any]
    rag_result: Dict[str, Any]
    final_response: str
    error: str


class AgentGraph:
    """LangGraph agent that routes queries between weather and RAG services."""
    
    def __init__(self):
        self.settings = get_settings()
        
        # Initialize LangSmith tracing
        self.langsmith_enabled = init_langsmith()
        
        self.weather_service = WeatherService()
        self.rag_service = RAGService()
        self.llm_service = LLMService()
        
        # Initialize the graph
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph state machine."""
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_query", self._classify_query)
        workflow.add_node("process_weather", self._process_weather)
        workflow.add_node("process_rag", self._process_rag)
        workflow.add_node("enhance_response", self._enhance_response)
        workflow.add_node("handle_error", self._handle_error)
        
        # Add edges
        workflow.add_edge(START, "classify_query")
        workflow.add_conditional_edges(
            "classify_query",
            self._route_query,
            {
                "weather": "process_weather",
                "rag": "process_rag",
                "error": "handle_error"
            }
        )
        workflow.add_edge("process_weather", "enhance_response")
        workflow.add_edge("process_rag", "enhance_response")
        workflow.add_edge("enhance_response", END)
        workflow.add_edge("handle_error", END)
        
        return workflow
    
    def _classify_query(self, state: AgentState) -> AgentState:
        """Classify the query as weather or RAG."""
        try:
            query = state["query"]
            classification = self.llm_service.classify_query(query)
            
            return {
                **state,
                "classification": classification
            }
        except Exception as e:
            return {
                **state,
                "classification": "error",
                "error": f"Error classifying query: {str(e)}"
            }
    
    def _route_query(self, state: AgentState) -> str:
        """Route the query based on classification."""
        classification = state.get("classification", "rag")
        
        if classification == "weather":
            return "weather"
        elif classification == "rag":
            return "rag"
        else:
            return "error"
    
    def _process_weather(self, state: AgentState) -> AgentState:
        """Process weather queries."""
        try:
            query = state["query"]
            result = self.weather_service.process_weather_query(query)
            
            return {
                **state,
                "weather_result": result
            }
        except Exception as e:
            return {
                **state,
                "weather_result": {"error": str(e)},
                "error": f"Error processing weather query: {str(e)}"
            }
    
    def _process_rag(self, state: AgentState) -> AgentState:
        """Process RAG queries."""
        try:
            query = state["query"]
            result = self.rag_service.process_rag_query(query)
            
            return {
                **state,
                "rag_result": result
            }
        except Exception as e:
            return {
                **state,
                "rag_result": {"error": str(e)},
                "error": f"Error processing RAG query: {str(e)}"
            }
    
    def _enhance_response(self, state: AgentState) -> AgentState:
        """Enhance the final response using LLM."""
        try:
            # Determine which result to use
            weather_result = state.get("weather_result", {})
            rag_result = state.get("rag_result", {})
            
            if weather_result and not weather_result.get("error"):
                # Use weather result
                response = weather_result.get("response", "No weather data available")
            elif rag_result and not rag_result.get("error"):
                # Use RAG result
                response = rag_result.get("response", "No document information available")
            else:
                # Handle error case
                error_msg = weather_result.get("error", "") or rag_result.get("error", "")
                response = f"Unable to process your query. Error: {error_msg}"
            
            # Enhance response with LLM
            enhanced_response = self.llm_service.enhance_response(
                original_response=response,
                query=state["query"]
            )
            
            return {
                **state,
                "final_response": enhanced_response
            }
            
        except Exception as e:
            return {
                **state,
                "final_response": f"Error enhancing response: {str(e)}",
                "error": str(e)
            }
    
    def _handle_error(self, state: AgentState) -> AgentState:
        """Handle errors in the pipeline."""
        error_msg = state.get("error", "Unknown error occurred")
        return {
            **state,
            "final_response": f"Sorry, I encountered an error: {error_msg}",
            "error": error_msg
        }
    
    def _store_processed_response(self, query: str, response: str, classification: str) -> bool:
        """Store processed response in vector database without overwriting existing documents."""
        try:
            # Create document for the processed response with special metadata
            document = Document(
                page_content=response,
                metadata={
                    "source": "ai_response",
                    "query": query,
                    "classification": classification,
                    "timestamp": datetime.now().isoformat(),
                    "type": "processed_response",
                    "model": self.llm_service.get_model_info()["model"]
                }
            )
            
            # Store using the new responses method that doesn't clear existing documents
            success = self.rag_service.vector_store.store_responses([document])
            
            if success:
                print(f"✅ Stored AI response in vector database alongside existing documents")
            else:
                print(f"⚠️  Failed to store AI response in vector database")
            
            return success
            
        except Exception as e:
            print(f"❌ Error storing AI response: {str(e)}")
            return False
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query through the agent pipeline."""
        try:
            # Initialize state
            initial_state = AgentState(
                query=query,
                classification="",
                weather_result={},
                rag_result={},
                final_response="",
                error=""
            )
            
            # Compile the graph
            app = self.graph.compile()
            
            # Run the graph (nest_asyncio handles the async issues)
            result = app.invoke(initial_state)
            
            # Store the processed data (final response) in vector database
            final_response = result.get("final_response", "")
            if final_response and not result.get("error"):
                self._store_processed_response(
                    query=query,
                    response=final_response,
                    classification=result.get("classification", "")
                )
            
            # Extract relevant information
            response = {
                "query": query,
                "classification": result.get("classification", ""),
                "response": final_response,
                "weather_result": result.get("weather_result", {}),
                "rag_result": result.get("rag_result", {}),
                "error": result.get("error", ""),
                "stored_in_vector_db": final_response and not result.get("error")
            }
            
            return response
            
        except Exception as e:
            return {
                "query": query,
                "classification": "error",
                "response": f"Error in agent pipeline: {str(e)}",
                "weather_result": {},
                "rag_result": {},
                "error": str(e),
                "stored_in_vector_db": False
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent."""
        return {
            "type": "LangGraph Agent",
            "services": ["Weather Service", "RAG Service", "LLM Service"],
            "capabilities": [
                "Query Classification", 
                "Weather Data", 
                "Document Search", 
                "Response Enhancement",
                "Processed Data Storage"  # ✅ New capability
            ],
            "model_info": self.llm_service.get_model_info()
        }


def create_agent_graph() -> AgentGraph:
    """Create and return an agent graph instance."""
    return AgentGraph() 