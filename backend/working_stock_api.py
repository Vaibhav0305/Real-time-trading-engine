from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import json

app = FastAPI(title="VittCott Stock API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your Finnhub API key
FINNHUB_API_KEY = "d2ccu61r01qihtcr6m2gd2ccu61r01qihtcr6m30"
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

@app.get("/")
def home():
    return {
        "message": "VittCott Stock Trading Platform",
        "status": "running",
        "api": "Finnhub",
        "endpoints": {
            "stock_price": "/stock/{symbol}",
            "company_profile": "/profile/{symbol}",
            "market_data": "/market/overview"
        }
    }

@app.get("/stock/{symbol}")
def get_stock_price(symbol: str):
    """Get real-time stock price from Finnhub"""
    try:
        url = f"{FINNHUB_BASE_URL}/quote?symbol={symbol.upper()}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "symbol": symbol.upper(),
                "current_price": data.get('c', 0),
                "change": data.get('d', 0),
                "change_percent": data.get('dp', 0),
                "high": data.get('h', 0),
                "low": data.get('l', 0),
                "open": data.get('o', 0),
                "previous_close": data.get('pc', 0),
                "volume": data.get('v', 0),
                "timestamp": "2024-01-01T00:00:00Z"
            }
        else:
            return {"error": f"Failed to fetch data for {symbol}", "status_code": response.status_code}
            
    except Exception as e:
        return {"error": f"Error fetching stock data: {str(e)}"}

@app.get("/profile/{symbol}")
def get_company_profile(symbol: str):
    """Get company profile from Finnhub"""
    try:
        url = f"{FINNHUB_BASE_URL}/stock/profile2?symbol={symbol.upper()}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "symbol": symbol.upper(),
                "name": data.get('name', ''),
                "exchange": data.get('exchange', ''),
                "currency": data.get('currency', ''),
                "country": data.get('country', ''),
                "industry": data.get('finnhubIndustry', ''),
                "market_cap": data.get('marketCapitalization', 0)
            }
        else:
            return {"error": f"Failed to fetch profile for {symbol}", "status_code": response.status_code}
            
    except Exception as e:
        return {"error": f"Error fetching company profile: {str(e)}"}

@app.get("/market/overview")
def get_market_overview():
    """Get market overview with popular stocks"""
    popular_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA"]
    
    market_data = []
    for symbol in popular_symbols:
        try:
            url = f"{FINNHUB_BASE_URL}/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                market_data.append({
                    "symbol": symbol,
                    "current_price": data.get('c', 0),
                    "change": data.get('d', 0),
                    "change_percent": data.get('dp', 0)
                })
        except:
            continue
    
    return {
        "market_status": "Open",
        "stocks": market_data,
        "total_stocks": len(market_data)
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting VittCott Stock Trading Platform...")
    print(f"📊 Using Finnhub API key: {FINNHUB_API_KEY[:10]}...")
    print("🌐 Server will be available at: http://127.0.0.1:8000")
    print("📖 API docs at: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)


