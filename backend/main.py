import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import upload, chat, analyze

app = FastAPI(title="Legal AI Knowledge Assistant")

# Essential for React Frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(analyze.router)

@app.get("/")
def home():
    return {"status": "online", "message": "Legal AI Backend is Running"}

if __name__ == "__main__":
    # Using 0.0.0.0 makes it accessible on your local network/MNNIT wifi
    uvicorn.run(app, host="0.0.0.0", port=8000)