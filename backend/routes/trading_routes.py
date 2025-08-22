from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
import json
import logging
from sqlalchemy.orm import Session

from models.database import get_db, Order, Trade, Position, TradingAccount, User
from services.trading_engine import TradingEngineService
from models.schemas import (
    OrderCreate, OrderResponse, OrderUpdate, 
    TradeResponse, PositionResponse, AccountResponse,
    OrderBookResponse, MarketDataResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: dict = {}  # user_id -> WebSocket

    async def connect(self, websocket: WebSocket, user_id: Optional[int] = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_connections[user_id] = websocket
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: Optional[int] = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")

manager = ConnectionManager()

# Initialize trading engine service
trading_service = TradingEngineService()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@router.get("/symbols")
async def get_symbols():
    """Get available trading symbols"""
    symbols = [
        {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ"},
        {"symbol": "NFLX", "name": "Netflix Inc.", "exchange": "NASDAQ"},
        {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ"},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ"},
        {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE"},
        {"symbol": "JNJ", "name": "Johnson & Johnson", "exchange": "NYSE"}
    ]
    return {"symbols": symbols}

@router.post("/orders", response_model=OrderResponse)
async def place_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """Place a new order"""
    try:
        # For now, we'll use a mock user_id (in production, get from JWT token)
        user_id = 1
        
        # Create order in database
        order = Order(
            order_id=order_data.order_id,
            user_id=user_id,
            account_id=1,  # Mock account_id
            symbol=order_data.symbol,
            order_type=order_data.order_type.value,
            side=order_data.side.value,
            quantity=order_data.quantity,
            price=order_data.price,
            stop_price=order_data.stop_price
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # Place order in trading engine
        engine_order = await trading_service.place_order(order_data)
        
        # Broadcast order update to all connected clients
        await manager.broadcast(json.dumps({
            "type": "order_placed",
            "data": {
                "order_id": order.order_id,
                "symbol": order.symbol,
                "side": order.side,
                "quantity": order.quantity,
                "price": order.price,
                "status": order.status
            }
        }))
        
        return OrderResponse.from_orm(order)
        
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get orders with optional filtering"""
    query = db.query(Order)
    
    if symbol:
        query = query.filter(Order.symbol == symbol)
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.limit(limit).all()
    return [OrderResponse.from_orm(order) for order in orders]

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: Session = Depends(get_db)):
    """Get a specific order by ID"""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderResponse.from_orm(order)

@router.put("/orders/{order_id}", response_model=OrderResponse)
async def modify_order(
    order_id: str,
    order_update: OrderUpdate,
    db: Session = Depends(get_db)
):
    """Modify an existing order"""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status not in ["PENDING", "PARTIALLY_FILLED"]:
        raise HTTPException(status_code=400, detail="Order cannot be modified")
    
    # Update order fields
    if order_update.price is not None:
        order.price = order_update.price
    if order_update.quantity is not None:
        order.quantity = order_update.quantity
    if order_update.stop_price is not None:
        order.stop_price = order_update.stop_price
    
    order.updated_at = datetime.now()
    db.commit()
    db.refresh(order)
    
    # Broadcast order update
    await manager.broadcast(json.dumps({
        "type": "order_modified",
        "data": {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "price": order.price,
            "quantity": order.quantity,
            "status": order.status
        }
    }))
    
    return OrderResponse.from_orm(order)

@router.delete("/orders/{order_id}")
async def cancel_order(order_id: str, db: Session = Depends(get_db)):
    """Cancel an order"""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status not in ["PENDING", "PARTIALLY_FILLED"]:
        raise HTTPException(status_code=400, detail="Order cannot be cancelled")
    
    # Cancel order in trading engine
    success = await trading_service.cancel_order(order_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to cancel order")
    
    # Update order status
    order.status = "CANCELLED"
    order.updated_at = datetime.now()
    db.commit()
    
    # Broadcast order cancellation
    await manager.broadcast(json.dumps({
        "type": "order_cancelled",
        "data": {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "status": order.status
        }
    }))
    
    return {"message": "Order cancelled successfully"}

@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(
    symbol: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get trades with optional filtering"""
    query = db.query(Trade)
    
    if symbol:
        query = query.filter(Trade.symbol == symbol)
    
    trades = query.order_by(Trade.executed_at.desc()).limit(limit).all()
    return [TradeResponse.from_orm(trade) for trade in trades]

@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(db: Session = Depends(get_db)):
    """Get current positions"""
    positions = db.query(Position).all()
    return [PositionResponse.from_orm(position) for position in positions]

@router.get("/orderbook/{symbol}", response_model=OrderBookResponse)
async def get_order_book(symbol: str):
    """Get order book for a specific symbol"""
    try:
        order_book = await trading_service.get_order_book(symbol)
        return order_book
    except Exception as e:
        logger.error(f"Error getting order book: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-data/{symbol}", response_model=MarketDataResponse)
async def get_market_data(symbol: str):
    """Get market data for a specific symbol"""
    # Mock market data (in production, this would come from a market data provider)
    import random
    base_price = 100.0 + random.uniform(-10, 10)
    
    market_data = {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "open_price": base_price,
        "high_price": base_price + random.uniform(0, 5),
        "low_price": base_price - random.uniform(0, 5),
        "close_price": base_price + random.uniform(-2, 2),
        "volume": random.randint(1000, 10000),
        "change": random.uniform(-5, 5),
        "change_percent": random.uniform(-5, 5)
    }
    
    return MarketDataResponse(**market_data)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe":
                # Handle subscription to specific symbols or updates
                symbol = message.get("symbol")
                if symbol:
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "symbol": symbol,
                        "message": f"Subscribed to {symbol} updates"
                    }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@router.websocket("/ws/{user_id}")
async def user_websocket_endpoint(websocket: WebSocket, user_id: int):
    """User-specific WebSocket endpoint for personalized updates"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle user-specific messages
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"User WebSocket error: {e}")
        manager.disconnect(websocket, user_id)
