from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import json
import re

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
        # 2. Save the PDF temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. Extract text from PDF
        document_text = extract_text_from_pdf(temp_path)

        if not document_text or "Error" in document_text:
            raise HTTPException(status_code=500, detail="Could not read PDF content.")

        # 4. Split into chunks and store in Vector DB (for /chat)
        chunks = split_text_into_chunks(document_text)
        vector_store.add_documents(chunks)

        # 5. Get structured risk analysis from LLM (first 8000 chars)
        raw_result = get_legal_analysis(document_text[:8000])

        # 6. Parse the JSON string returned by the LLM
        try:
            # Strip markdown code fences if the model wrapped the JSON
            cleaned = re.sub(r"```(?:json)?", "", raw_result).strip().rstrip("```").strip()
            analysis_parsed = json.loads(cleaned)
        except (json.JSONDecodeError, TypeError):
            print(f"⚠️ Could not parse LLM JSON output: {raw_result[:200]}")
            # Fallback: return a safe empty risks structure
            analysis_parsed = {"risks": [], "raw": raw_result}

        # 7. Cleanup temp file
        os.remove(temp_path)

        return {
            "status": "success",
            "fileName": file.filename,
            "totalChunksStored": len(chunks),
            "analysis": analysis_parsed
        }

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))
