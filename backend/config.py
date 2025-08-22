import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Database settings
    DATABASE_URL = "sqlite:///./vittcott.db"
    
    # Finnhub API settings - Using your actual API key!
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "d2ccu61r01qihtcr6m2gd2ccu61r01qihtcr6m30")
    FINNHUB_BASE_URL = os.getenv("FINNHUB_BASE_URL", "https://finnhub.io/api/v1")
    
    # Trading engine settings
    TRADING_ENGINE_PATH = "trading_engine.exe"
    
    # WebSocket settings
    WS_HEARTBEAT_INTERVAL = 30  # seconds
    
    # Rate limiting
    FINNHUB_RATE_LIMIT = 60  # requests per minute

settings = Settings()
