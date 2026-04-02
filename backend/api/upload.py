from fastapi import APIRouter
router = APIRouter(prefix="/upload", tags=["Upload"])

@router.get("/")
def test_upload():
    return {"message": "Upload route ready"}