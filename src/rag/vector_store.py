from typing import List, Dict, Any, Optional, Sequence
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_core.documents.base import Document
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from pydantic import SecretStr
from src.config import get_settings


class VectorStore:
    """Vector store service using Qdrant Cloud."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = QdrantClient(
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key,
            timeout=60  # Increased timeout to 60 seconds
        )
        
        # Use local embeddings instead of Gemini
        try:
            # Try local embeddings first
            self.embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",  # Fast, lightweight model
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            self.embedding_dimension = 384  # all-MiniLM-L6-v2 dimension
            self.embedding_provider = "local"
            print("✅ Using local embeddings: all-MiniLM-L6-v2")
        except Exception as e:
            # Fallback to Gemini if local fails
            if not self.settings.google_api_key:
                raise ValueError("Local embeddings failed and no GOOGLE_API_KEY provided")
            
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=SecretStr(self.settings.google_api_key)
            )
            self.embedding_dimension = 768  # Gemini embedding dimension
            self.embedding_provider = "gemini"
            print("⚠️ Fallback to Gemini embeddings")
            
        self.collection_name = self.settings.qdrant_collection_name

    def create_collection(self) -> bool:
        """Create the vector collection if it doesn't exist."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                print(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,  # Dynamic embedding dimension
                        distance=Distance.COSINE
                    )
                )
                print(f"Collection '{self.collection_name}' created successfully")
                return True
            else:
                print(f"Collection '{self.collection_name}' already exists")
                return True
                
        except Exception as e:
            print(f"Error creating collection: {str(e)}")
            return False
    
    def store_documents(self, documents: Sequence[Document], batch_size: int = 3) -> bool:
        """Store document chunks in the vector database with batching."""
        if not documents:
            print("No documents to store")
            return False
        
        try:
            # Clear and recreate collection
            if self.collection_name in [col.name for col in self.client.get_collections().collections]:
                print(f"Clearing existing collection: {self.collection_name}")
                self.client.delete_collection(collection_name=self.collection_name)
            
            # Create new collection
            if not self.create_collection():
                print("Failed to create or verify collection")
                return False
            
            print(f"Storing {len(documents)} document chunks in vector database...")
            documents = list(documents)  # Convert Sequence to list
            
            # Process documents in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                print(f"Processing batch {i//batch_size + 1} of {(len(documents) + batch_size - 1)//batch_size}")
                
                try:
                    # First try with the default method for this batch
                    vector_store = QdrantVectorStore.from_documents(
                        documents=batch,
                        embedding=self.embeddings,
                        collection_name=self.collection_name,
                        url=self.settings.qdrant_url,
                        api_key=self.settings.qdrant_api_key,
                        prefer_grpc=True,
                        batch_size=batch_size
                    )
                except Exception as e1:
                    print(f"First attempt failed for batch: {str(e1)}")
                    print("Trying alternative storage method for this batch...")
                    
                    # Alternative: Manual embedding and storage for this batch
                    texts = [doc.page_content for doc in batch]
                    # Manual embedding and storage for this batch
                    embeddings = self.embeddings.embed_documents(texts)
                    points = [
                        PointStruct(
                            id=idx + i,  # Ensure unique IDs across batches
                            vector=embedding,
                            payload={"text": text, "metadata": batch[idx].metadata}
                        )
                        for idx, (text, embedding) in enumerate(zip(texts, embeddings))
                    ]
                    
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=points,
                        wait=True  # Ensure the operation completes before moving to next batch
                    )
                    print(f"Successfully stored batch {i//batch_size + 1}")
                
            print(f"Successfully stored all {len(documents)} document chunks")
            return True
            
        except Exception as e:
            print(f"Error storing documents: {str(e)}")
            print(f"Document format example: {documents[0] if documents else 'No documents'}")
            return False
    
    def search_similar(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using semantic similarity."""
        try:
            print(f"DEBUG: Searching for query: {query}")
            # Create Qdrant vector store for search
            vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embedding=self.embeddings
            )
            
            # Search for similar documents
            results = vector_store.similarity_search_with_score(
                query=query,
                k=k
            )
            
            print(f"DEBUG: Found {len(results)} results")
            
            # Format results consistently and add debug logging
            formatted_results = []
            for doc, score in results:
                result = {
                    "page_content": doc.page_content,  # Use page_content for consistency
                    "content": doc.page_content,       # Also provide content for backward compatibility
                    "metadata": doc.metadata,
                    "similarity_score": score
                }
                formatted_results.append(result)
                print(f"DEBUG: Result score: {score}, First 100 chars: {doc.page_content[:100]}...")
            
            if not formatted_results:
                print("DEBUG: No results found in vector store")
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the vector collection."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": getattr(collection_info, 'vectors_count', 0),
                "points_count": getattr(collection_info, 'points_count', 0),
                "segments_count": getattr(collection_info, 'segments_count', 0),
                "status": getattr(collection_info, 'status', 'unknown')
            }
        except Exception as e:
            print(f"Error getting collection info: {str(e)}")
            return {}
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            self.client.delete_collection(self.collection_name)
            print(f"Collection '{self.collection_name}' deleted")
            return True
        except Exception as e:
            print(f"Error clearing collection: {str(e)}")
            return False 
    
    def store_responses(self, documents: Sequence[Document], batch_size: int = 3) -> bool:
        """Store AI responses in the vector database without clearing existing documents.
        
        Args:
            documents: Response documents to store
            batch_size: Number of documents per batch
        """
        if not documents:
            print("No response documents to store")
            return False
        
        try:
            # Ensure collection exists but don't clear it
            if not self.create_collection():
                print("Failed to create or verify collection")
                return False
            
            # Get current point count for ID offset
            try:
                collection_info = self.client.get_collection(self.collection_name)
                id_offset = getattr(collection_info, 'points_count', 0)
                print(f"Adding {len(documents)} response chunks to existing {id_offset} documents")
            except:
                id_offset = 0
            
            documents = list(documents)  # Convert Sequence to list
            
            # Process documents in batches without clearing
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                print(f"Processing response batch {i//batch_size + 1} of {(len(documents) + batch_size - 1)//batch_size}")
                
                # Use manual embedding and storage to avoid clearing
                texts = [doc.page_content for doc in batch]
                embeddings = self.embeddings.embed_documents(texts)
                points = [
                    PointStruct(
                        id=idx + i + id_offset,  # Use offset to avoid ID conflicts
                        vector=embedding,
                        payload={"text": text, "metadata": batch[idx].metadata}
                    )
                    for idx, (text, embedding) in enumerate(zip(texts, embeddings))
                ]
                
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points,
                    wait=True
                )
                print(f"Successfully stored response batch {i//batch_size + 1}")
            
            print(f"✅ Successfully stored all {len(documents)} response chunks alongside existing documents")
            return True
            
        except Exception as e:
            print(f"❌ Error storing response documents: {str(e)}")
            return False
            
    def search_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for documents using semantic similarity (alias for search_similar)."""
        return self.search_similar(query, k)