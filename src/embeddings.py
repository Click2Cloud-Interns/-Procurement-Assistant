import sys
from pathlib import Path
import pickle
import numpy as np
import faiss
from openai import AzureOpenAI

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import (
    DOCUMENTS_DIR,
    VECTOR_STORE_DIR,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_KEY,
    AZURE_EMBEDDING_DEPLOYMENT,
    AZURE_API_VERSION,
    EMBEDDING_DIMENSION
)

class EmbeddingManager:
    def __init__(self):
        self.docs_dir = DOCUMENTS_DIR
        self.vector_store_dir = VECTOR_STORE_DIR
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_KEY,
            api_version=AZURE_API_VERSION
        )
        self.embedding_deployment = AZURE_EMBEDDING_DEPLOYMENT
    
    def load_documents(self):
        """Load all text documents from directories"""
        documents = []
        metadata = []
        
        # Load from all subdirectories
        for subdir in ['materials', 'suppliers', 'purchase_orders', 'invoices']:
            dir_path = self.docs_dir / subdir
            if dir_path.exists():
                for file_path in dir_path.glob("*.txt"):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        documents.append(content)
                        metadata.append({
                            'source': str(file_path),
                            'category': subdir,
                            'filename': file_path.name
                        })
                
                print(f"✅ Loaded {len(list(dir_path.glob('*.txt')))} documents from {subdir}")
        
        return documents, metadata
    
    def split_text(self, text, chunk_size=1000, chunk_overlap=100):
        """Simple text splitter"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - chunk_overlap
        
        return chunks
    
    def get_embedding(self, text):
        """Get embedding from Azure OpenAI"""
        response = self.client.embeddings.create(
            model=self.embedding_deployment,
            input=text
        )
        return response.data[0].embedding
    
    def get_embeddings_batch(self, texts, batch_size=10):
        """Get embeddings in batches for efficiency"""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            print(f"  Processing embeddings {i+1}-{min(i+batch_size, len(texts))} of {len(texts)}...")
            
            response = self.client.embeddings.create(
                model=self.embedding_deployment,
                input=batch
            )
            
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def create_vector_store(self):
        """Create FAISS vector store from documents"""
        print("🔄 Loading documents...")
        documents, metadata = self.load_documents()
        
        if not documents:
            raise ValueError("No documents found. Run data_processor.py first!")
        
        print(f"📄 Total documents: {len(documents)}")
        
        # Split documents into chunks
        print("📝 Splitting documents into chunks...")
        all_chunks = []
        all_metadata = []
        
        for doc, meta in zip(documents, metadata):
            chunks = self.split_text(doc, chunk_size=1000, chunk_overlap=100)
            all_chunks.extend(chunks)
            all_metadata.extend([meta] * len(chunks))
        
        print(f"📝 Created {len(all_chunks)} text chunks")
        
        # Create embeddings
        print("🧠 Creating embeddings (this may take a few minutes)...")
        embeddings = self.get_embeddings_batch(all_chunks, batch_size=10)
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        print("🔧 Building FAISS index...")
        index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
        index.add(embeddings_array)
        
        # Save everything
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(index, str(self.vector_store_dir / "index.faiss"))
        
        # Save chunks and metadata
        with open(self.vector_store_dir / "chunks.pkl", 'wb') as f:
            pickle.dump(all_chunks, f)
        
        with open(self.vector_store_dir / "metadata.pkl", 'wb') as f:
            pickle.dump(all_metadata, f)
        
        print(f"✅ Vector store saved to {self.vector_store_dir}")
        print(f"   - Index size: {len(embeddings_array)} vectors")
        print(f"   - Dimension: {EMBEDDING_DIMENSION}")
        
        return index, all_chunks, all_metadata

if __name__ == "__main__":
    manager = EmbeddingManager()
    manager.create_vector_store()