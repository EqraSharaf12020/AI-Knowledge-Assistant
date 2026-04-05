from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from services.vector_service import search, search_global, add_chat_message, get_chat_history
from services.llm_service import get_chat_answer

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str


@router.post("/")
async def chat_with_document(
    request: ChatRequest,
    x_session_id: Optional[str] = Header(None),
):
    if not x_session_id or not x_session_id.strip():
        raise HTTPException(status_code=400, detail="Missing X-Session-Id header.")

    session_id = x_session_id.strip()

    # Search both session-specific and global knowledge base
    session_chunks = search(session_id, request.question, top_k=3)
    global_chunks = search_global(request.question, top_k=3)

    # Combine and sort by score, take top 5
    all_chunks = session_chunks + global_chunks
    all_chunks.sort(key=lambda x: x.get("score", 0), reverse=True)
    context_chunks = all_chunks[:5]

    # Check if no documents available
    if not context_chunks:
        return {"answer": "I don't have any documents in my memory. Please upload a PDF first!"}
    
    # Handle case where search returns error message
    if len(context_chunks) == 1 and "No documents found" in context_chunks[0].get("text", ""):
        return {"answer": "I don't have any documents in my memory. Please upload a PDF first!"}

    # Build context text from chunks (now dicts with metadata)
    context_parts = []
    section_references = set()
    source_references = set()

    for chunk in context_chunks:
        chunk_text = chunk.get("text", "")
        chunk_section = chunk.get("section", "General")
        chunk_source = chunk.get("source", "")

        if chunk_text and "No documents" not in chunk_text:
            context_parts.append(chunk_text)
            section_references.add(chunk_section)
            if chunk_source:
                source_references.add(chunk_source)

    if not context_parts:
        return {"answer": "I don't have any documents in my memory. Please upload a PDF first!"}

    # Format section references as comma-separated list
    section_references_str = ", ".join(sorted(section_references)) if section_references else "General"
    if source_references:
        section_references_str += f" (from: {', '.join(sorted(source_references))})"

    # Get conversation history
    chat_history = get_chat_history(session_id)
    
    # Format conversation history for the prompt
    history_text = ""
    if chat_history:
        history_lines = []
        for msg in chat_history[-10:]:  # Include last 10 messages to keep context manageable
            role = "User" if msg["role"] == "user" else "Assistant"
            history_lines.append(f"{role}: {msg['message']}")
        history_text = "\n".join(history_lines) + "\n\n"

    context_text = "\n\n".join(context_parts)
    rag_prompt = f"""Use the following document context and conversation history to answer the user's question.

DOCUMENT CONTEXT:
{context_text}

SECTIONS REFERENCED: {section_references_str}

CONVERSATION HISTORY:
{history_text}User: {request.question}

Assistant:"""

    try:
        answer = get_chat_answer(rag_prompt)
        
        # Store the conversation
        add_chat_message(session_id, "user", request.question)
        add_chat_message(session_id, "assistant", answer)
        
        return {"answer": answer}
    except Exception as e:
        print(f"❌ Chat Error: {e}")
        return {"answer": "The AI service is currently busy. Please try again in a moment."}
