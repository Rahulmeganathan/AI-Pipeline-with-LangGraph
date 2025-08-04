#!/usr/bin/env python3
"""
Simple quota-aware version for testing when API limits are hit.
This provides basic responses based on the retrieved content without using the LLM.
"""

def create_basic_response(query: str, context_items: list) -> str:
    """Create a basic response from context without using LLM when quota is exceeded."""
    
    # Extract content from context
    content_parts = []
    for item in context_items:
        if isinstance(item, dict):
            content = item.get('page_content', item.get('content', ''))
            if content:
                content_parts.append(content)
    
    if not content_parts:
        return "I found some information but couldn't extract readable content."
    
    # Basic keyword matching for different query types
    query_lower = query.lower()
    all_content = ' '.join(content_parts)
    
    if any(word in query_lower for word in ['skill', 'technical', 'technology', 'programming']):
        # Look for technical skills
        skills = []
        skill_keywords = ['LangChain', 'LangGraph', 'Hugging Face', 'LoRA', 'RAG', 'FAISS', 
                         'Python', 'Machine Learning', 'Deep Learning', 'Computer Vision',
                         'AWS', 'Azure', 'MLflow', 'Prompt Engineering']
        
        for skill in skill_keywords:
            if skill.lower() in all_content.lower():
                skills.append(skill)
        
        if skills:
            return f"Based on the resume, Rahul has experience with: {', '.join(skills)}"
    
    elif any(word in query_lower for word in ['experience', 'work', 'job', 'samsung', 'company']):
        # Look for work experience
        if 'Samsung' in all_content:
            return "Rahul worked at Samsung R&D Institute India as a Software Engineer and Machine Learning Engineer."
    
    elif any(word in query_lower for word in ['project', 'built', 'developed', 'created']):
        # Look for projects
        if 'computer vision' in all_content.lower():
            return "Rahul worked on computer vision projects including GPU-accelerated prototypes on AWS EC2 for real-time analytics."
    
    # Fallback - return first meaningful chunk
    first_content = content_parts[0][:200] + "..." if len(content_parts[0]) > 200 else content_parts[0]
    return f"Here's relevant information from the resume: {first_content}"

if __name__ == "__main__":
    # Test the basic response function
    test_context = [
        {"page_content": "LangChain, LangGraph, Hugging Face, LoRA (PEFT), RAG, FAISS, Prompt Engineering"},
        {"page_content": "Samsung R&D Institute India - Software Engineer, Machine Learning Engineer"}
    ]
    
    queries = [
        "What technical skills does Rahul have?",
        "Tell me about Rahul's work experience",
        "What projects has Rahul worked on?"
    ]
    
    for query in queries:
        response = create_basic_response(query, test_context)
        print(f"Query: {query}")
        print(f"Response: {response}\n")
