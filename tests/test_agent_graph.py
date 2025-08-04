import pytest
from unittest.mock import Mock, patch, MagicMock
from src.graph.agent_graph import AgentGraph, AgentState


class TestAgentGraph:
    """Test cases for AgentGraph."""
    
    @pytest.fixture
    def agent_graph(self):
        """Create an AgentGraph instance for testing."""
        with patch('src.config.get_settings') as mock_settings:
            mock_settings.return_value.openai_api_key = "test_api_key"
            mock_settings.return_value.openai_model = "gpt-3.5-turbo"
            mock_settings.return_value.temperature = 0.7
            mock_settings.return_value.max_tokens = 1000
            return AgentGraph()
    
    def test_classify_query_weather(self, agent_graph):
        """Test query classification for weather queries."""
        with patch.object(agent_graph.llm_service, 'classify_query') as mock_classify:
            mock_classify.return_value = "weather"
            
            state = AgentState(
                query="What's the weather in New York?",
                classification="",
                weather_result={},
                rag_result={},
                final_response="",
                error=""
            )
            
            result = agent_graph._classify_query(state)
            
            assert result["classification"] == "weather"
            assert result["query"] == "What's the weather in New York?"
    
    def test_classify_query_rag(self, agent_graph):
        """Test query classification for RAG queries."""
        with patch.object(agent_graph.llm_service, 'classify_query') as mock_classify:
            mock_classify.return_value = "rag"
            
            state = AgentState(
                query="What is machine learning?",
                classification="",
                weather_result={},
                rag_result={},
                final_response="",
                error=""
            )
            
            result = agent_graph._classify_query(state)
            
            assert result["classification"] == "rag"
            assert result["query"] == "What is machine learning?"
    
    def test_classify_query_error(self, agent_graph):
        """Test query classification with error."""
        with patch.object(agent_graph.llm_service, 'classify_query') as mock_classify:
            mock_classify.side_effect = Exception("Classification error")
            
            state = AgentState(
                query="Test query",
                classification="",
                weather_result={},
                rag_result={},
                final_response="",
                error=""
            )
            
            result = agent_graph._classify_query(state)
            
            assert result["classification"] == "error"
            assert "Classification error" in result["error"]
    
    def test_route_query_weather(self, agent_graph):
        """Test query routing for weather classification."""
        state = AgentState(
            query="Weather query",
            classification="weather",
            weather_result={},
            rag_result={},
            final_response="",
            error=""
        )
        
        result = agent_graph._route_query(state)
        assert result == "weather"
    
    def test_route_query_rag(self, agent_graph):
        """Test query routing for RAG classification."""
        state = AgentState(
            query="RAG query",
            classification="rag",
            weather_result={},
            rag_result={},
            final_response="",
            error=""
        )
        
        result = agent_graph._route_query(state)
        assert result == "rag"
    
    def test_route_query_error(self, agent_graph):
        """Test query routing for error classification."""
        state = AgentState(
            query="Error query",
            classification="error",
            weather_result={},
            rag_result={},
            final_response="",
            error=""
        )
        
        result = agent_graph._route_query(state)
        assert result == "error"
    
    def test_route_query_default(self, agent_graph):
        """Test query routing with default classification."""
        state = AgentState(
            query="Default query",
            classification="",
            weather_result={},
            rag_result={},
            final_response="",
            error=""
        )
        
        result = agent_graph._route_query(state)
        assert result == "rag"  # Default to RAG
    
    @patch.object(AgentGraph, '_process_weather')
    def test_process_weather_success(self, mock_process_weather, agent_graph):
        """Test successful weather processing."""
        mock_process_weather.return_value = {
            "type": "weather",
            "success": True,
            "response": "Weather data for New York"
        }
        
        state = AgentState(
            query="What's the weather in New York?",
            classification="weather",
            weather_result={},
            rag_result={},
            final_response="",
            error=""
        )
        
        result = agent_graph._process_weather(state)
        
        assert result["weather_result"]["success"] is True
        assert "Weather data for New York" in result["final_response"]
    
    @patch.object(AgentGraph, '_process_weather')
    def test_process_weather_error(self, mock_process_weather, agent_graph):
        """Test weather processing with error."""
        mock_process_weather.side_effect = Exception("Weather API error")
        
        state = AgentState(
            query="What's the weather in Tokyo?",
            classification="weather",
            weather_result={},
            rag_result={},
            final_response="",
            error=""
        )
        
        result = agent_graph._process_weather(state)
        
        assert "Weather API error" in result["final_response"]
        assert "Weather API error" in result["weather_result"]["error"]
    
    @patch.object(AgentGraph, '_process_rag')
    def test_process_rag_success(self, mock_process_rag, agent_graph):
        """Test successful RAG processing."""
        mock_process_rag.return_value = {
            "type": "rag",
            "success": True,
            "response": "Machine learning is a subset of AI"
        }
        
        state = AgentState(
            query="What is machine learning?",
            classification="rag",
            weather_result={},
            rag_result={},
            final_response="",
            error=""
        )
        
        result = agent_graph._process_rag(state)
        
        assert result["rag_result"]["success"] is True
        assert "Machine learning is a subset of AI" in result["final_response"]
    
    @patch.object(AgentGraph, '_process_rag')
    def test_process_rag_error(self, mock_process_rag, agent_graph):
        """Test RAG processing with error."""
        mock_process_rag.side_effect = Exception("RAG processing error")
        
        state = AgentState(
            query="What is AI?",
            classification="rag",
            weather_result={},
            rag_result={},
            final_response="",
            error=""
        )
        
        result = agent_graph._process_rag(state)
        
        assert "RAG processing error" in result["final_response"]
        assert "RAG processing error" in result["rag_result"]["error"]
    
    def test_enhance_response_success(self, agent_graph):
        """Test successful response enhancement."""
        with patch.object(agent_graph.llm_service, 'enhance_response') as mock_enhance:
            mock_enhance.return_value = "Enhanced response"
            
            state = AgentState(
                query="Test query",
                classification="weather",
                weather_result={},
                rag_result={},
                final_response="Original response",
                error=""
            )
            
            result = agent_graph._enhance_response(state)
            
            assert result["final_response"] == "Enhanced response"
    
    def test_enhance_response_error(self, agent_graph):
        """Test response enhancement with error."""
        with patch.object(agent_graph.llm_service, 'enhance_response') as mock_enhance:
            mock_enhance.side_effect = Exception("Enhancement error")
            
            state = AgentState(
                query="Test query",
                classification="weather",
                weather_result={},
                rag_result={},
                final_response="Original response",
                error=""
            )
            
            result = agent_graph._enhance_response(state)
            
            # Should keep original response on error
            assert result["final_response"] == "Original response"
    
    def test_handle_error(self, agent_graph):
        """Test error handling."""
        state = AgentState(
            query="Test query",
            classification="error",
            weather_result={},
            rag_result={},
            final_response="",
            error="Test error message"
        )
        
        result = agent_graph._handle_error(state)
        
        assert "Test error message" in result["final_response"]
        assert "encountered an error" in result["final_response"]
    
    @patch('src.graph.agent_graph.StateGraph')
    def test_create_graph(self, mock_state_graph, agent_graph):
        """Test graph creation."""
        mock_graph = Mock()
        mock_state_graph.return_value = mock_graph
        
        # The graph should be created with proper nodes and edges
        assert agent_graph.graph is not None
    
    @patch.object(AgentGraph, '_classify_query')
    @patch.object(AgentGraph, '_process_weather')
    @patch.object(AgentGraph, '_enhance_response')
    def test_process_query_success(self, mock_enhance, mock_weather, mock_classify, agent_graph):
        """Test successful query processing through the pipeline."""
        # Mock the graph compilation and execution
        mock_app = Mock()
        mock_app.invoke.return_value = {
            "query": "What's the weather in London?",
            "classification": "weather",
            "final_response": "Weather data for London",
            "weather_result": {"success": True},
            "rag_result": {},
            "error": ""
        }
        
        with patch.object(agent_graph.graph, 'compile') as mock_compile:
            mock_compile.return_value = mock_app
            
            result = agent_graph.process_query("What's the weather in London?")
            
            assert result["query"] == "What's the weather in London?"
            assert result["classification"] == "weather"
            assert "Weather data for London" in result["response"]
            assert result["weather_result"]["success"] is True
    
    def test_process_query_error(self, agent_graph):
        """Test query processing with error."""
        with patch.object(agent_graph.graph, 'compile') as mock_compile:
            mock_compile.side_effect = Exception("Graph compilation error")
            
            result = agent_graph.process_query("Test query")
            
            assert result["classification"] == "error"
            assert "Graph compilation error" in result["response"]
    
    def test_get_agent_info(self, agent_graph):
        """Test agent information retrieval."""
        info = agent_graph.get_agent_info()
        
        assert info["type"] == "LangGraph Agent"
        assert "Weather Service" in info["services"]
        assert "RAG Service" in info["services"]
        assert "Query Classification" in info["capabilities"]
        assert "Weather Data" in info["capabilities"]


def test_create_agent_graph():
    """Test agent graph creation function."""
    with patch('src.config.get_settings'):
        agent = create_agent_graph()
        assert isinstance(agent, AgentGraph)


if __name__ == "__main__":
    pytest.main([__file__]) 