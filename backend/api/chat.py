from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from services.vector_service import search
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

    context_text = "\n\n".join(context_chunks)
    rag_prompt = f"""Use the following document context to answer the user's question.

CONTEXT:
{context_text}

QUESTION:
{request.question}
"""
    try:
        answer = get_chat_answer(rag_prompt)
        return {"answer": answer}
    except Exception as e:
        print(f"❌ Chat Error: {e}")
        return {"answer": "The AI service is currently busy. Please try again in a moment."}
