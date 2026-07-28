from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.vector_service import search_global
from services.llm_service import get_chat_answer

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    question: str

@router.post("/")
async def chat_with_document(request: ChatRequest):
    # 1. SEARCH: Get relevant context from the global knowledge base
    context_chunks = search_global(request.question, top_k=3)

    if not context_chunks:
        return {"answer": "I don't have any documents in my memory. Please upload a PDF first!"}

    context_text = "\n\n".join(chunk["text"] for chunk in context_chunks)

    # 2. PROMPT: Build the RAG prompt with context
    rag_prompt = f"""Use the following document context to answer the user's question.

CONTEXT:
{context_text}

QUESTION:
{request.question}
"""

    # 3. GENERATE: Get answer from LLM with system prompt
    try:
        answer = get_chat_answer(rag_prompt)
        return {"answer": answer}
    except Exception as e:
        print(f"❌ Chat Error: {e}")
        return {"answer": "The AI service is currently busy. Please try again in a moment."}