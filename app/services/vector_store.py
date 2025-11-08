from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import numpy as np

from app.core.config import get_settings

settings = get_settings()

class VectorStore:
    def __init__(self):
        self.client = None
        # Try to connect to Qdrant, but don't block if it fails
        try:
            # Use a very short timeout for the connection
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  # 1 second timeout
            qdrant_host = settings.QDRANT_URL.replace("http://", "").replace("https://", "").split(":")[0]
            qdrant_port = int(settings.QDRANT_URL.split(":")[-1]) if ":" in settings.QDRANT_URL else 6333
            result = sock.connect_ex((qdrant_host, qdrant_port))
            sock.close()
            
            if result == 0:
                # Port is open, try to connect
                self.client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY,
                    timeout=2  # 2 second timeout
                )
                # Test connection with timeout
                self.client.get_collections()
                print("Connected to Qdrant successfully")
            else:
                raise ConnectionError("Qdrant port is not open")
        except Exception as e:
            print(f"WARNING: Could not connect to Qdrant at {settings.QDRANT_URL}: {e}")
            print("Vector search will return empty results. Please start Qdrant with: docker-compose up -d qdrant")
            self.client = None
        
        # Lazy load encoder to avoid blocking server startup
        self._encoder = None
        self.embedding_model = settings.EMBEDDING_MODEL
        self.collection_name = settings.COLLECTION_NAME
        
        # Ensure collection exists if client is available
        if self.client:
            self._create_collection_if_not_exists()
    
    @property
    def encoder(self):
        """Lazy load the sentence transformer model."""
        if self._encoder is None:
            print(f"Loading embedding model: {self.embedding_model}...")
            self._encoder = SentenceTransformer(self.embedding_model)
            print("Embedding model loaded successfully")
        return self._encoder
    
    def _create_collection_if_not_exists(self):
        """Create the vector collection if it doesn't exist."""
        if not self.client:
            return
        try:
            collections = self.client.get_collections().collections
            if not any(col.name == self.collection_name for col in collections):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.encoder.get_sentence_embedding_dimension(),
                        distance=models.Distance.COSINE
                    )
                )
        except Exception as e:
            print(f"⚠️ WARNING: Could not create collection: {e}")
    
    def add_documents(self, texts: List[str], metadata: List[Dict[str, Any]] = None):
        """Add documents to the vector store."""
        if not self.client:
            print("⚠️ Qdrant not available, cannot add documents")
            return
        
        if metadata is None:
            metadata = [{} for _ in texts]
        
        try:
            # Generate embeddings
            embeddings = self.encoder.encode(texts)
            
            # Prepare points for insertion
            points = [
                models.PointStruct(
                    id=i,
                    vector=embedding.tolist(),
                    payload={"text": text, **meta}
                )
                for i, (text, embedding, meta) in enumerate(zip(texts, embeddings, metadata))
            ]
            
            # Upload to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
        except Exception as e:
            print(f"⚠️ WARNING: Could not add documents to Qdrant: {e}")
    
    def semantic_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search using the query."""
        if not self.client:
            print("⚠️ Qdrant not available, returning empty search results")
            return []
        
        try:
            query_vector = self.encoder.encode(query)
            
            # Search in Qdrant
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            # Format results
            results = []
            for scored_point in search_result:
                results.append({
                    "text": scored_point.payload["text"],
                    "score": scored_point.score,
                    "metadata": {k: v for k, v in scored_point.payload.items() if k != "text"}
                })
            
            return results
        except Exception as e:
            print(f"⚠️ WARNING: Semantic search failed: {e}")
            return []
