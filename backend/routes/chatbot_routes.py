from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging
from sqlalchemy.orm import Session
import uuid

from models.database import get_db
from services.ai_chatbot import ai_chatbot, ChatMessage, MessageType, IntentType

router = APIRouter()
logger = logging.getLogger(__name__)

# WebSocket connection manager for real-time chat
class ChatbotConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: dict = {}  # user_id -> WebSocket

    async def connect(self, websocket: WebSocket, user_id: Optional[str] = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_connections[user_id] = websocket
        logger.info(f"Chatbot WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: Optional[str] = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
        logger.info(f"Chatbot WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, user_id: str):
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

chatbot_manager = ChatbotConnectionManager()

@router.get("/health")
async def health_check():
    """Health check for chatbot service"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(chatbot_manager.active_connections)
    }

@router.post("/chat")
async def send_message(chat_data: dict):
    """Send a message to the AI chatbot"""
    try:
        # Validate chat data
        required_fields = ['user_id', 'message']
        for field in required_fields:
            if field not in chat_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        user_id = chat_data['user_id']
        message = chat_data['message']
        
        # Process message through chatbot
        response = await ai_chatbot.process_message(user_id, message)
        
        return {
            "message_id": f"msg_{datetime.now().timestamp()}",
            "user_id": user_id,
            "response": {
                "content": response.content,
                "intent": response.intent.value,
                "confidence": response.confidence,
                "suggested_actions": response.suggested_actions,
                "metadata": response.metadata
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to process chat message: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message")

@router.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 20):
    """Get chat history for a user"""
    try:
        history = ai_chatbot.get_conversation_history(user_id, limit)
        
        # Convert to serializable format
        serializable_history = []
        for msg in history:
            serializable_history.append({
                "message_id": msg.message_id,
                "user_id": msg.user_id,
                "message_type": msg.message_type.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "intent": msg.intent.value if msg.intent else None,
                "metadata": msg.metadata
            })
        
        return {
            "user_id": user_id,
            "history": serializable_history,
            "total_messages": len(serializable_history)
        }
        
    except Exception as e:
        logger.error(f"Failed to get chat history for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

@router.delete("/chat/history/{user_id}")
async def clear_chat_history(user_id: str):
    """Clear chat history for a user"""
    try:
        ai_chatbot.clear_conversation_history(user_id)
        return {"message": "Chat history cleared successfully"}
        
    except Exception as e:
        logger.error(f"Failed to clear chat history for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear chat history")

@router.get("/chat/intents")
async def get_available_intents():
    """Get available chat intents and their descriptions"""
    return {
        "intents": [
            {
                "type": intent.value,
                "name": intent.name.replace('_', ' ').title(),
                "description": get_intent_description(intent)
            }
            for intent in IntentType
        ]
    }

@router.get("/chat/help")
async def get_chat_help():
    """Get help information for using the chatbot"""
    return {
        "welcome_message": "Hello! I'm your AI trading assistant. I can help you with:",
        "capabilities": [
            {
                "category": "Market Analysis",
                "examples": [
                    "What's the current market outlook?",
                    "Analyze AAPL stock",
                    "What's the trend for tech stocks?"
                ]
            },
            {
                "category": "Trading Strategies",
                "examples": [
                    "Recommend a strategy for trending markets",
                    "Explain moving average crossover",
                    "What strategy works best for volatility?"
                ]
            },
            {
                "category": "Portfolio Management",
                "examples": [
                    "How should I diversify my portfolio?",
                    "What's the optimal asset allocation?",
                    "When should I rebalance?"
                ]
            },
            {
                "category": "Risk Management",
                "examples": [
                    "How much should I risk per trade?",
                    "Where should I set stop losses?",
                    "How to manage portfolio risk?"
                ]
            },
            {
                "category": "Technical Analysis",
                "examples": [
                    "What indicators should I use?",
                    "How to identify support/resistance?",
                    "Explain chart patterns"
                ]
            }
        ],
        "tips": [
            "Be specific with your questions for better answers",
            "Mention stock symbols (e.g., AAPL, GOOGL) for specific analysis",
            "Ask follow-up questions to dive deeper into topics",
            "Use the suggested actions to explore related topics"
        ]
    }

@router.post("/chat/preferences/{user_id}")
async def update_user_preferences(user_id: str, preferences: dict):
    """Update user preferences for personalized responses"""
    try:
        ai_chatbot.update_user_preferences(user_id, preferences)
        return {
            "message": "Preferences updated successfully",
            "user_id": user_id,
            "preferences": ai_chatbot.get_user_preferences(user_id)
        }
        
    except Exception as e:
        logger.error(f"Failed to update preferences for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")

@router.get("/chat/preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """Get user preferences"""
    try:
        preferences = ai_chatbot.get_user_preferences(user_id)
        return {
            "user_id": user_id,
            "preferences": preferences
        }
        
    except Exception as e:
        logger.error(f"Failed to get preferences for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve preferences")

@router.get("/chat/strategies")
async def get_strategy_knowledge():
    """Get available strategy knowledge for the chatbot"""
    try:
        return {
            "strategies": ai_chatbot.strategy_knowledge,
            "market_analysis_templates": {
                "types": list(ai_chatbot.market_analysis_templates.keys()),
                "descriptions": {
                    "bullish": "Optimistic market outlook with upward momentum",
                    "bearish": "Pessimistic market outlook with downward pressure",
                    "neutral": "Sideways market with no clear directional bias"
                }
            },
            "risk_advice": ai_chatbot.risk_advice
        }
        
    except Exception as e:
        logger.error(f"Failed to get strategy knowledge: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve strategy knowledge")

@router.websocket("/ws/chat/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time chat"""
    await chatbot_manager.connect(websocket, user_id)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get('type') == 'chat_message':
                # Process chat message
                response = await ai_chatbot.process_message(
                    user_id, 
                    message_data.get('content', '')
                )
                
                # Send response back to client
                await websocket.send_text(json.dumps({
                    'type': 'chat_response',
                    'message_id': f"msg_{datetime.now().timestamp()}",
                    'user_id': user_id,
                    'response': {
                        'content': response.content,
                        'intent': response.intent.value,
                        'confidence': response.confidence,
                        'suggested_actions': response.suggested_actions,
                        'metadata': response.metadata
                    },
                    'timestamp': datetime.now().isoformat()
                }))
                
            elif message_data.get('type') == 'ping':
                # Keep connection alive
                await websocket.send_text(json.dumps({
                    'type': 'pong', 
                    'timestamp': datetime.now().isoformat()
                }))
                
            elif message_data.get('type') == 'get_history':
                # Send chat history
                history = ai_chatbot.get_conversation_history(user_id, 10)
                serializable_history = []
                for msg in history:
                    serializable_history.append({
                        "message_id": msg.message_id,
                        "user_id": msg.user_id,
                        "message_type": msg.message_type.value,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                        "intent": msg.intent.value if msg.intent else None
                    })
                
                await websocket.send_text(json.dumps({
                    'type': 'chat_history',
                    'history': serializable_history
                }))
                
    except WebSocketDisconnect:
        chatbot_manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        chatbot_manager.disconnect(websocket, user_id)

def get_intent_description(intent: IntentType) -> str:
    """Get description for intent type"""
    descriptions = {
        IntentType.MARKET_ANALYSIS: "Questions about market conditions, trends, and outlook",
        IntentType.STRATEGY_RECOMMENDATION: "Requests for trading strategy advice and recommendations",
        IntentType.PORTFOLIO_ADVICE: "Questions about portfolio management and optimization",
        IntentType.RISK_MANAGEMENT: "Inquiries about risk management principles and practices",
        IntentType.TECHNICAL_ANALYSIS: "Questions about technical indicators and chart analysis",
        IntentType.GENERAL_QUESTION: "General trading and investment questions",
        IntentType.GREETING: "Greeting and introduction messages"
    }
    return descriptions.get(intent, "General trading assistance")
