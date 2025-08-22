from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="VittCott Advanced Trading Platform",
    description="Professional stock trading platform with real-time data",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Finnhub API Key
FINNHUB_API_KEY = "d2ccu61r01qihtcr6m2gd2ccu61r01qihtcr6m30"

# Data Models
class Order(BaseModel):
    id: str
    symbol: str
    side: str  # BUY or SELL
    type: str  # MARKET, LIMIT, STOP
    quantity: int
    price: Optional[float]
    validity: str
    status: str
    timestamp: str
    user_id: str

class PortfolioHolding(BaseModel):
    symbol: str
    quantity: int
    avg_price: float
    current_price: float
    pnl: float
    pnl_percent: float

class MarketData(BaseModel):
    symbol: str
    current_price: float
    change: float
    change_percent: float
    volume: int
    market_cap: float
    high_24h: float
    low_24h: float
    open_price: float
    previous_close: float

# Global data storage (in production, use database)
orders_db: List[Order] = []
portfolio_db: List[PortfolioHolding] = []
watchlist_db: List[str] = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "NFLX", "JPM", "JNJ"]
websocket_connections: List[WebSocket] = []

# Simulated market data
def generate_market_data(symbol: str) -> MarketData:
    """Generate realistic market data for a symbol"""
    base_price = {
        'AAPL': 180, 'GOOGL': 3000, 'MSFT': 350, 'TSLA': 250,
        'AMZN': 150, 'META': 400, 'NVDA': 800, 'NFLX': 600,
        'JPM': 150, 'JNJ': 160
    }.get(symbol, 100)
    
    # Simulate price movement
    change_percent = random.uniform(-5, 5)
    change = base_price * (change_percent / 100)
    current_price = base_price + change
    
    return MarketData(
        symbol=symbol,
        current_price=round(current_price, 2),
        change=round(change, 2),
        change_percent=round(change_percent, 2),
        volume=random.randint(1000000, 10000000),
        market_cap=current_price * random.randint(1000000, 100000000),
        high_24h=current_price * (1 + random.uniform(0, 0.1)),
        low_24h=current_price * (1 - random.uniform(0, 0.1)),
        open_price=base_price,
        previous_close=base_price
    )

def generate_portfolio_data() -> List[PortfolioHolding]:
    """Generate sample portfolio data"""
    symbols = ["AAPL", "GOOGL", "MSFT"]
    holdings = []
    
    for symbol in symbols:
        current_data = generate_market_data(symbol)
        quantity = random.randint(50, 200)
        avg_price = current_data.current_price * random.uniform(0.8, 1.2)
        pnl = (current_data.current_price - avg_price) * quantity
        
        holdings.append(PortfolioHolding(
            symbol=symbol,
            quantity=quantity,
            avg_price=round(avg_price, 2),
            current_price=current_data.current_price,
            pnl=round(pnl, 2),
            pnl_percent=round((pnl / (avg_price * quantity)) * 100, 2)
        ))
    
    return holdings

# Initialize sample data
portfolio_db = generate_portfolio_data()

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("🚀 Starting VittCott Advanced Trading Platform...")
    logger.info(f"📊 Using Finnhub API key: {FINNHUB_API_KEY[:10]}...")
    logger.info("🌐 Server will be available at: http://127.0.0.1:8000")
    logger.info("📖 API docs at: http://127.0.0.1:8000/docs")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "VittCott Advanced Trading Platform",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Market Data Endpoints
@app.get("/api/v1/market/overview")
async def get_market_overview():
    """Get market overview with major indices"""
    try:
        indices = ["^GSPC", "^DJI", "^IXIC", "^RUT"]  # S&P 500, Dow, NASDAQ, Russell
        market_data = {}
        
        for index in indices:
            market_data[index] = generate_market_data(index)
        
        return {
            "status": "success",
            "data": {
                "indices": market_data,
                "market_status": "OPEN",
                "last_updated": datetime.now().isoformat(),
                "total_volume": sum(data.volume for data in market_data.values()),
                "advancing": len([d for d in market_data.values() if d.change > 0]),
                "declining": len([d for d in market_data.values() if d.change < 0])
            }
        }
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market overview")

@app.get("/api/v1/market/price/{symbol}")
async def get_stock_price(symbol: str):
    """Get real-time price for a specific symbol"""
    try:
        market_data = generate_market_data(symbol.upper())
        return {
            "status": "success",
            "data": market_data
        }
    except Exception as e:
        logger.error(f"Error getting price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get price for {symbol}")

