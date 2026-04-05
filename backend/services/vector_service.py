import faiss
import numpy as np
import os
import json
import time
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

DB_DIR = os.path.join(os.path.dirname(__file__), '..', 'db', 'sessions')
os.makedirs(DB_DIR, exist_ok=True)


# ── file-path helpers ─────────────────────────────────────────────────────────

def _index_path(session_id: str) -> str:
    return os.path.join(DB_DIR, f"{session_id}.index")

def _meta_path(session_id: str) -> str:
    return os.path.join(DB_DIR, f"{session_id}_meta.json")

def _chat_path(session_id: str) -> str:
    return os.path.join(DB_DIR, f"{session_id}_chat.json")


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


def _load_chat_history(session_id: str) -> list:
    """Load conversation history for this session."""
    chat_path = _chat_path(session_id)
    if os.path.exists(chat_path):
        try:
            with open(chat_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[VectorDB] Error loading chat history: {e}")
    return []


def _save_chat_history(session_id: str, chat_history: list):
    """Save conversation history for this session."""
    chat_path = _chat_path(session_id)
    try:
        with open(chat_path, 'w', encoding='utf-8') as f:
            json.dump(chat_history, f, indent=2)
    except Exception as e:
        print(f"[VectorDB] Error saving chat history: {e}")


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


def add_chat_message(session_id: str, role: str, message: str):
    """Add a message to the conversation history."""
    chat_history = _load_chat_history(session_id)
    chat_history.append({"role": role, "message": message, "timestamp": int(time.time())})
    # Keep only last 20 messages to avoid token limits
    if len(chat_history) > 20:
        chat_history = chat_history[-20:]
    _save_chat_history(session_id, chat_history)


def get_chat_history(session_id: str) -> list:
    """Get the conversation history for this session."""
    return _load_chat_history(session_id)


def clear_session(session_id: str):
    """Delete all data for a session (optional cleanup)."""
    for path in [_index_path(session_id), _meta_path(session_id), _chat_path(session_id)]:
        if os.path.exists(path):
            os.remove(path)
    print(f"[VectorDB] Cleared session {session_id}")
