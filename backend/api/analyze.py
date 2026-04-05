from fastapi import APIRouter, UploadFile, File, HTTPException, Header
import shutil, os, json, re, difflib
from typing import Optional

from services.document_service import extract_text_from_file
from services.llm_service import get_legal_analysis
from services.vector_service import add_documents, get_session_stats
from rag.chunking import split_text_into_chunks

router = APIRouter(prefix="/analyze", tags=["Analysis"])


def _require_session(x_session_id: Optional[str]) -> str:
    if not x_session_id or not x_session_id.strip():
        raise HTTPException(status_code=400, detail="Missing X-Session-Id header.")
    return x_session_id.strip()


@router.post("/")
async def analyze_document(
    file: UploadFile = File(...),
    x_session_id: Optional[str] = Header(None),
):
    session_id = _require_session(x_session_id)

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_path = f"temp_{session_id}_{file.filename}"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        document_text = extract_text_from_file(temp_path)
        if not document_text or "Error" in document_text:
            raise HTTPException(status_code=500, detail="Could not read document content.")

        # Get chunks with metadata
        chunks = split_text_into_chunks(document_text, return_metadata=True)
        add_documents(session_id, chunks)           # ← isolated per session

        raw_result = get_legal_analysis(document_text[:8000])

        try:
            cleaned = re.sub(r"```(?:json)?", "", raw_result).strip().rstrip("```").strip()
            analysis_parsed = json.loads(cleaned)
        except (json.JSONDecodeError, TypeError):
            print(f"⚠️ Could not parse LLM JSON output: {raw_result[:200]}")
            analysis_parsed = {"risks": [], "raw": raw_result}

        # Get session stats
        session_stats = get_session_stats(session_id)

        os.remove(temp_path)

        return {
            "status": "success",
            "fileName": file.filename,
            "totalChunksStored": len(chunks),
            "sessionStats": session_stats,
            "analysis": analysis_parsed,
        }

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_documents(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    x_session_id: Optional[str] = Header(None),
):
    session_id = _require_session(x_session_id)

    if not (file1.filename.endswith(".pdf") and file2.filename.endswith(".pdf")):
        raise HTTPException(status_code=400, detail="Both files must be PDFs.")

    temp_path1 = f"temp_{session_id}_{file1.filename}"
    temp_path2 = f"temp_{session_id}_{file2.filename}"

    try:
        with open(temp_path1, "wb") as buffer:
            shutil.copyfileobj(file1.file, buffer)
        with open(temp_path2, "wb") as buffer:
            shutil.copyfileobj(file2.file, buffer)

        text1 = extract_text_from_file(temp_path1)
        text2 = extract_text_from_file(temp_path2)

        if not text1 or "Error" in text1 or not text2 or "Error" in text2:
            raise HTTPException(status_code=500, detail="Could not read document content.")

        differ = difflib.HtmlDiff()
        diff_html = differ.make_file(
            text1.splitlines(), text2.splitlines(),
            fromdesc=file1.filename, todesc=file2.filename,
        )

        analysis1 = get_legal_analysis(text1[:8000])
        analysis2 = get_legal_analysis(text2[:8000])

        def parse_analysis(raw):
            try:
                cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()
                return json.loads(cleaned)
            except Exception:
                return {"risks": [], "raw": raw}

        parsed1 = parse_analysis(analysis1)
        parsed2 = parse_analysis(analysis2)

        risks1 = parsed1.get("risks", [])
        risks2 = parsed2.get("risks", [])

        clauses1 = {r.get("clause", ""): r for r in risks1}
        clauses2 = {r.get("clause", ""): r for r in risks2}

        new_risks, removed_risks, modified_risks = [], [], []
        for clause, risk in clauses2.items():
            if clause not in clauses1:
                new_risks.append(risk)
            elif clauses1[clause] != risk:
                modified_risks.append({"old": clauses1[clause], "new": risk})
        for clause, risk in clauses1.items():
            if clause not in clauses2:
                removed_risks.append(risk)

        weights = {"High": 35, "Medium": 18, "Low": 8}
        score_delta = (
            sum(weights.get(r.get("type", "Low"), 0) for r in risks2)
            - sum(weights.get(r.get("type", "Low"), 0) for r in risks1)
        )

        # Get chunks with metadata
        chunks1 = split_text_into_chunks(text1, return_metadata=True)
        chunks2 = split_text_into_chunks(text2, return_metadata=True)
        add_documents(session_id, chunks1 + chunks2)   # ← isolated per session

        # Get session stats
        session_stats = get_session_stats(session_id)

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
                "score_delta": score_delta,
            },
            "total_chunks_stored": len(chunks1) + len(chunks2),
            "sessionStats": session_stats,
        }

    except Exception as e:
        for path in [temp_path1, temp_path2]:
            if os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=500, detail=str(e))
