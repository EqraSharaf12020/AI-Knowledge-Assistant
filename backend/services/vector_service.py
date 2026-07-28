import faiss
import numpy as np
import os
import json
import time
from fastembed import TextEmbedding

# BGE model for better legal document retrieval
model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

DB_DIR = os.path.join(os.path.dirname(__file__), '..', 'db', 'sessions')
os.makedirs(DB_DIR, exist_ok=True)

# Global knowledge base paths
GLOBAL_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'vector_store')
os.makedirs(GLOBAL_DIR, exist_ok=True)


# ── file-path helpers ─────────────────────────────────────────────────────────

def _index_path(session_id: str) -> str:
    return os.path.join(DB_DIR, f"{session_id}.index")

def _global_index_path() -> str:
    return os.path.join(GLOBAL_DIR, "global.index")

def _global_meta_path() -> str:
    return os.path.join(GLOBAL_DIR, "global_meta.json")

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
        
        # Backward compatibility: auto-wrap old plain strings as metadata dicts
        chunks = _upgrade_chunks_metadata(chunks)
        
        print(f"[VectorDB] Loaded session {session_id}: {index.ntotal} vectors")
        return index, chunks
    index = faiss.IndexFlatL2(384)
    print(f"[VectorDB] New session {session_id}")
    return index, []


def _save(session_id: str, index, chunks: list):
    """Persist index + metadata for this session."""
    faiss.write_index(index, _index_path(session_id))
    with open(_meta_path(session_id), 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)


