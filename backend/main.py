from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

from routes.auth_routes import router as auth_router
from routes.trading_routes import router as trading_router
from routes.algo_trading_routes import router as algo_trading_router
from routes.chatbot_routes import router as chatbot_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('backend.log')
    ]
)

app = FastAPI(
    title="VittCott Trading Platform API",
    description="Real-time stock trading engine with C++ matching engine",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "Welcome to VittCott Trading Platform Backend!",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

# Enable CORS for frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(trading_router, prefix="/api/v1", tags=["Trading"])
app.include_router(algo_trading_router, prefix="/api/v1/algo", tags=["Algorithmic Trading"])
app.include_router(chatbot_router, prefix="/api/v1/chatbot", tags=["AI Chatbot"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
