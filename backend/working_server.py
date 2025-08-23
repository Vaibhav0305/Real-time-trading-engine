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
    return {"message": "VittCott Trading Platform API - WORKING!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "VittCott Backend", "message": "Server is running!"}

@app.get("/api/v1/chatbot/chat/history/{user_id}")
async def get_chat_history(user_id: str):
    return {
        "success": True,
        "messages": [
            {"id": 1, "content": "Welcome to VittCott!", "timestamp": "2024-01-01T00:00:00Z"},
            {"id": 2, "content": "How can I help you with trading today?", "timestamp": "2024-01-01T00:00:01Z"}
        ]
    }

@app.post("/api/v1/auth/login")
async def login():
    return {"success": True, "message": "Login endpoint ready"}

@app.get("/api/v1/portfolio/overview")
async def portfolio_overview():
    return {
        "total_value": 50000.00,
        "total_pnl": 2500.00,
        "holdings": 5
    }

@app.get("/api/v1/watchlist")
async def watchlist():
    return {
        "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"],
        "count": 5
    }

if __name__ == "__main__":
    print("🚀 Starting VittCott Backend Server...")
    print("📍 Server will run on: http://localhost:8000")
    print("🔗 Health check: http://localhost:8000/health")
    print("📱 Frontend should connect to: http://localhost:3000")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
