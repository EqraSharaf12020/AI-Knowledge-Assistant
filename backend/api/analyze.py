from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os

# Connecting the "Brain" and "Eyes"
from services.pdf_service import extract_text_from_pdf
from services.llm_service import get_legal_analysis

router = APIRouter(prefix="/analyze", tags=["Analysis"])

@router.post("/")
async def analyze_document(file: UploadFile = File(...)):
    # 1. Validation: Only allow PDFs
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # 2. Temporary Storage Path
    temp_path = f"temp_{file.filename}"
    
    try:
        # 3. Save the uploaded file to your laptop temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 4. Step 1: Call Person 2's code to get the text
        document_text = extract_text_from_pdf(temp_path)
        
        if not document_text or "Error" in document_text:
            raise HTTPException(status_code=500, detail="Could not read PDF content.")

        # 5. Step 2: Call Person 1's code to get AI Analysis
        # (We send the first 8000 characters to stay within Groq limits)
        analysis_result = get_legal_analysis(document_text[:8000])

        # 6. Cleanup: Delete the temp file
        os.remove(temp_path)
        # 7. Return final JSON to the Frontend (Person 5)
        return {
            "status": "success",
            "fileName": file.filename,
            "analysis": analysis_result
        }

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))