@app.get("/api/v1/market/prices")
async def get_multiple_prices(symbols: str):
    """Get prices for multiple symbols (comma-separated)"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        prices = {}
        
        for symbol in symbol_list:
            prices[symbol] = generate_market_data(symbol)
        
        return {
            "status": "success",
            "data": prices
        }
    except Exception as e:
        logger.error(f"Error getting multiple prices: {e}")
        raise HTTPException(status_code=500, detail="Failed to get multiple prices")

@app.get("/api/v1/market/search")
async def search_symbols(query: str):
    """Search for symbols by name or symbol"""
    try:
        all_symbols = [
            {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ"},
            {"symbol": "NFLX", "name": "Netflix Inc.", "exchange": "NASDAQ"},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE"},
            {"symbol": "JNJ", "name": "Johnson & Johnson", "exchange": "NYSE"}
        ]
        
        query_lower = query.lower()
        results = [
            symbol for symbol in all_symbols
            if query_lower in symbol["symbol"].lower() or query_lower in symbol["name"].lower()
        ]
        
        return {
            "status": "success",
            "data": results[:10]  # Limit to 10 results
        }
    except Exception as e:
        logger.error(f"Error searching symbols: {e}")
        raise HTTPException(status_code=500, detail="Failed to search symbols")

# Portfolio Endpoints
@app.get("/api/v1/portfolio/overview")
async def get_portfolio_overview():
    """Get portfolio overview and summary"""
    try:
        total_value = sum(holding.current_price * holding.quantity for holding in portfolio_db)
        total_cost = sum(holding.avg_price * holding.quantity for holding in portfolio_db)
        total_pnl = total_value - total_cost
        total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        return {
            "status": "success",
            "data": {
                "total_value": round(total_value, 2),
                "total_cost": round(total_cost, 2),
                "total_pnl": round(total_pnl, 2),
                "total_pnl_percent": round(total_pnl_percent, 2),
                "holdings_count": len(portfolio_db),
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting portfolio overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get portfolio overview")

@app.get("/api/v1/portfolio/holdings")
async def get_portfolio_holdings():
    """Get all portfolio holdings"""
    try:
        return {
            "status": "success",
            "data": portfolio_db
        }
    except Exception as e:
        logger.error(f"Error getting portfolio holdings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get portfolio holdings")

# Order Management Endpoints
@app.post("/api/v1/orders/place")
async def place_order(order_data: dict):
    """Place a new order"""
    try:
        order = Order(
            id=f"ORDER_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
            symbol=order_data["symbol"],
            side=order_data["side"],
            type=order_data["type"],
            quantity=order_data["quantity"],
            price=order_data.get("price"),
            validity=order_data.get("validity", "DAY"),
            status="PENDING",
            timestamp=datetime.now().isoformat(),
            user_id=order_data.get("user_id", "default_user")
        )
        
        orders_db.append(order)
        
        # Simulate order processing
        await asyncio.sleep(1)
        
        # Update order status (simulate market execution)
        if order.type == "MARKET":
            order.status = "FILLED"
        else:
            order.status = "PENDING"
        
        # Notify connected WebSocket clients
        await notify_order_update(order)
        
        return {
            "status": "success",
            "message": "Order placed successfully",
            "data": {
                "order_id": order.id,
                "status": order.status
            }
        }
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        raise HTTPException(status_code=500, detail="Failed to place order")

@app.get("/api/v1/orders")
async def get_orders(user_id: str = "default_user", status: Optional[str] = None):
    """Get orders for a user"""
    try:
        user_orders = [order for order in orders_db if order.user_id == user_id]
        
        if status:
            user_orders = [order for order in user_orders if order.status == status.upper()]
        
        return {
            "status": "success",
            "data": user_orders
        }
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to get orders")

@app.get("/api/v1/orders/{order_id}")
async def get_order(order_id: str):
    """Get specific order by ID"""
    try:
        order = next((order for order in orders_db if order.id == order_id), None)
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {
            "status": "success",
            "data": order
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order {order_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get order")

# Watchlist Endpoints
@app.get("/api/v1/watchlist")
async def get_watchlist():
    """Get user's watchlist"""
    try:
        watchlist_data = []
        for symbol in watchlist_db:
            market_data = generate_market_data(symbol)
            watchlist_data.append({
                "symbol": symbol,
                "name": get_company_name(symbol),
                "current_price": market_data.current_price,
                "change": market_data.change,
                "change_percent": market_data.change_percent,
                "volume": market_data.volume
            })
        
        return {
            "status": "success",
            "data": watchlist_data
        }
    except Exception as e:
        logger.error(f"Error getting watchlist: {e}")
        raise HTTPException(status_code=500, detail="Failed to get watchlist")

