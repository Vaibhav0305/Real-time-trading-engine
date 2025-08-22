from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging
from sqlalchemy.orm import Session
import uuid

from models.database import get_db
from services.algo_trading import (
    algo_trading_service, StrategyConfig, StrategyType, 
    StrategyStatus, BacktestResult
)
from models.schemas import OrderCreate

router = APIRouter()
logger = logging.getLogger(__name__)

# WebSocket connection manager for real-time strategy updates
class AlgoTradingConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: dict = {}  # user_id -> WebSocket

    async def connect(self, websocket: WebSocket, user_id: Optional[str] = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_connections[user_id] = websocket
        logger.info(f"Algo trading WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: Optional[str] = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
        logger.info(f"Algo trading WebSocket disconnected. Total connections: {len(self.active_connections)}")

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

algo_manager = AlgoTradingConnectionManager()

@router.get("/health")
async def health_check():
    """Health check for algo trading service"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "active_strategies": len(algo_trading_service.strategies)
    }

@router.get("/strategies")
async def get_strategies():
    """Get all available trading strategies"""
    try:
        strategies = await algo_trading_service.get_all_strategies()
        return {"strategies": strategies}
    except Exception as e:
        logger.error(f"Failed to get strategies: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve strategies")

@router.get("/strategies/{strategy_id}")
async def get_strategy(strategy_id: str):
    """Get specific strategy details"""
    try:
        strategy = await algo_trading_service.get_strategy_status(strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        return strategy
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get strategy {strategy_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve strategy")

@router.post("/strategies")
async def create_strategy(strategy_data: dict):
    """Create a new trading strategy"""
    try:
        # Validate strategy data
        required_fields = ['name', 'strategy_type', 'symbols', 'parameters', 'risk_limits']
        for field in required_fields:
            if field not in strategy_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create strategy config
        config = StrategyConfig(
            strategy_id=str(uuid.uuid4()),
            name=strategy_data['name'],
            strategy_type=StrategyType(strategy_data['strategy_type']),
            symbols=strategy_data['symbols'],
            parameters=strategy_data['parameters'],
            risk_limits=strategy_data['risk_limits'],
            enabled=strategy_data.get('enabled', True)
        )
        
        # Add strategy to service
        success = await algo_trading_service.add_strategy(config)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create strategy")
        
        return {
            "message": "Strategy created successfully",
            "strategy_id": config.strategy_id,
            "strategy": await algo_trading_service.get_strategy_status(config.strategy_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create strategy: {e}")
        raise HTTPException(status_code=500, detail="Failed to create strategy")

@router.put("/strategies/{strategy_id}")
async def update_strategy(strategy_id: str, strategy_data: dict):
    """Update an existing trading strategy"""
    try:
        # Check if strategy exists
        existing_strategy = await algo_trading_service.get_strategy_status(strategy_id)
        if not existing_strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        # Remove old strategy
        await algo_trading_service.remove_strategy(strategy_id)
        
        # Create updated config
        config = StrategyConfig(
            strategy_id=strategy_id,
            name=strategy_data.get('name', existing_strategy['name']),
            strategy_type=StrategyType(strategy_data.get('strategy_type', 'moving_average_crossover')),
            symbols=strategy_data.get('symbols', []),
            parameters=strategy_data.get('parameters', {}),
            risk_limits=strategy_data.get('risk_limits', {}),
            enabled=strategy_data.get('enabled', True)
        )
        
        # Add updated strategy
        success = await algo_trading_service.add_strategy(config)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update strategy")
        
        return {
            "message": "Strategy updated successfully",
            "strategy": await algo_trading_service.get_strategy_status(strategy_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update strategy {strategy_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update strategy")

@router.delete("/strategies/{strategy_id}")
async def delete_strategy(strategy_id: str):
    """Delete a trading strategy"""
    try:
        success = await algo_trading_service.remove_strategy(strategy_id)
        if not success:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        return {"message": "Strategy deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete strategy {strategy_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete strategy")

@router.post("/strategies/{strategy_id}/start")
async def start_strategy(strategy_id: str):
    """Start a trading strategy"""
    try:
        success = await algo_trading_service.start_strategy(strategy_id)
        if not success:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        return {"message": "Strategy started successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start strategy {strategy_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to start strategy")

@router.post("/strategies/{strategy_id}/stop")
async def stop_strategy(strategy_id: str):
    """Stop a trading strategy"""
    try:
        success = await algo_trading_service.stop_strategy(strategy_id)
        if not success:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        return {"message": "Strategy stopped successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop strategy {strategy_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop strategy")

@router.post("/strategies/{strategy_id}/backtest")
async def backtest_strategy(strategy_id: str, backtest_data: dict):
    """Backtest a trading strategy"""
    try:
        # Check if strategy exists
        existing_strategy = await algo_trading_service.get_strategy_status(strategy_id)
        if not existing_strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        # Validate backtest data
        required_fields = ['start_date', 'end_date', 'historical_data']
        for field in required_fields:
            if field not in backtest_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Parse dates
        start_date = datetime.fromisoformat(backtest_data['start_date'])
        end_date = datetime.fromisoformat(backtest_data['end_date'])
        
        # Get strategy config
        config = algo_trading_service.strategy_configs.get(strategy_id)
        if not config:
            raise HTTPException(status_code=404, detail="Strategy configuration not found")
        
        # Run backtest
        result = await algo_trading_service.backtest_strategy(
            config, start_date, end_date, backtest_data['historical_data']
        )
        
        return {
            "strategy_id": strategy_id,
            "backtest_result": {
                "start_date": result.start_date.isoformat(),
                "end_date": result.end_date.isoformat(),
                "total_return": result.total_return,
                "sharpe_ratio": result.sharpe_ratio,
                "max_drawdown": result.max_drawdown,
                "win_rate": result.win_rate,
                "total_trades": result.total_trades,
                "trades": result.trades
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to backtest strategy {strategy_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to run backtest")

@router.get("/strategy-types")
async def get_strategy_types():
    """Get available strategy types"""
    return {
        "strategy_types": [
            {
                "type": strategy_type.value,
                "name": strategy_type.name.replace('_', ' ').title(),
                "description": get_strategy_description(strategy_type)
            }
            for strategy_type in StrategyType
        ]
    }

@router.get("/strategy-templates")
async def get_strategy_templates():
    """Get pre-configured strategy templates"""
    return {
        "templates": [
            {
                "name": "Moving Average Crossover",
                "type": "moving_average_crossover",
                "description": "Trend-following strategy using moving average crossovers",
                "default_parameters": {
                    "short_ma": 10,
                    "long_ma": 20
                },
                "default_risk_limits": {
                    "max_position_risk": 0.02,
                    "max_position_size": 1000,
                    "max_risk_per_trade": 1000
                }
            },
            {
                "name": "Mean Reversion",
                "type": "mean_reversion",
                "description": "Contrarian strategy for range-bound markets",
                "default_parameters": {
                    "lookback": 20,
                    "std_threshold": 2.0
                },
                "default_risk_limits": {
                    "max_position_risk": 0.015,
                    "max_position_size": 800,
                    "max_risk_per_trade": 800
                }
            }
        ]
    }

@router.websocket("/ws/strategy-updates/{user_id}")
async def websocket_strategy_updates(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time strategy updates"""
    await algo_manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get('type') == 'ping':
                await websocket.send_text(json.dumps({'type': 'pong', 'timestamp': datetime.now().isoformat()}))
            elif message.get('type') == 'get_strategies':
                strategies = await algo_trading_service.get_all_strategies()
                await websocket.send_text(json.dumps({
                    'type': 'strategies_update',
                    'strategies': strategies
                }))
                
    except WebSocketDisconnect:
        algo_manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        algo_manager.disconnect(websocket, user_id)

def get_strategy_description(strategy_type: StrategyType) -> str:
    """Get description for strategy type"""
    descriptions = {
        StrategyType.MOVING_AVERAGE_CROSSOVER: "Uses moving average crossovers to identify trend changes and generate buy/sell signals",
        StrategyType.MEAN_REVERSION: "Assumes prices will revert to their historical average after extreme moves",
        StrategyType.MOMENTUM: "Follows trends by buying rising assets and selling falling ones",
        StrategyType.ARBITRAGE: "Exploits price differences between markets or instruments",
        StrategyType.GRID_TRADING: "Places buy and sell orders at regular price intervals",
        StrategyType.CUSTOM: "User-defined custom trading strategy"
    }
    return descriptions.get(strategy_type, "Custom trading strategy")
