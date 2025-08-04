# LangSmith Integration Guide

## Overview

This project has comprehensive LangSmith integration for tracing, monitoring, and evaluating your AI pipeline. LangSmith helps you debug, monitor, and optimize your LLM applications.

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# LangSmith Configuration
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=ai_pipeline_demo
LANGCHAIN_TRACING_V2=true
```

### Project Setup

1. **Get LangSmith API Key**: Sign up at [smith.langchain.com](https://smith.langchain.com) and get your API key
2. **Set Environment Variables**: Add the variables above to your `.env` file
3. **Configure Project Name**: Set `LANGCHAIN_PROJECT` to your desired project name

## Features

### 1. Automatic Tracing

- **LLM Calls**: All Ollama LLM interactions are automatically traced
- **Agent Execution**: LangGraph agent workflows are tracked
- **RAG Pipeline**: Document retrieval and processing is monitored
- **Vector Operations**: Embeddings and vector store operations are logged

### 2. Response Evaluation

The integrated `ResponseEvaluator` provides:

- **Relevance Scoring**: Measures how well responses match queries
- **Accuracy Assessment**: Evaluates factual correctness
- **Helpfulness Rating**: Assesses response utility
- **Overall Metrics**: Composite scoring across all dimensions

### 3. Performance Monitoring

Track key metrics:
- Response latency
- Query classification accuracy
- RAG retrieval effectiveness
- Overall system performance

## Usage

### Basic Tracing

Tracing is automatically enabled when you initialize any component:

```python
from src.graph.agent_graph import AgentGraph
from src.llm.llm_service import LLMService

# LangSmith tracing starts automatically
agent = AgentGraph()
llm_service = LLMService()
```

### Manual Evaluation

```python
from src.evaluation.evaluator import ResponseEvaluator

evaluator = ResponseEvaluator()

# Evaluate a response
result = evaluator.evaluate_response(
    query="What are Rahul's technical skills?",
    response="Rahul has expertise in Python, machine learning, and cloud computing.",
    context={"source": "resume"}
)

print(f"Overall score: {result['overall_score']}")
print(f"Relevance: {result['evaluations']['relevance']['score']}")
```

### Batch Evaluation

```python
# Evaluate multiple responses
batch_data = [
    {
        "query": "What programming languages does Rahul know?",
        "response": "Rahul is proficient in Python and JavaScript.",
        "context": {"source": "resume"}
    },
    # ... more queries
]

results = evaluator.evaluate_batch(batch_data)
summary = evaluator.get_evaluation_summary(results)
```

## Integration Points

### 1. LLM Service (`src/llm/llm_service.py`)

- Initializes LangSmith tracing
- Tracks all Ollama model interactions
- Logs query classification and response enhancement

### 2. Agent Graph (`src/graph/agent_graph.py`)

- Traces complete workflow execution
- Monitors routing decisions
- Logs response storage operations

### 3. RAG Service (`src/rag/rag_service.py`)

- Tracks document processing
- Monitors vector similarity searches
- Logs context retrieval

### 4. Vector Store (`src/rag/vector_store.py`)

- Traces embedding operations
- Monitors document storage
- Logs query performance

## Monitoring Dashboard

Access your LangSmith dashboard at [smith.langchain.com](https://smith.langchain.com) to:

1. **View Traces**: See detailed execution flows
2. **Analyze Performance**: Monitor latency and throughput
3. **Debug Issues**: Identify bottlenecks and errors
4. **Track Usage**: Monitor API calls and costs

## Testing

Run the comprehensive test suite:

```bash
python test_langsmith_integration.py
```

This tests:
- Configuration setup
- Component integration
- Tracing functionality
- Evaluation system

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```
   ⚠️ LangSmith API key not found. Tracing disabled.
   ```
   - Check your `.env` file has `LANGCHAIN_API_KEY`
   - Ensure the API key is valid

2. **Project Not Found**
   - Create the project in your LangSmith dashboard
   - Update `LANGCHAIN_PROJECT` in your `.env` file

3. **Tracing Not Appearing**
   - Verify `LANGCHAIN_TRACING_V2=true` in your environment
   - Check network connectivity
   - Ensure you're using the correct project name

### Debug Mode

Enable detailed logging:

```python
import os
os.environ["LANGCHAIN_VERBOSE"] = "true"
```

## Best Practices

1. **Project Organization**: Use descriptive project names like `ai_pipeline_demo`
2. **Environment Separation**: Use different projects for dev/staging/prod
3. **Regular Monitoring**: Check your dashboard regularly for issues
4. **Cost Awareness**: Monitor API usage to avoid unexpected costs
5. **Data Privacy**: Be mindful of sensitive data in traces

## Advanced Features

### Custom Evaluators

Create custom evaluation metrics:

```python
def custom_evaluator(prediction: str, input: str) -> Dict[str, Any]:
    # Your custom evaluation logic
    score = calculate_custom_score(prediction, input)
    return {
        "score": score,
        "reasoning": "Custom evaluation criteria"
    }
```

### Experiment Tracking

Use LangSmith for A/B testing different prompts or models:

```python
# Track experiments with different configurations
with langsmith.trace(name="experiment_v1"):
    result_v1 = agent.process_query(query)

with langsmith.trace(name="experiment_v2"):
    result_v2 = agent.process_query_v2(query)
```

## Status

✅ **Configuration**: Environment variables and settings  
✅ **LLM Service**: Ollama integration with tracing  
✅ **Agent Graph**: LangGraph workflow monitoring  
✅ **Evaluation**: Response quality assessment  
✅ **Vector Store**: Document and embedding operations  
✅ **Streamlit App**: UI integration with tracing  

The LangSmith integration is fully functional and ready for production use with your local Ollama-based RAG system.
