import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from db.faiss_db import save_index, load_index
from db.metadata_db import save_metadata, load_metadata

from db.faiss_db import save_index, load_index
from db.metadata_db import save_metadata, load_metadata

# 1. Load the "Translator" model (Converts text to math vectors)
# We use a lightweight model suitable for local development at MNNIT
model = SentenceTransformer('all-MiniLM-L6-v2')

class VectorDB:
    def __init__(self):
        # 2. Try to load existing data from the /db folder
        self.index = load_index()
        self.chunks = load_metadata()
        
        # 3. If no existing DB is found, create a fresh one (384 dimensions)
        if self.index is None:
            self.index = faiss.IndexFlatL2(384)
            self.chunks = []
            print("🚀 Created fresh Vector Database.")
        else:
            print(f"📂 Loaded existing Database with {self.index.ntotal} records.")

    def add_documents(self, text_chunks):
        """Processes text chunks, turns them into vectors, and SAVES to disk."""
        if not text_chunks:
            return

        self.chunks.extend(text_chunks)
        
        # Convert text list to mathematical vectors
        embeddings = model.encode(text_chunks)
        
        # Add to the FAISS index
        self.index.add(np.array(embeddings).astype('float32'))
        
        # PERMANENCE: Write to the /db folder files
        save_index(self.index)
        save_metadata(self.chunks)
        print(f"✅ Memory Updated: {len(text_chunks)} new chunks stored.")

    def search(self, query, top_k=3):
        """Finds the most relevant text for a user's question."""
        if self.index.ntotal == 0:
            return ["No documents found in memory. Please upload a PDF first."]

        # Convert the user's question into a vector
        query_vector = model.encode([query])
        
        # Search the index for the 'Top K' closest matches
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), top_k)
        
        # Map the math results back to actual text strings
        results = []
        for i in indices[0]:
            if i != -1 and i < len(self.chunks):
                results.append(self.chunks[i])
        
        return results

# Initialize the global instance for the Alchemists' Backend
vector_store = VectorDB()