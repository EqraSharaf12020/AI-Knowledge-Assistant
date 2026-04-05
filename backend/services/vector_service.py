import faiss
import numpy as np
import os
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

DB_DIR = os.path.join(os.path.dirname(__file__), '..', 'db', 'sessions')
os.makedirs(DB_DIR, exist_ok=True)


# ── file-path helpers ─────────────────────────────────────────────────────────

def _index_path(session_id: str) -> str:
    return os.path.join(DB_DIR, f"{session_id}.index")

def _meta_path(session_id: str) -> str:
    return os.path.join(DB_DIR, f"{session_id}_meta.json")


# ── load / save ───────────────────────────────────────────────────────────────

def _load(session_id: str):
    """Return (faiss_index, chunks_list) for this session."""
    idx_p = _index_path(session_id)
    met_p = _meta_path(session_id)
    if os.path.exists(idx_p) and os.path.exists(met_p):
        index = faiss.read_index(idx_p)
        with open(met_p, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        print(f"[VectorDB] Loaded session {session_id}: {index.ntotal} vectors")
        return index, chunks
    index = faiss.IndexFlatL2(384)
    print(f"[VectorDB] New session {session_id}")
    return index, []


def _save(session_id: str, index, chunks: list):
    """Persist index + metadata for this session."""
    faiss.write_index(index, _index_path(session_id))
    with open(_meta_path(session_id), 'w', encoding='utf-8') as f:
        json.dump(chunks, f)


# ── public API ────────────────────────────────────────────────────────────────

def add_documents(session_id: str, text_chunks: list):
    """Embed chunks and store them under this session's private index."""
    if not text_chunks:
        return
    index, chunks = _load(session_id)
    chunks.extend(text_chunks)
    embeddings = model.encode(text_chunks)
    index.add(np.array(embeddings).astype('float32'))
    _save(session_id, index, chunks)
    print(f"[VectorDB] {len(text_chunks)} chunks stored for session {session_id}")


def search(session_id: str, query: str, top_k: int = 3) -> list:
    """Search only this session's private index."""
    index, chunks = _load(session_id)
    if index.ntotal == 0:
        return ["No documents found in memory. Please upload a PDF first."]
    query_vec = model.encode([query])
    distances, indices = index.search(np.array(query_vec).astype('float32'), top_k)
    results = []
    for i in indices[0]:
        if i != -1 and i < len(chunks):
            results.append(chunks[i])
    return results


def clear_session(session_id: str):
    """Delete all data for a session (optional cleanup)."""
    for path in [_index_path(session_id), _meta_path(session_id)]:
        if os.path.exists(path):
            os.remove(path)
    print(f"[VectorDB] Cleared session {session_id}")
