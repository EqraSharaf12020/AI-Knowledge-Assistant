from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.vector_service import vector_store
from services.llm_service import get_legal_analysis

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    question: str

@router.post("/")
async def chat_with_document(request: ChatRequest):
    # 1. SEARCH: Get relevant context
    # This calls Person 4's Vector DB
    context_chunks = vector_store.search(request.question, top_k=3)
    
    if not context_chunks or "No documents" in str(context_chunks[0]):
        return {"answer": "I don't have any documents in my memory. Please upload a PDF first!"}

    context_text = "\n".join(context_chunks)

    # 2. PROMPT: Construct the instruction
    rag_prompt = f"""
    You are a professional Legal Assistant. 
    Use the following context to answer the question. 
    If the answer is not in the context, say 'I cannot find this in the uploaded document.'

    CONTEXT:
    {context_text}
    
    QUESTION:
    {request.question}
    """

    # 3. GENERATE: Get answer from Person 1's LLM service
    try:
        raw_answer = get_legal_analysis(rag_prompt)
        
        # Ensure we are sending a string, not a dictionary or object
        # If Person 1's code returns a dict, we extract the text
        final_text = raw_answer["choices"][0]["message"]["content"] if isinstance(raw_answer, dict) else str(raw_answer)

        return {"answer": final_text}
        
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return {"answer": "The AI service is currently busy. Please try again in a moment."}