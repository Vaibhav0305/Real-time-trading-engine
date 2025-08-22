import asyncio
import json
import logging
from typing import Dict, Set, List
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.symbol_subscriptions: Dict[str, Set[WebSocket]] = {}
        self.price_stream_task = None
        
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "connection",
            "message": "Connected to VittCott Real-time Market Data",
            "timestamp": datetime.now().isoformat()
        }))
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.discard(websocket)
        
        # Remove from symbol subscriptions
        for symbol, connections in self.symbol_subscriptions.items():
            connections.discard(websocket)
            
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def subscribe_to_symbol(self, websocket: WebSocket, symbol: str):
        """Subscribe to real-time updates for a specific symbol"""
        if symbol not in self.symbol_subscriptions:
            self.symbol_subscriptions[symbol] = set()
        
        self.symbol_subscriptions[symbol].add(websocket)
        
        await websocket.send_text(json.dumps({
            "type": "subscription",
            "symbol": symbol,
            "message": f"Subscribed to {symbol} updates",
            "timestamp": datetime.now().isoformat()
        }))
        
        logger.info(f"Client subscribed to {symbol}. Total subscribers: {len(self.symbol_subscriptions[symbol])}")
    
    async def unsubscribe_from_symbol(self, websocket: WebSocket, symbol: str):
        """Unsubscribe from symbol updates"""
        if symbol in self.symbol_subscriptions:
            self.symbol_subscriptions[symbol].discard(websocket)
            
            # Clean up empty subscriptions
            if not self.symbol_subscriptions[symbol]:
                del self.symbol_subscriptions[symbol]
        
        await websocket.send_text(json.dumps({
            "type": "unsubscription",
            "symbol": symbol,
            "message": f"Unsubscribed from {symbol} updates",
            "timestamp": datetime.now().isoformat()
        }))
        
        logger.info(f"Client unsubscribed from {symbol}")
    
    async def broadcast_price_update(self, symbol: str, price_data: Dict):
        """Broadcast price update to all subscribers of a symbol"""
        if symbol not in self.symbol_subscriptions:
            return
        
        message = {
            "type": "price_update",
            "symbol": symbol,
            "data": price_data,
            "timestamp": datetime.now().isoformat()
        }
        
        message_json = json.dumps(message)
        disconnected = set()
        
        for websocket in self.symbol_subscriptions[symbol]:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {str(e)}")
                disconnected.add(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast_market_update(self, market_data: Dict):
        """Broadcast general market update to all connected clients"""
        message = {
            "type": "market_update",
            "data": market_data,
            "timestamp": datetime.now().isoformat()
        }
        
        message_json = json.dumps(message)
        disconnected = set()
        
        for websocket in self.active_connections:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending market update: {str(e)}")
                disconnected.add(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def handle_message(self, websocket: WebSocket, message: str):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "subscribe":
                symbol = data.get("symbol")
                if symbol:
                    await self.subscribe_to_symbol(websocket, symbol)
                    
            elif msg_type == "unsubscribe":
                symbol = data.get("symbol")
                if symbol:
                    await self.unsubscribe_from_symbol(websocket, symbol)
                    
            elif msg_type == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
                
        except json.JSONDecodeError:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Invalid JSON message",
                "timestamp": datetime.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Internal error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }))
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)
    
    def get_subscription_count(self, symbol: str) -> int:
        """Get number of subscribers for a symbol"""
        return len(self.symbol_subscriptions.get(symbol, set()))

# Global WebSocket manager instance
websocket_manager = WebSocketManager()
