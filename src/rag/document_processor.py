import os
from typing import List, Dict, Any, Union, Sequence
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents.base import Document
from src.config import get_settings


class DocumentProcessor:
    """Process PDF documents and split them into chunks for vector storage."""
    
    def __init__(self):
        self.settings = get_settings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_documents(self, data_dir: str = "data") -> List[Document]:
        """Load all documents (PDF and text) from the data directory."""
        documents = []
        data_path = Path(data_dir)
        
        if not data_path.exists():
            print(f"Data directory '{data_dir}' does not exist. Creating it...")
            data_path.mkdir(parents=True, exist_ok=True)
            return documents
        
        # Find all PDF files
        pdf_files = list(data_path.glob("*.pdf"))
        text_files = list(data_path.glob("*.txt"))
        
        if not pdf_files and not text_files:
            print(f"No PDF or text files found in '{data_dir}' directory.")
            return documents
        
        # Process PDF files
        for pdf_file in pdf_files:
            try:
                print(f"Processing PDF: {pdf_file.name}")
                loader = PyPDFLoader(str(pdf_file))
                pdf_docs = loader.load()
                
                # Add metadata and ensure correct document format
                for doc in pdf_docs:
                    if not hasattr(doc, 'page_content'):
                        print(f"Warning: Document missing page_content, converting text: {pdf_file.name}")
                        doc_text = str(doc)
                    else:
                        doc_text = doc.page_content
                        
                    documents.append(Document(
                        page_content=doc_text,
                        metadata={
                            "source": pdf_file.name,
                            "file_path": str(pdf_file),
                            "type": "pdf"
                        }
                    ))
                
                print(f"Successfully loaded {len(pdf_docs)} pages from {pdf_file.name}")
                
            except Exception as e:
                print(f"Error processing {pdf_file.name}: {str(e)}")
                continue
        
        # Process text files
        for text_file in text_files:
            try:
                print(f"Processing text file: {text_file.name}")
                with open(text_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create a document object for text files
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": text_file.name,
                        "file_path": str(text_file),
                        "file_type": "text"
                    }
                )
                
                documents.append(doc)
                print(f"Successfully loaded text file: {text_file.name}")
                
            except Exception as e:
                print(f"Error processing {text_file.name}: {str(e)}")
                continue
        
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks for vector storage."""
        if not documents:
            return []
        
        print(f"Splitting {len(documents)} documents into chunks...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks")
        
        return chunks
    
    def process_documents(self, data_dir: str = "data") -> List[Document]:
        """Complete document processing pipeline."""
        # Load documents
        documents = self.load_documents(data_dir)
        
        if not documents:
            return []
        
        # Split into chunks
        chunks = self.split_documents(documents)
        
        return chunks
    
    def get_document_summary(self, chunks: Sequence[Document]) -> Dict[str, Any]:
        """Generate a summary of processed documents."""
        if not chunks:
            return {
                "total_chunks": 0,
                "total_pages": 0,
                "sources": [],
                "average_chunk_size": 0
            }
        
        # Count unique sources
        sources = list(set(chunk.metadata.get("source", "unknown") for chunk in chunks))
        
        # Calculate average chunk size
        total_text_length = sum(len(chunk.page_content) for chunk in chunks)
        average_chunk_size = total_text_length / len(chunks) if chunks else 0
        
        return {
            "total_chunks": len(chunks),
            "total_pages": len(set(chunk.metadata.get("page", 0) for chunk in chunks)),
            "sources": sources,
            "average_chunk_size": round(average_chunk_size, 2)
        } 