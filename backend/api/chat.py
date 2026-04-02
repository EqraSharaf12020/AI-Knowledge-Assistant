from fastapi import APIRouter
router = APIRouter(prefix="/chat", tags=["Chat"])

@router.get("/")
def test_chat():
    return {"message": "Chat route ready"}