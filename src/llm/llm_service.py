from typing import Dict, Any, List, Optional
import nest_asyncio
import time
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from src.config import get_settings
from src.langsmith_integration import init_langsmith, is_langsmith_enabled

# Apply nest_asyncio to handle nested event loops
nest_asyncio.apply()


class LLMService:
    """LLM service for text processing and generation."""
    
    def __init__(self):
        self.settings = get_settings()
        self.quota_exceeded = False
        self.last_quota_check = 0
        
        # Initialize LangSmith tracing
        self.langsmith_enabled = init_langsmith()
        
        # Use Ollama for local LLM processing
        try:
            self.llm = ChatOllama(
                model="llama3.2:latest",
                base_url="http://localhost:11434",
                temperature=0.3,
                num_predict=300  # Equivalent to max_tokens
            )
            self.llm_provider = "ollama"
            print("✅ Using Ollama LLM: llama3.2:latest")
        except Exception as e:
            print(f"❌ Failed to initialize Ollama: {e}")
            raise ValueError("Ollama is not available. Please ensure Ollama is running with llama3.2:latest model.")
        
        # Decision prompt for routing queries
        self.decision_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a query classifier that determines whether a user query is about weather or general knowledge/documentation.

            Classify the query into one of these categories:
            - "weather": If the query asks about weather, temperature, forecast, climate, or location-specific weather conditions
            - "rag": If the query asks about general knowledge, documents, explanations, definitions, or information that would require document search

            Respond with only "weather" or "rag".
            
            Examples:
            - "What's the weather in New York?" -> "weather"
            - "What is machine learning?" -> "rag"
            - "Tell me about the weather in London" -> "weather"
            - "Explain quantum computing" -> "rag"
            """),
            ("human", "{query}")
        ])
        
        # Response enhancement prompt
        self.enhancement_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant that enhances and formats responses to make them more user-friendly and informative.
            
            Enhance the provided response to be:
            - Clear and concise
            - Well-formatted with bullet points where appropriate
            - Professional yet conversational
            - Include relevant context when helpful"""),
            ("human", "Original response: {original_response}\n\nQuery: {query}\n\nPlease enhance this response:")
        ])
    
    def classify_query(self, query: str) -> str:
        """Classify a query as weather or RAG."""
        try:
            # Use simple string prompt for Ollama
            if self.llm_provider == "ollama":
                prompt = f"""You are a query classifier. Classify this query as either "weather" or "rag":

Query: {query}

Rules:
- If the query asks about weather, temperature, forecast, climate, or location-specific weather conditions, respond with: weather
- If the query asks about general knowledge, documents, explanations, definitions, or information that would require document search, respond with: rag

Respond with only one word: "weather" or "rag"."""
                
                response = self.llm.invoke(prompt)
            else:
                messages = self.decision_prompt.format_messages(query=query)
                response = self.llm.invoke(messages)
            
            # Clean the response - handle different response types
            if hasattr(response, 'content'):
                classification = str(response.content).strip().lower()
            else:
                classification = str(response).strip().lower()
            
            if classification in ["weather", "rag"]:
                return classification
            else:
                # Default to RAG for unclear queries
                return "rag"
                
        except Exception as e:
            print(f"Error classifying query: {str(e)}")
            # Default to RAG for errors
            return "rag"
    
    def enhance_response(self, original_response: str, query: str) -> str:
        """Enhance a response to make it more user-friendly."""
        try:
            # Validate inputs
            if not original_response or not original_response.strip():
                return "I apologize, but I couldn't generate a proper response to your question. Please try rephrasing your query."
            
            if not query or not query.strip():
                return original_response  # Return original if query is empty
            
            # Use simple string prompt for Ollama
            if self.llm_provider == "ollama":
                prompt = f"""You are a helpful AI assistant. Enhance this response to be more user-friendly and informative.

Original response: {original_response}

Query: {query}

Make the response:
- Clear and concise
- Well-formatted with bullet points where appropriate
- Professional yet conversational
- Include relevant context when helpful

Enhanced response:"""
                
                response = self.llm.invoke(prompt)
            else:
                messages = self.enhancement_prompt.format_messages(
                    original_response=original_response,
                    query=query
                )
                response = self.llm.invoke(messages)
            
            # Validate the enhanced response - handle different response types
            if hasattr(response, 'content'):
                enhanced = str(response.content)
            else:
                enhanced = str(response)
                
            if enhanced and enhanced.strip():
                return enhanced
            else:
                return original_response  # Return original if enhancement failed
            
        except Exception as e:
            print(f"Error enhancing response: {str(e)}")
            return original_response
    
    def generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate a summary of the provided content."""
        try:
            # Use simple string prompt for Ollama
            if self.llm_provider == "ollama":
                prompt = f"""Summarize the following content in {max_length} words or less:

