from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from typing import List, Dict
import logging
from backend.services.market_data import market_data_service
from backend.services.websocket_manager import websocket_manager

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/search")
async def search_symbols(query: str = Query(..., min_length=1, description="Search for stocks, ETFs, or indices")):
    """Search for trading symbols like Zerodha"""
    try:
        if len(query) < 1:
            raise HTTPException(status_code=400, detail="Search query must be at least 1 character")
        
        results = await market_data_service.search_symbols(query)
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Error searching symbols: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search symbols")

@router.get("/depth/{symbol}")
async def get_market_depth(symbol: str):
    """Get market depth (bid/ask orders) like Zerodha"""
    try:
        depth = await market_data_service.get_market_depth(symbol.upper())
        if not depth:
            raise HTTPException(status_code=404, detail=f"No market depth available for {symbol}")
        return depth
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market depth for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch market depth")

@router.get("/overview")
async def get_market_overview():
    """Get comprehensive market overview like Zerodha dashboard"""
    try:
        overview = await market_data_service.get_market_overview()
        return overview
    except Exception as e:
        logger.error(f"Error fetching market overview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch market overview")

@router.get("/watchlist")
async def get_watchlist():
    """Get popular watchlist symbols with real-time prices"""
    try:
        # Popular symbols for watchlist
        watchlist_symbols = [
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX",
            "JPM", "JNJ", "V", "PG", "UNH", "HD", "PYPL", "ADBE"
        ]
        
        prices = await market_data_service.get_multiple_prices(watchlist_symbols)
        
        watchlist = []
        for symbol in watchlist_symbols:
            if symbol in prices:
                watchlist.append(prices[symbol])
        
        return {
            "watchlist": watchlist,
            "count": len(watchlist),
            "last_updated": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Error fetching watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch watchlist")

@router.get("/indices")
async def get_major_indices():
    """Get major market indices like S&P 500, Dow Jones, NASDAQ"""
    try:
        overview = await market_data_service.get_market_overview()
        return {
            "indices": overview.get("indices", {}),
            "market_status": overview.get("market_status", "Unknown"),
            "last_updated": overview.get("last_updated", "2024-01-01T00:00:00Z")
        }
    except Exception as e:
        logger.error(f"Error fetching indices: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch indices")

@router.get("/symbols")
async def get_symbols():
    """Get all available trading symbols with real-time prices"""
    try:
        symbols = await market_data_service.get_symbols()
        return {"symbols": symbols, "count": len(symbols)}
    except Exception as e:
        logger.error(f"Error fetching symbols: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch symbols")

@router.get("/price/{symbol}")
async def get_symbol_price(symbol: str):
    """Get real-time price for a specific symbol"""
    try:
        price_data = await market_data_service.get_real_time_price(symbol.upper())
        if not price_data:
            raise HTTPException(status_code=404, detail=f"No price data available for {symbol}")
        return price_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch price data")

@router.get("/prices")
async def get_multiple_prices(symbols: str):
    """Get real-time prices for multiple symbols (comma-separated)"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        if len(symbol_list) > 10:  # Limit to 10 symbols per request
            raise HTTPException(status_code=400, detail="Maximum 10 symbols allowed per request")
        
        prices = await market_data_service.get_multiple_prices(symbol_list)
        return {"prices": prices, "requested": symbol_list, "received": list(prices.keys())}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching multiple prices: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch price data")

@router.get("/profile/{symbol}")
async def get_company_profile(symbol: str):
    """Get company profile information for a symbol"""
    try:
        profile = await market_data_service.get_company_profile(symbol.upper())
        if not profile:
            raise HTTPException(status_code=404, detail=f"No profile data available for {symbol}")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching profile for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch company profile")

@router.websocket("/ws/market-data")
async def websocket_market_data(websocket: WebSocket):
    """WebSocket endpoint for real-time market data"""
    await websocket_manager.connect(websocket)
    
    try:
        while True:
            # Wait for messages from client
            message = await websocket.receive_text()
            await websocket_manager.handle_message(websocket, message)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        websocket_manager.disconnect(websocket)

@router.get("/status")
async def get_service_status():
    """Get service status and connection info"""
    return {
        "status": "healthy",
        "websocket_connections": websocket_manager.get_connection_count(),
        "active_subscriptions": {
            symbol: websocket_manager.get_subscription_count(symbol)
            for symbol in websocket_manager.symbol_subscriptions.keys()
        },
        "finnhub_api_key": "configured" if market_data_service.client.api_key else "missing"
    }