@app.post("/api/v1/watchlist/add")
async def add_to_watchlist(symbol: str):
    """Add symbol to watchlist"""
    try:
        if symbol.upper() not in watchlist_db:
            watchlist_db.append(symbol.upper())
        
        return {
            "status": "success",
            "message": f"{symbol} added to watchlist"
        }
    except Exception as e:
        logger.error(f"Error adding to watchlist: {e}")
        raise HTTPException(status_code=500, detail="Failed to add to watchlist")

@app.delete("/api/v1/watchlist/remove/{symbol}")
async def remove_from_watchlist(symbol: str):
    """Remove symbol from watchlist"""
    try:
        if symbol.upper() in watchlist_db:
            watchlist_db.remove(symbol.upper())
        
        return {
            "status": "success",
            "message": f"{symbol} removed from watchlist"
        }
    except Exception as e:
        logger.error(f"Error removing from watchlist: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove from watchlist")

# WebSocket for real-time updates
@app.websocket("/api/v1/ws/market-data")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time market data"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            # Send real-time updates every 2 seconds
            await asyncio.sleep(2)
            
            # Generate updated market data for watchlist
            market_updates = {}
            for symbol in watchlist_db:
                market_data = generate_market_data(symbol)
                market_updates[symbol] = {
                    "current_price": market_data.current_price,
                    "change": market_data.change,
                    "change_percent": market_data.change_percent,
                    "volume": market_data.volume,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Send updates to client
            await websocket.send_text(json.dumps({
                "type": "market_update",
                "data": market_updates
            }))
            
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

async def notify_order_update(order: Order):
    """Notify all connected WebSocket clients about order updates"""
    if websocket_connections:
        message = {
            "type": "order_update",
            "data": {
                "order_id": order.id,
                "symbol": order.symbol,
                "status": order.status,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        for connection in websocket_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")

def get_company_name(symbol: str) -> str:
    """Get company name for a symbol"""
    names = {
        'AAPL': 'Apple Inc.',
        'GOOGL': 'Alphabet Inc.',
        'MSFT': 'Microsoft Corporation',
        'TSLA': 'Tesla Inc.',
        'AMZN': 'Amazon.com Inc.',
        'META': 'Meta Platforms Inc.',
        'NVDA': 'NVIDIA Corporation',
        'NFLX': 'Netflix Inc.',
        'JPM': 'JPMorgan Chase & Co.',
        'JNJ': 'Johnson & Johnson',
        '^GSPC': 'S&P 500 Index',
        '^DJI': 'Dow Jones Industrial Average',
        '^IXIC': 'NASDAQ Composite',
        '^RUT': 'Russell 2000 Index'
    }
    return names.get(symbol, symbol)

# Market Scanner Endpoint
@app.get("/api/v1/market/scanner")
async def market_scanner(
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_volume: Optional[int] = None,
    min_change_percent: Optional[float] = None
):
    """Market scanner to find stocks matching criteria"""
    try:
        all_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "NFLX", "JPM", "JNJ"]
        results = []
        
        for symbol in all_symbols:
            market_data = generate_market_data(symbol)
            
            # Apply filters
            if min_price and market_data.current_price < min_price:
                continue
            if max_price and market_data.current_price > max_price:
                continue
            if min_volume and market_data.volume < min_volume:
                continue
            if min_change_percent and abs(market_data.change_percent) < min_change_percent:
                continue
            
            results.append({
                "symbol": symbol,
                "name": get_company_name(symbol),
                "current_price": market_data.current_price,
                "change": market_data.change,
                "change_percent": market_data.change_percent,
                "volume": market_data.volume,
                "market_cap": market_data.market_cap
            })
        
        return {
            "status": "success",
            "data": results,
            "filters_applied": {
                "min_price": min_price,
                "max_price": max_price,
                "min_volume": min_volume,
                "min_change_percent": min_change_percent
            }
        }
    except Exception as e:
        logger.error(f"Error in market scanner: {e}")
        raise HTTPException(status_code=500, detail="Failed to run market scanner")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


