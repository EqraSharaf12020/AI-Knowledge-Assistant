from fastapi import FastAPI
from api import upload, chat, analyze

app = FastAPI(title="Legal AI RAG API")

app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(analyze.router)

@app.get("/")
def home():
    return {"message": "Legal AI backend running"}

if __name__ == "__main__":
    import uvicorn
    # This starts the server on port 8000 and keeps it running
    uvicorn.run(app, host="0.0.0.0", port=8000)