Content: {content}

Summary:"""
                
                response = self.llm.invoke(prompt)
            else:
                summary_prompt = ChatPromptTemplate.from_messages([
                    ("system", f"You are a summarizer. Create a concise summary of the provided content in {max_length} words or less."),
                    ("human", "{content}")
                ])
                
                messages = summary_prompt.format_messages(content=content)
                response = self.llm.invoke(messages)
            
            # Handle different response types
            if hasattr(response, 'content'):
                return str(response.content)
            else:
                return str(response)
            
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return content[:max_length] + "..." if len(content) > max_length else content
    
    def process_query_with_context(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Process a query with additional context."""
        try:
            # Debug: Print context structure
            print("DEBUG: Processing query with context")
            print(f"DEBUG: Number of context items: {len(context)}")
            
            # Extract page content from context
            context_text = "\n".join([
                str(item.get('page_content', '')) if isinstance(item, dict) else str(item)
                for item in context if item  # Filter out None or empty items
            ])
            
            print(f"DEBUG: Context length: {len(context_text)} characters")
            print("DEBUG: First 200 chars of context:", context_text[:200] + "...")
            
            # Format context and query for Ollama - use simple string approach
            if self.llm_provider == "ollama":
                # Create a simple prompt string for Ollama
                prompt_text = f"""Question: {query}

Resume Content:
{context_text}

Instructions: Based ONLY on the resume content above, provide a clear, concise answer to the question. Be specific and avoid repetition. Limit your response to the most relevant information."""

                # Use the invoke method with a simple string
                response = self.llm.invoke(prompt_text)
            else:
                # For other providers (future extensions)
                context_prompt = ChatPromptTemplate.from_messages([
                    ("system", """You are a helpful AI assistant. Answer the user's question using the provided context from their resume.
                    If you can't find relevant information in the context, please state that clearly.
                    
                    Context:
                    {context}
                    
                    Question: {query}
                    
                    Answer:"""),
                ])
                
                messages = context_prompt.format_messages(
                    context=context_text,
                    query=query
                )
                
                response = self.llm.invoke(messages)
            
            # Handle different response types and validate
            try:
                if hasattr(response, 'content'):
                    result = str(response.content)
                else:
                    result = str(response)
                
                # Clean up repetitive content
                result = self._clean_repetitive_response(result)
                
                # Validate response
                if not result or not result.strip():
                    print("DEBUG: Empty response received")
                    return "I apologize, but I couldn't generate a response based on the provided resume context. Please try rephrasing your question."
                
                print("DEBUG: Successfully generated response")
                return result
                
            except Exception as e:
                print(f"DEBUG: Error extracting response content: {str(e)}")
                return "I apologize, but there was an error processing the resume information. Please try again."
            
        except Exception as e:
            print(f"Error processing query with context: {str(e)}")
            return f"Error processing your request: {str(e)}"
    
    def _clean_repetitive_response(self, text: str) -> str:
        """Clean up repetitive content in the response."""
        if not text:
            return text
            
        # Split into sentences and paragraphs
        paragraphs = text.split('\n\n')
        cleaned_paragraphs = []
        seen_content = set()
        
        for paragraph in paragraphs:
            # Clean up the paragraph
            cleaned_para = paragraph.strip()
            if not cleaned_para:
                continue
                
            # Create a signature for this paragraph (first 50 chars)
            signature = cleaned_para[:50].lower().strip()
            
            # Skip if we've seen very similar content
            if signature not in seen_content:
                seen_content.add(signature)
                cleaned_paragraphs.append(cleaned_para)
            
            # Stop if we have enough content (to prevent overly long responses)
            if len(cleaned_paragraphs) >= 10:  # Max 10 paragraphs
                break
        
        result = '\n\n'.join(cleaned_paragraphs)
        
        # Additional cleanup: remove trailing repeated phrases
        lines = result.split('\n')
        final_lines = []
        seen_lines = set()
        
        for line in lines:
            line_clean = line.strip()
            if line_clean and line_clean not in seen_lines:
                seen_lines.add(line_clean)
                final_lines.append(line)
        
        return '\n'.join(final_lines)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the LLM model."""
        return {
            "model": self.settings.gemini_model,
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_tokens,
            "provider": "Google Gemini"
        } 