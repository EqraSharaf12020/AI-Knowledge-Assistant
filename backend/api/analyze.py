from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import json
import re
import difflib

from services.pdf_service import extract_text_from_pdf
from services.llm_service import get_legal_analysis
from services.vector_service import add_global_documents
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
        add_global_documents(chunks, source_file=file.filename)

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

@router.post("/compare")
async def compare_documents(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    # Validation
    if not (file1.filename.endswith(".pdf") and file2.filename.endswith(".pdf")):
        raise HTTPException(status_code=400, detail="Both files must be PDFs.")

    temp_path1 = f"temp_{file1.filename}"
    temp_path2 = f"temp_{file2.filename}"

    try:
        # Save both PDFs temporarily
        with open(temp_path1, "wb") as buffer:
            shutil.copyfileobj(file1.file, buffer)
        with open(temp_path2, "wb") as buffer:
            shutil.copyfileobj(file2.file, buffer)

        # Extract text from both
        text1 = extract_text_from_pdf(temp_path1)
        text2 = extract_text_from_pdf(temp_path2)

        if not text1 or "Error" in text1 or not text2 or "Error" in text2:
            raise HTTPException(status_code=500, detail="Could not read PDF content.")

        # Compute text diff
        differ = difflib.HtmlDiff()
        diff_html = differ.make_file(
            text1.splitlines(),
            text2.splitlines(),
            fromdesc=file1.filename,
            todesc=file2.filename
        )

        # Analyze risks for both
        analysis1 = get_legal_analysis(text1[:8000])
        analysis2 = get_legal_analysis(text2[:8000])

        # Parse analyses
        def parse_analysis(raw):
            try:
                cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()
                return json.loads(cleaned)
            except:
                return {"risks": [], "raw": raw}

        parsed1 = parse_analysis(analysis1)
        parsed2 = parse_analysis(analysis2)

        # Compute risk deltas
        risks1 = parsed1.get("risks", [])
        risks2 = parsed2.get("risks", [])

        # Simple comparison: find new/removed/modified risks by clause text
        clauses1 = {risk.get("clause", ""): risk for risk in risks1}
        clauses2 = {risk.get("clause", ""): risk for risk in risks2}

        new_risks = []
        removed_risks = []
        modified_risks = []

        for clause, risk in clauses2.items():
            if clause not in clauses1:
                new_risks.append(risk)
            elif clauses1[clause] != risk:
                modified_risks.append({"old": clauses1[clause], "new": risk})

        for clause, risk in clauses1.items():
            if clause not in clauses2:
                removed_risks.append(risk)

        # Calculate score deltas (assuming same weights as frontend)
        weights = {"High": 35, "Medium": 18, "Low": 8}
        score1 = sum(weights.get(r.get("type", "Low"), 0) for r in risks1)
        score2 = sum(weights.get(r.get("type", "Low"), 0) for r in risks2)
        score_delta = score2 - score1

        # Store chunks from both in vector DB (for chat), tagged with their own source file
        chunks1 = split_text_into_chunks(text1)
        chunks2 = split_text_into_chunks(text2)
        add_global_documents(chunks1, source_file=file1.filename)
        add_global_documents(chunks2, source_file=file2.filename)

        # Cleanup
        os.remove(temp_path1)
        os.remove(temp_path2)

        return {
            "status": "success",
            "file1": file1.filename,
            "file2": file2.filename,
            "text_diff_html": diff_html,
            "analysis1": parsed1,
            "analysis2": parsed2,
            "risk_comparison": {
                "new_risks": new_risks,
                "removed_risks": removed_risks,
                "modified_risks": modified_risks,
                "score_delta": score_delta
            },
            "total_chunks_stored": len(chunks1) + len(chunks2)
        }

    except Exception as e:
        for path in [temp_path1, temp_path2]:
            if os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=500, detail=str(e))