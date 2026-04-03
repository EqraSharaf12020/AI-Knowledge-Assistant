from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os


# Connecting the "Brain" (Person 1), "Eyes" (Person 2), and "Memory" (Person 4)
from services.pdf_service import extract_text_from_pdf
from services.llm_service import get_legal_analysis
from services.vector_service import vector_store
from rag.chunking import split_text_into_chunks

router = APIRouter(prefix="/analyze", tags=["Analysis"])

@router.post("/")
async def analyze_document(file: UploadFile = File(...)):
    # 1. Validation
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_path = f"temp_{file.filename}"
    
    try:
        # 2. Save the PDF locally so the services can read it
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. EXTRACT: Call Person 2's code to get the raw text
        document_text = extract_text_from_pdf(temp_path)
        
        if not document_text or "Error" in document_text:
            raise HTTPException(status_code=500, detail="Could not read PDF content.")

        # 4. MEMORIZE (New!): Split into chunks and save to Vector DB (Person 4)
        # This allows the /chat route to work later
        chunks = split_text_into_chunks(document_text)
        vector_store.add_documents(chunks)

        # 5. ANALYZE: Call Person 1's code to get the high-level Risk Report
        # (Using the first 8000 chars to avoid token limits)
        analysis_result = get_legal_analysis(document_text[:8000])

        # 6. CLEANUP: Remove the temporary file
        os.remove(temp_path)

        # 7. RESPONSE: Return everything the Frontend needs
        return {
            "status": "success",
            "fileName": file.filename,
            "totalChunksStored": len(chunks),
            "analysis": analysis_result
        }

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))