def _load_global():
    """Return (faiss_index, chunks_list) for global knowledge base."""
    idx_p = _global_index_path()
    met_p = _global_meta_path()
    if os.path.exists(idx_p) and os.path.exists(met_p):
        index = faiss.read_index(idx_p)
        with open(met_p, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        chunks = _upgrade_chunks_metadata(chunks)
        
        print(f"[VectorDB] Loaded global knowledge base: {index.ntotal} vectors")
        return index, chunks
    index = faiss.IndexFlatL2(384)
    print("[VectorDB] New global knowledge base")
    return index, []


def _save_global(index, chunks: list):
    """Persist global index + metadata."""
    faiss.write_index(index, _global_index_path())
    with open(_global_meta_path(), 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)


def _upgrade_chunks_metadata(chunks: list) -> list:
    """
    Upgrade old plain string chunks to metadata dicts.
    If chunk is already a dict, leave it alone.
    If chunk is a string, wrap it: {"text": chunk, "chunk_index": i, "section": "General", "word_count": ...}
    """
    upgraded = []
    for i, chunk in enumerate(chunks):
        if isinstance(chunk, dict):
            # Already has metadata
            upgraded.append(chunk)
        else:
            # Plain string, wrap it
            upgraded.append({
                "text": str(chunk),
                "chunk_index": i,
                "section": "General",
                "word_count": len(str(chunk).split())
            })
    return upgraded


def _normalize_chunk(chunk) -> dict:
    """
    Normalize a chunk to dict format.
    Accepts both string and dict; returns dict.
    """
    if isinstance(chunk, dict):
        return chunk
    else:
        return {
            "text": str(chunk),
            "chunk_index": 0,
            "section": "General",
            "word_count": len(str(chunk).split())
        }


# ── public API ────────────────────────────────────────────────────────────────

def add_documents(session_id: str, text_chunks: list):
    """
    Embed chunks and store them under this session's private index.
    
    Accepts:
    - list of strings (old behavior, backward compatible)
    - list of dicts with "text" key (new metadata-aware format)
    """
    if not text_chunks:
        return
    
    index, chunks = _load(session_id)
    
    # Normalize input chunks to dict format
    normalized_chunks = []
    embeddings_list = []
    
    for i, chunk in enumerate(text_chunks):
        normalized = _normalize_chunk(chunk)
        normalized["chunk_index"] = len(chunks) + i  # Update index
        normalized_chunks.append(normalized)
        embeddings_list.append(normalized["text"])
    
    # Encode all documents
    embeddings = list(model.embed(embeddings_list))
    
    # Add to FAISS index
    index.add(np.array(embeddings).astype('float32'))
    
    # Store normalized chunks in metadata
    chunks.extend(normalized_chunks)
    _save(session_id, index, chunks)
    
    print(f"[VectorDB] {len(text_chunks)} chunks stored for session {session_id}")


def add_global_documents(text_chunks: list, source_file: str = "unknown"):
    """
    Embed chunks and store them in the global knowledge base.
    
    Accepts:
    - list of strings or dicts
    - source_file: name of the source document for metadata
    """
    if not text_chunks:
        return
    
    index, chunks = _load_global()
    
    # Normalize input chunks to dict format
    normalized_chunks = []
    embeddings_list = []
    
    for i, chunk in enumerate(text_chunks):
        normalized = _normalize_chunk(chunk)
        normalized["chunk_index"] = len(chunks) + i
        normalized["source"] = source_file  # Add source metadata
        normalized_chunks.append(normalized)
        embeddings_list.append(normalized["text"])
    
    # Encode all documents
    embeddings = list(model.embed(embeddings_list))
    
    # Add to FAISS index
    index.add(np.array(embeddings).astype('float32'))
    
    # Store normalized chunks in metadata
    chunks.extend(normalized_chunks)
    _save_global(index, chunks)
    
    print(f"[VectorDB] {len(text_chunks)} chunks stored in global knowledge base from {source_file}")


def search(session_id: str, query: str, top_k: int = 3) -> list:
    """
    Search this session's private index with reranking.
    
    Returns list of dicts: [{"text": "...", "section": "...", "score": 0.87}, ...]
    """
    index, chunks = _load(session_id)
    
    if index.ntotal == 0:
        return [{"text": "No documents found in memory. Please upload a PDF first.", "section": "General", "score": 0.0}]
    
    # Step 1: Fetch more candidates for reranking (top_k * 3)
    candidate_k = min(top_k * 3, index.ntotal)
    
    # Encode query with BGE prefix for search
    query_with_prefix = BGE_QUERY_PREFIX + query
    query_vec = list(model.embed([query_with_prefix]))
    
    # Search FAISS
    distances, indices = index.search(np.array(query_vec).astype('float32'), candidate_k)
    
    # Step 2 & 3: Rerank by cosine similarity and keyword boost
    candidates_with_scores = []
    
    for dist_idx, chunk_idx in enumerate(indices[0]):
        if chunk_idx == -1 or chunk_idx >= len(chunks):
            continue
        
        chunk_data = chunks[chunk_idx]
        chunk_text = chunk_data["text"] if isinstance(chunk_data, dict) else str(chunk_data)
        chunk_section = chunk_data.get("section", "General") if isinstance(chunk_data, dict) else "General"
        
        # Convert L2 distance to similarity (1 / (1 + distance))
        l2_distance = distances[0][dist_idx]
        cosine_score = 1.0 / (1.0 + l2_distance)
        
        # Step 3: Boost score for query keywords found in chunk
        boost = 0.0
        query_words = [w for w in query.lower().split() if len(w) > 3]  # Words > 3 chars
        chunk_text_lower = chunk_text.lower()
        
        for word in query_words:
            if word in chunk_text_lower:
                boost += 0.1
        
        boost = min(boost, 0.3)  # Cap boost at 0.3 to avoid over-boosting
        final_score = min(cosine_score + boost, 1.0)
        
        candidates_with_scores.append({
            "text": chunk_text,
            "section": chunk_section,
            "score": final_score,
            "idx": chunk_idx
        })
    
    # Step 4: Sort by final score and return top_k
    candidates_with_scores.sort(key=lambda x: x["score"], reverse=True)
    
    results = []
    for candidate in candidates_with_scores[:top_k]:
        results.append({
            "text": candidate["text"],
            "section": candidate["section"],
            "score": round(candidate["score"], 4)
        })
    
    return results


def search_global(query: str, top_k: int = 3) -> list:
    """
    Search the global knowledge base with reranking.
    
    Returns list of dicts: [{"text": "...", "section": "...", "source": "...", "score": 0.87}, ...]
    """
    index, chunks = _load_global()
    
    if index.ntotal == 0:
        return []
    
    # Step 1: Fetch more candidates for reranking (top_k * 3)
    candidate_k = min(top_k * 3, index.ntotal)
    
    # Encode query with BGE prefix for search
    query_with_prefix = BGE_QUERY_PREFIX + query
    query_vec = list(model.embed([query_with_prefix]))
    
    # Search FAISS
    distances, indices = index.search(np.array(query_vec).astype('float32'), candidate_k)
    
    # Step 2 & 3: Rerank by cosine similarity and keyword boost
    candidates_with_scores = []
    
    for dist_idx, chunk_idx in enumerate(indices[0]):
        if chunk_idx == -1 or chunk_idx >= len(chunks):
            continue
        
        chunk_data = chunks[chunk_idx]
        chunk_text = chunk_data["text"] if isinstance(chunk_data, dict) else str(chunk_data)
        chunk_section = chunk_data.get("section", "General") if isinstance(chunk_data, dict) else "General"
        chunk_source = chunk_data.get("source", "unknown") if isinstance(chunk_data, dict) else "unknown"
        
        # Convert L2 distance to similarity (1 / (1 + distance))
        l2_distance = distances[0][dist_idx]
        cosine_score = 1.0 / (1.0 + l2_distance)
        
        # Step 3: Boost score for query keywords found in chunk
        boost = 0.0
        query_words = [w for w in query.lower().split() if len(w) > 3]  # Words > 3 chars
        chunk_text_lower = chunk_text.lower()
        
        for word in query_words:
            if word in chunk_text_lower:
                boost += 0.1
        
        boost = min(boost, 0.3)  # Cap boost at 0.3 to avoid over-boosting
        final_score = min(cosine_score + boost, 1.0)
        
        candidates_with_scores.append({
            "text": chunk_text,
            "section": chunk_section,
            "source": chunk_source,
            "score": final_score,
            "idx": chunk_idx
        })
    
    # Step 4: Sort by final score and return top_k
    candidates_with_scores.sort(key=lambda x: x["score"], reverse=True)
    
    results = []
    for candidate in candidates_with_scores[:top_k]:
        results.append({
            "text": candidate["text"],
            "section": candidate["section"],
            "source": candidate["source"],
            "score": round(candidate["score"], 4)
        })
    
    return results


def get_session_stats(session_id: str) -> dict:
    """Get statistics about this session's stored documents."""
    index, chunks = _load(session_id)
    
    # Collect unique sections
    sections = set()
    for chunk in chunks:
        if isinstance(chunk, dict):
            sections.add(chunk.get("section", "General"))
        else:
            sections.add("General")
    
    return {
        "total_chunks": index.ntotal,
        "sections": sorted(list(sections)),
        "index_size": index.ntotal
    }


# ── Chat history management ───────────────────────────────────────────────────

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
            json.dump(chat_history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[VectorDB] Error saving chat history: {e}")


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