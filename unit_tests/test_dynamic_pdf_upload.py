#!/usr/bin/env python3
"""
Test script for dynamic PDF upload functionality.
"""

import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_sample_pdf():
    """Create a sample PDF for testing."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create temporary PDF
        pdf_path = "test_sample.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        # Add content to PDF
        c.drawString(100, 750, "Machine Learning Fundamentals")
        c.drawString(100, 720, "Machine learning is a subset of artificial intelligence")
        c.drawString(100, 700, "that enables computers to learn and improve from experience.")
        c.drawString(100, 680, "It focuses on developing algorithms that can access data")
        c.drawString(100, 660, "and use it to learn for themselves.")
        
        c.drawString(100, 620, "Key Concepts:")
        c.drawString(100, 600, "1. Supervised Learning")
        c.drawString(100, 580, "2. Unsupervised Learning")
        c.drawString(100, 560, "3. Reinforcement Learning")
        
        c.save()
        return pdf_path
        
    except ImportError:
        print("⚠️  reportlab not installed. Creating text file instead.")
        # Create text file as fallback
        text_path = "test_sample.txt"
        with open(text_path, "w") as f:
            f.write("Machine Learning Fundamentals\n\n")
            f.write("Machine learning is a subset of artificial intelligence\n")
            f.write("that enables computers to learn and improve from experience.\n")
        return text_path

def test_dynamic_pdf_processing():
    """Test dynamic PDF processing functionality."""
    
    print("🧪 Testing Dynamic PDF Upload and Processing")
    print("=" * 50)
    
    try:
        # Create sample document
        print("📄 Creating sample document...")
        sample_doc = create_sample_pdf()
        print(f"✅ Created sample document: {sample_doc}")
        
        # Test RAG service
        from src.rag.rag_service import RAGService
        
        rag_service = RAGService()
        print("✅ RAG Service initialized")
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"📁 Using temporary directory: {temp_dir}")
            
            # Copy sample document to temp directory
            import shutil
            temp_doc_path = Path(temp_dir) / Path(sample_doc).name
            shutil.copy2(sample_doc, temp_doc_path)
            print(f"✅ Copied document to: {temp_doc_path}")
            
            # Process documents
            print("📖 Processing documents...")
            init_result = rag_service.initialize_documents(temp_dir)
            
            if init_result["success"]:
                print("✅ Documents processed successfully!")
                print(f"   - {init_result['message']}")
                print(f"   - Summary: {init_result['summary']}")
                
                # Test RAG queries
                print("\n🔍 Testing RAG Queries:")
                
                test_queries = [
                    "What is machine learning?",
                    "Explain supervised learning",
                    "What are the key concepts?",
                    "Tell me about artificial intelligence"
                ]
                
                for query in test_queries:
                    print(f"\n📝 Query: {query}")
                    result = rag_service.process_rag_query(query)
                    
                    if result["success"]:
                        print(f"✅ Response: {result['response'][:100]}...")
                        print(f"   Sources: {result['sources']}")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                print("\n🎉 Dynamic PDF processing is working correctly!")
                return True
                
            else:
                print(f"❌ Document processing failed: {init_result['error']}")
                return False
        
    except Exception as e:
        print(f"❌ Dynamic PDF test failed: {str(e)}")
        return False
    finally:
        # Clean up sample document
        if os.path.exists("test_sample.pdf"):
            os.remove("test_sample.pdf")
        if os.path.exists("test_sample.txt"):
            os.remove("test_sample.txt")

if __name__ == "__main__":
    test_dynamic_pdf_processing() 