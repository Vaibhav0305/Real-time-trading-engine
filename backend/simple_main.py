from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="VittCott Trading Platform", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "VittCott Trading Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "VittCott Backend"}

@app.get("/api/v1/chatbot/chat/history/{user_id}")
async def get_chat_history(user_id: str):
    return {
        "success": True,
        "messages": [
            {"id": 1, "content": "Welcome to VittCott!", "timestamp": "2024-01-01T00:00:00Z"}
        ]
    }

@app.post("/api/v1/auth/login")
async def login():
    return {"success": True, "message": "Login endpoint ready"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
