import faiss
import numpy as np
import os
from fastembed import TextEmbedding
from db.faiss_db import save_index, load_index
from db.metadata_db import save_metadata, load_metadata

# Lightweight ONNX-based embedding model — no PyTorch, much lower memory
model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

class VectorDB:
    def __init__(self):
        self.index = load_index()
        self.chunks = load_metadata()

        if self.index is None:
            self.index = faiss.IndexFlatL2(384)
            self.chunks = []
            print("🚀 Created fresh Vector Database.")
        else:
            print(f"📂 Loaded existing Database with {self.index.ntotal} records.")

    def add_documents(self, text_chunks):
        if not text_chunks:
            return

        self.chunks.extend(text_chunks)

        # fastembed returns a generator of embeddings — convert to list/array
        embeddings = list(model.embed(text_chunks))

        self.index.add(np.array(embeddings).astype('float32'))

        save_index(self.index)
        save_metadata(self.chunks)
        print(f"✅ Memory Updated: {len(text_chunks)} new chunks stored.")

    def search(self, query, top_k=3):
        if self.index.ntotal == 0:
            return ["No documents found in memory. Please upload a PDF first."]

        query_vector = list(model.embed([query]))

        distances, indices = self.index.search(np.array(query_vector).astype('float32'), top_k)

        results = []
        for i in indices[0]:
            if i != -1 and i < len(self.chunks):
                results.append(self.chunks[i])

        return results

vector_store = VectorDB()