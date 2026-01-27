"""
Custom RAG engine WITHOUT LangChain
Pure FAISS + Azure OpenAI
"""
import sys
from pathlib import Path
import pickle
import numpy as np
import faiss
from openai import AzureOpenAI

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import (
    VECTOR_STORE_DIR,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_KEY,
    AZURE_EMBEDDING_DEPLOYMENT,
    AZURE_API_VERSION,
    TOP_K_RESULTS
)

class RAGEngine:
    def __init__(self):
        self.vector_store_dir = VECTOR_STORE_DIR
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_KEY,
            api_version=AZURE_API_VERSION
        )
        self.embedding_deployment = AZURE_EMBEDDING_DEPLOYMENT
        
        # Load FAISS index and data
        self.index = self._load_index()
        self.chunks = self._load_chunks()
        self.metadata = self._load_metadata()
    
    def _load_index(self):
        index_path = self.vector_store_dir / "index.faiss"
        if not index_path.exists():
            raise FileNotFoundError(
                "FAISS index not found. Run embeddings.py first!"
            )
        return faiss.read_index(str(index_path))
    
    def _load_chunks(self):
        """Load text chunks"""
        chunks_path = self.vector_store_dir / "chunks.pkl"
        with open(chunks_path, 'rb') as f:
            return pickle.load(f)
    
    def _load_metadata(self):
        """Load metadata"""
        metadata_path = self.vector_store_dir / "metadata.pkl"
        with open(metadata_path, 'rb') as f:
            return pickle.load(f)
    
    def get_embedding(self, text):
        """Get embedding for query"""
        response = self.client.embeddings.create(
            model=self.embedding_deployment,
            input=text
        )
        return response.data[0].embedding
    
    def retrieve(self, query, k=TOP_K_RESULTS):
        """Retrieve top-k relevant documents"""
        # Get query embedding
        query_embedding = self.get_embedding(query)
        query_vector = np.array([query_embedding]).astype('float32')
        
        # Search in FAISS
        distances, indices = self.index.search(query_vector, k)
        
        # Retrieve chunks
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            results.append({
                'content': self.chunks[idx],
                'metadata': self.metadata[idx],
                'score': float(distance)
            })
        
        return results
    
    def retrieve_with_scores(self, query, k=TOP_K_RESULTS):
        """Same as retrieve - kept for compatibility"""
        return self.retrieve(query, k)