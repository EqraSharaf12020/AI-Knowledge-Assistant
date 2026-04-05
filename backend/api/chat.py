from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from services.vector_service import search, add_chat_message, get_chat_history
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
    context_chunks = search(session_id, request.question, top_k=3)   # ← isolated

    if not context_chunks or "No documents" in str(context_chunks[0]):
        return {"answer": "I don't have any documents in my memory. Please upload a PDF first!"}

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

    context_text = "\n\n".join(context_chunks)
    rag_prompt = f"""Use the following document context and conversation history to answer the user's question.

DOCUMENT CONTEXT:
{context_text}

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
