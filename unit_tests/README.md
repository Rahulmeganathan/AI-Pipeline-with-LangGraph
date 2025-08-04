# Unit Tests

This directory contains all the test scripts for the AI Pipeline project.

## Test Files

- `test_agent_graph.py`: Tests for the LangGraph agent implementation
- `test_dynamic_pdf_upload.py`: Tests for PDF upload functionality
- `test_evaluator_without_langsmith.py`: Tests for evaluator without LangSmith
- `test_final_async_fix.py`: Tests for asynchronous operations
- `test_gemini_integration.py`: Tests for Gemini model integration
- `test_gemini_models.py`: Tests for different Gemini models
- `test_langsmith_config.py`: Tests for LangSmith configuration
- `test_processed_data_storage.py`: Tests for data storage functionality
- `test_simple_processed_data.py`: Tests for data processing
- `test_streamlit_async_fix.py`: Tests for Streamlit async operations
- `test_weather_service.py`: Tests for weather service integration

## Running Tests

To run all tests:
```bash
python -m pytest unit_tests/
```

To run a specific test:
```bash
python -m pytest unit_tests/test_file_name.py
```
