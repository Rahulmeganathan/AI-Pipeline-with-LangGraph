# 🤖 AI Pipeline with Local LLM, RAG, and LangSmith Integration

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://python.langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)](https://streamlit.io/)
[![LangSmith](https://img.shields.io/badge/LangSmith-Integrated-purple.svg)](https://smith.langchain.com/)

A comprehensive AI pipeline that combines **local LLM processing** (Ollama), **RAG capabilities**, **intelligent query routing**, and **LangSmith monitoring** for document-based question answering and weather queries.

## ✨ Features

### 🔄 **Intelligent Query Routing**
- **LangGraph-based decision making** for weather vs RAG queries
- **Automatic classification** of user intents
- **Seamless workflow orchestration**

### 📚 **Advanced RAG System**
- **Dynamic PDF upload** and processing
- **Local embeddings** (HuggingFace all-MiniLM-L6-v2)
- **Smart response storage** without overwriting source documents
- **Vector similarity search** with Qdrant Cloud

### 🏠 **Fully Local LLM Processing**
- **Ollama integration** (llama3.2:latest)
- **No external API dependencies** for LLM calls
- **Local embeddings** for complete privacy
- **Cost-effective** local processing

### 🌦️ **Weather Integration**
- **Real-time weather data** via OpenWeatherMap API
- **Location-based queries**
- **Seamless integration** with the RAG pipeline

### 📊 **LangSmith Monitoring**
- **Complete tracing** of all operations
- **Response quality evaluation**
- **Performance monitoring**
- **Comprehensive analytics**

### 🖥️ **User-Friendly Interface**
- **Streamlit web app** with modern UI
- **Real-time chat interface**
- **Dynamic PDF upload**
- **Response evaluation display**

## 🏗️ Architecture

```
User Query → LangGraph Router → [Weather Service | RAG Service] → Response Enhancement → LangSmith Evaluation
                 ↓                                    ↓
            Classification                    Document Processing
                 ↓                                    ↓
            Route Decision                   Vector Store Search
                                                     ↓
                                             Ollama LLM Processing
```

## 📁 Project Structure

```
LangGraph_querying/
├── 📁 src/                          # Core application code
│   ├── 🔧 config.py                 # Configuration management
│   ├── 🤖 langsmith_integration.py  # LangSmith tracing setup
│   ├── 📁 weather/                  # Weather service module
│   │   ├── __init__.py
│   │   └── weather_service.py       # OpenWeatherMap API integration
│   ├── 📁 rag/                      # RAG implementation
│   │   ├── __init__.py
│   │   ├── document_processor.py    # PDF processing
│   │   ├── vector_store.py          # Qdrant vector operations
│   │   └── rag_service.py           # RAG orchestration
│   ├── 📁 llm/                      # LLM services
│   │   ├── __init__.py
│   │   └── llm_service.py           # Ollama integration
│   ├── 📁 graph/                    # LangGraph workflows
│   │   ├── __init__.py
│   │   └── agent_graph.py           # Query routing logic
│   └── 📁 evaluation/               # Response evaluation
│       ├── __init__.py
│       └── evaluator.py             # LangSmith evaluation
├── 📁 tests/                        # Test suite
│   ├── __init__.py
│   ├── test_weather_service.py
│   ├── test_rag_service.py
│   ├── test_agent_graph.py
│   └── test_langsmith_integration.py
├── 📁 ui/                           # User interface
│   ├── streamlit_app.py
│   └── streamlit_app_enhanced.py    # Enhanced version with PDF upload
├── 📁 data/                         # Sample data
│   └── sample_document.txt
├── 📄 requirements.txt              # Python dependencies
├── 📄 .env.example                  # Environment variables template
├── 📄 LANGSMITH_INTEGRATION.md      # LangSmith setup guide
└── 📄 README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** installed
- **Ollama** installed and running locally
- **Git** for cloning the repository

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/LangGraph_querying.git
cd LangGraph_querying
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install and Setup Ollama

```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/download

# Pull the required model
ollama pull llama3.2:latest
```

### 4. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys (see Configuration section below)
```

### 5. Run the Application

```bash
# Start the enhanced Streamlit app
streamlit run ui/streamlit_app_enhanced.py --server.port 8501
```

Visit `http://localhost:8501` in your browser to access the application.

## ⚙️ Configuration

Create a `.env` file in the root directory with the following variables:

```env
# LangSmith Configuration (Required for monitoring)
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=your_project_name
LANGCHAIN_TRACING_V2=true

# OpenWeatherMap API (Required for weather queries)
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Qdrant Vector Database (Required for RAG)
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key

# Optional: Google Gemini (fallback embeddings)
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

### Getting API Keys

1. **LangSmith**: Sign up at [smith.langchain.com](https://smith.langchain.com)
2. **OpenWeatherMap**: Get your key at [openweathermap.org](https://openweathermap.org/api)
3. **Qdrant**: Create a cluster at [cloud.qdrant.io](https://cloud.qdrant.io)
4. **Google Gemini** (optional): Get your key at [aistudio.google.com](https://aistudio.google.com)

## 🎯 Usage Examples

### RAG Queries (Document-based)
```
"What are Rahul's technical skills?"
"Tell me about the experience at Samsung R&D"
"What programming languages are mentioned in the resume?"
```

### Weather Queries
```
"What's the weather in London?"
"Tell me the forecast for New York"
"How's the weather in Tokyo today?"
```

### Smart Routing
The system automatically detects query intent and routes to the appropriate service:
- Document/knowledge queries → RAG pipeline
- Weather-related queries → Weather service

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Test all components
python -m pytest tests/ -v

# Test specific components
python test_langsmith_integration.py
python test_rag_service.py

# Test with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## 📊 Monitoring with LangSmith

The application includes comprehensive monitoring:

1. **Automatic Tracing**: All LLM calls and workflows are traced
2. **Response Evaluation**: Quality metrics for all responses
3. **Performance Analytics**: Latency and throughput monitoring
4. **Error Tracking**: Detailed error logs and debugging

Access your dashboard at [smith.langchain.com](https://smith.langchain.com) after configuring your API key.

For detailed setup instructions, see [LANGSMITH_INTEGRATION.md](LANGSMITH_INTEGRATION.md).

## 🔧 Advanced Configuration

### Custom Ollama Models

To use a different Ollama model, update `src/llm/llm_service.py`:

```python
self.llm = ChatOllama(
    model="your-preferred-model",  # e.g., "mistral", "codellama"
    base_url="http://localhost:11434",
    temperature=0.3
)
```

### Custom Embeddings

To use different embeddings, update `src/rag/vector_store.py`:

```python
from sentence_transformers import SentenceTransformer

# Use a different embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="your-preferred-model"  # e.g., "all-mpnet-base-v2"
)
```

### Environment-Specific Projects

Use different LangSmith projects for different environments:

```env
# Development
LANGCHAIN_PROJECT=ai_pipeline_dev

# Staging
LANGCHAIN_PROJECT=ai_pipeline_staging

# Production
LANGCHAIN_PROJECT=ai_pipeline_prod
```

## Setup Instructions

### 1. Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd LangGraph_querying
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI Configuration (Optional - can use Gemini instead)
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini Configuration
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# LangSmith Configuration
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=your_project_name
LANGCHAIN_TRACING_V2=true

# OpenWeatherMap Configuration
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Qdrant Configuration
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
```

### 3. API Keys Setup

1. **Google Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey) (Recommended)
2. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/) (Optional fallback)
3. **LangSmith API Key**: Get from [LangSmith](https://smith.langchain.com/)
4. **OpenWeatherMap API Key**: Get from [OpenWeatherMap](https://openweathermap.org/api)
5. **Qdrant Cloud**: Set up a free account at [Qdrant Cloud](https://cloud.qdrant.io/)

### 4. Sample Document

Place a PDF document in the `data/` directory for RAG functionality. The system will automatically process and embed the document.

## Usage

### Running the Streamlit UI

```bash
streamlit run ui/streamlit_app.py
```

### Running Tests

```bash
pytest tests/ -v
```

### Running Individual Components

```python
from src.graph.agent_graph import create_agent_graph
from src.config import get_settings

# Initialize the agent
graph = create_agent_graph()
app = graph.compile()

# Process a query
result = app.invoke({"query": "What's the weather in New York?"})
print(result)
```

## Implementation Details

### 1. LangGraph Agent Architecture

The agent uses a decision-making node that routes queries to either:
- **Weather Service**: For weather-related queries
- **RAG Service**: For document-based questions

### 2. Vector Database Integration

- Uses Qdrant Cloud for document embeddings
- Automatic document processing and chunking
- Semantic search capabilities

### 3. LangSmith Evaluation

- Response quality evaluation
- Performance monitoring
- Trace logging for debugging

### 4. Testing Strategy

- Unit tests for all services
- Mock API responses
- Integration tests for the complete pipeline

## 🛠️ Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Ollama not responding** | Ensure Ollama is running: `ollama serve` |
| **Model not found** | Pull the model: `ollama pull llama3.2:latest` |
| **LangSmith traces not appearing** | Check your API key and project name in `.env` |
| **Vector store connection failed** | Verify Qdrant URL and API key |
| **Weather API errors** | Confirm OpenWeatherMap API key is valid |

### Performance Optimization

- **Embedding Model**: Use smaller models like `all-MiniLM-L6-v2` for faster processing
- **Chunk Size**: Adjust `CHUNK_SIZE` in config for optimal retrieval
- **Ollama Model**: Use quantized models for better performance on limited hardware

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain** for the excellent framework
- **LangSmith** for monitoring and evaluation capabilities
- **Ollama** for local LLM inference
- **Qdrant** for vector database services
- **Streamlit** for the user interface framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/LangGraph_querying/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/LangGraph_querying/discussions)
- **Documentation**: [LangSmith Integration Guide](LANGSMITH_INTEGRATION.md)

---

## 🔥 Key Features Highlight

- ✅ **100% Local LLM Processing** - No external API calls for text generation
- ✅ **Smart Document Storage** - Preserves original PDFs while learning from responses
- ✅ **Comprehensive Monitoring** - Full LangSmith integration with tracing and evaluation
- ✅ **Intelligent Query Routing** - Automatic classification and appropriate service selection
- ✅ **Cost Effective** - Minimal API usage, primarily local processing
- ✅ **Privacy Focused** - Local embeddings and processing for sensitive documents
- ✅ **Production Ready** - Comprehensive testing, monitoring, and error handling

**Built with ❤️ for AI enthusiasts and developers looking for a complete, local RAG solution with enterprise-grade monitoring.** 