import logging
import json
import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
import random
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pandas as pd
from textblob import TextBlob

logger = logging.getLogger(__name__)

class MessageType(Enum):
    USER = "user"
    BOT = "bot"
    SYSTEM = "system"

class IntentType(Enum):
    MARKET_ANALYSIS = "market_analysis"
    STRATEGY_RECOMMENDATION = "strategy_recommendation"
    PORTFOLIO_ADVICE = "portfolio_advice"
    RISK_MANAGEMENT = "risk_management"
    TECHNICAL_ANALYSIS = "technical_analysis"
    GENERAL_QUESTION = "general_question"
    GREETING = "greeting"
    PRICE_PREDICTION = "price_prediction"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    PATTERN_RECOGNITION = "pattern_recognition"

@dataclass
class ChatMessage:
    message_id: str
    user_id: str
    message_type: MessageType
    content: str
    timestamp: datetime
    intent: Optional[IntentType] = None
    confidence: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ChatResponse:
    content: str
    intent: IntentType
    confidence: float
    suggested_actions: List[str]
    data: Optional[Dict] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class PricePrediction:
    symbol: str
    predicted_price: float
    confidence: float
    timeframe: str
    factors: List[str]

@dataclass
class SentimentResult:
    symbol: str
    sentiment_score: float
    sentiment_label: str
    sources: List[str]
    confidence: float

@dataclass
class PatternResult:
    symbol: str
    pattern_type: str
    confidence: float
    description: str
    trading_signal: str

class TradingAIChatbot:
    """AI-powered trading assistant chatbot"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conversation_history: Dict[str, List[ChatMessage]] = {}
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        self.ml_models: Dict[str, any] = {}
        self.scaler = StandardScaler()
        self._initialize_ml_models()
        
        # Knowledge base for trading strategies and market analysis
        self.strategy_knowledge = {
            "moving_average_crossover": {
                "description": "A trend-following strategy that generates buy/sell signals based on the crossover of short and long-term moving averages.",
                "best_for": "Trending markets with clear directional movement",
                "risks": "Whipsaws in sideways markets, lag in trend changes",
                "parameters": ["short_ma", "long_ma"],
                "example": "Short MA (10) crosses above Long MA (20) = BUY signal"
            },
            "mean_reversion": {
                "description": "A contrarian strategy that assumes prices will revert to their historical average after extreme moves.",
                "best_for": "Range-bound markets, oversold/overbought conditions",
                "risks": "Trending markets can cause significant losses",
                "parameters": ["lookback_period", "std_threshold"],
                "example": "Price 2 standard deviations below mean = BUY signal"
            },
            "momentum": {
                "description": "A strategy that follows the trend by buying assets that are rising and selling those that are falling.",
                "best_for": "Strong trending markets, growth stocks",
                "risks": "Reversals can cause rapid losses, high volatility",
                "parameters": ["momentum_period", "threshold"],
                "example": "Price up 5% in last 20 days = BUY signal"
            }
        }
        
        # Market analysis templates
        self.market_analysis_templates = {
            "bullish": [
                "The market appears bullish with strong upward momentum. Key support levels are holding, and volume is increasing.",
                "Positive technical indicators suggest continued upward movement. Consider maintaining long positions or scaling in.",
                "Market sentiment is optimistic with institutional buying pressure evident."
            ],
            "bearish": [
                "The market shows bearish characteristics with declining prices and increasing volume on down days.",
                "Key resistance levels are preventing upward movement. Consider reducing exposure or hedging positions.",
                "Technical indicators suggest downward momentum may continue."
            ],
            "neutral": [
                "The market is currently in a consolidation phase with no clear directional bias.",
                "Prices are trading within a defined range. Consider range-bound strategies or wait for breakout confirmation.",
                "Low volatility suggests accumulation phase before next major move."
            ]
        }
        
        # Risk management advice
        self.risk_advice = {
            "position_sizing": "Never risk more than 1-2% of your portfolio on any single trade.",
            "stop_losses": "Always use stop-losses to limit potential losses. Set them at logical support/resistance levels.",
            "diversification": "Diversify across different asset classes, sectors, and strategies to reduce overall risk.",
            "leverage": "Use leverage cautiously. High leverage can amplify both gains and losses.",
            "correlation": "Be aware of correlation between positions. High correlation increases portfolio risk."
        }
    
    def _initialize_ml_models(self):
        """Initialize machine learning models for various predictions"""
        # Price prediction model
        self.ml_models['price_prediction'] = RandomForestRegressor(
            n_estimators=100, 
            random_state=42
        )
        
        # Initialize scaler
        self.scaler = StandardScaler()
    
    async def process_message(self, user_id: str, message: str) -> ChatResponse:
        """Process user message and generate intelligent response"""
        # Add message to history
        self._add_message_to_history(user_id, message, MessageType.USER)
        
        # Classify intent
        intent, confidence = self._classify_intent(message)
        
        # Generate response based on intent
        response = self._generate_response(message, intent, confidence, user_id)
        
        # Add bot response to history
        self._add_message_to_history(user_id, response.content, MessageType.BOT, intent, confidence)
        
        return response
    
    def _classify_intent(self, message: str) -> Tuple[IntentType, float]:
        """Classify user intent using NLP and ML"""
        message_lower = message.lower()
        
        # Enhanced intent classification with ML capabilities
        if any(word in message_lower for word in ['predict', 'forecast', 'price', 'target']):
            return IntentType.PRICE_PREDICTION, 0.9
        elif any(word in message_lower for word in ['sentiment', 'news', 'social', 'mood']):
            return IntentType.SENTIMENT_ANALYSIS, 0.85
        elif any(word in message_lower for word in ['pattern', 'chart', 'formation', 'technical']):
            return IntentType.PATTERN_RECOGNITION, 0.8
        elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'start']):
            return IntentType.GREETING, 0.95
        elif any(word in message_lower for word in ['market', 'analysis', 'trend']):
            return IntentType.MARKET_ANALYSIS, 0.9
        elif any(word in message_lower for word in ['strategy', 'recommend', 'approach']):
            return IntentType.STRATEGY_RECOMMENDATION, 0.85
        elif any(word in message_lower for word in ['portfolio', 'holdings', 'positions']):
            return IntentType.PORTFOLIO_ADVICE, 0.8
        elif any(word in message_lower for word in ['risk', 'stop', 'loss', 'protection']):
            return IntentType.RISK_MANAGEMENT, 0.9
        elif any(word in message_lower for word in ['technical', 'indicator', 'chart']):
            return IntentType.TECHNICAL_ANALYSIS, 0.85
        else:
            return IntentType.GENERAL_QUESTION, 0.6
    
    def _generate_response(self, message: str, intent: IntentType, confidence: float, user_id: str) -> ChatResponse:
        """Generate intelligent response based on intent and ML analysis"""
        if intent == IntentType.PRICE_PREDICTION:
            return self._handle_price_prediction(message, confidence)
        elif intent == IntentType.SENTIMENT_ANALYSIS:
            return self._handle_sentiment_analysis(message, confidence)
        elif intent == IntentType.PATTERN_RECOGNITION:
            return self._handle_pattern_recognition(message, confidence)
        elif intent == IntentType.GREETING:
            return self._handle_greeting(message, confidence)
        elif intent == IntentType.MARKET_ANALYSIS:
            return self._handle_market_analysis(message, confidence)
        elif intent == IntentType.STRATEGY_RECOMMENDATION:
            return self._handle_strategy_recommendation(message, confidence)
        elif intent == IntentType.PORTFOLIO_ADVICE:
            return self._handle_portfolio_advice(message, confidence)
        elif intent == IntentType.RISK_MANAGEMENT:
            return self._handle_risk_management(message, confidence)
        elif intent == IntentType.TECHNICAL_ANALYSIS:
            return self._handle_technical_analysis(message, confidence)
        else:
            return self._handle_general_question(message, confidence)
    
    def _handle_greeting(self, message: str, confidence: float) -> ChatResponse:
        """Handle greeting messages"""
        greetings = [
            f"Hello! I'm your AI trading assistant. How can I help you today?",
            f"Welcome back! I'm here to help with your trading decisions and market analysis.",
            f"Hi there! Ready to discuss trading strategies and market insights?"
        ]
        
        return ChatResponse(
            content=random.choice(greetings),
            intent=IntentType.GREETING,
            confidence=confidence,
            suggested_actions=[
                "Ask about current market conditions",
                "Get strategy recommendations",
                "Learn about risk management",
                "Discuss portfolio optimization"
            ]
        )
    
    def _handle_market_analysis(self, message: str, confidence: float) -> ChatResponse:
        """Handle market analysis requests"""
        # Extract symbols if mentioned
        symbols = self._extract_symbols(message)
        
        if symbols:
            analysis = f"Based on current market conditions, here's my analysis for {', '.join(symbols)}:\n\n"
            analysis += "📈 **Technical Outlook**: The stocks show mixed signals with some exhibiting bullish momentum while others consolidate.\n\n"
            analysis += "📊 **Key Levels**: Watch for support at recent lows and resistance at recent highs.\n\n"
            analysis += "🔍 **Recommendation**: Consider a balanced approach - maintain core positions while being selective with new entries."
        else:
            analysis = "Here's my current market analysis:\n\n"
            analysis += "📈 **Overall Trend**: The market is currently in a consolidation phase with mixed sector performance.\n\n"
            analysis += "📊 **Volume Analysis**: Trading volume is moderate, suggesting institutional participation.\n\n"
            analysis += "🔍 **Outlook**: Expect continued range-bound trading with potential breakout opportunities."
        
        return ChatResponse(
            content=analysis,
            intent=IntentType.MARKET_ANALYSIS,
            confidence=confidence,
            suggested_actions=[
                "Get specific stock analysis",
                "Learn about technical indicators",
                "Discuss market timing strategies"
            ],
            metadata={"symbols": symbols}
        )
    
    def _handle_strategy_recommendation(self, message: str, confidence: float) -> ChatResponse:
        """Handle strategy recommendation requests"""
        # Extract strategy type if mentioned
        strategy_type = self._extract_strategy_type(message)
        
        if strategy_type and strategy_type in self.strategy_knowledge:
            strategy_info = self.strategy_knowledge[strategy_type]
            response = f"Here's my recommendation for the **{strategy_type.replace('_', ' ').title()}** strategy:\n\n"
            response += f"📋 **Description**: {strategy_info['description']}\n\n"
            response += f"✅ **Best For**: {strategy_info['best_for']}\n\n"
            response += f"⚠️ **Risks**: {strategy_info['risks']}\n\n"
            response += f"⚙️ **Key Parameters**: {', '.join(strategy_info['parameters'])}\n\n"
            response += f"💡 **Example**: {strategy_info['example']}"
        else:
            response = "Based on current market conditions, here are my strategy recommendations:\n\n"
            response += "📈 **Trend Following**: Consider moving average crossover strategies for trending markets\n\n"
            response += "🔄 **Mean Reversion**: Look for oversold/overbought opportunities in range-bound stocks\n\n"
            response += "⚡ **Momentum**: Focus on stocks with strong relative strength and volume confirmation"
        
        return ChatResponse(
            content=response,
            intent=IntentType.STRATEGY_RECOMMENDATION,
            confidence=confidence,
            suggested_actions=[
                "Learn more about specific strategies",
                "Get backtesting results",
                "Discuss strategy parameters",
                "Compare different approaches"
            ],
            metadata={"strategy_type": strategy_type}
        )
    
    def _handle_portfolio_advice(self, message: str, confidence: float) -> ChatResponse:
        """Handle portfolio advice requests"""
        response = "Here's my portfolio advice based on best practices:\n\n"
        response += "🎯 **Asset Allocation**: Maintain a balanced mix of stocks, bonds, and alternative investments\n\n"
        response += "📊 **Sector Diversification**: Spread exposure across different sectors to reduce concentration risk\n\n"
        response += "🌍 **Geographic Diversification**: Consider international exposure for global growth opportunities\n\n"
        response += "💰 **Rebalancing**: Review and rebalance your portfolio quarterly to maintain target allocations\n\n"
        response += "📈 **Performance Review**: Regularly assess performance and adjust strategy based on changing market conditions"
        
        return ChatResponse(
            content=response,
            intent=IntentType.PORTFOLIO_ADVICE,
            confidence=confidence,
            suggested_actions=[
                "Get portfolio analysis tools",
                "Learn about rebalancing strategies",
                "Discuss risk-adjusted returns",
                "Explore new investment opportunities"
            ]
        )
    
    def _handle_risk_management(self, message: str, confidence: float) -> ChatResponse:
        """Handle risk management advice"""
        response = "Here are my key risk management principles:\n\n"
        response += "🛡️ **Position Sizing**: {}\n\n".format(self.risk_advice['position_sizing'])
        response += "🛑 **Stop Losses**: {}\n\n".format(self.risk_advice['stop_losses'])
        response += "🌐 **Diversification**: {}\n\n".format(self.risk_advice['diversification'])
        response += "⚖️ **Leverage**: {}\n\n".format(self.risk_advice['leverage'])
        response += "🔗 **Correlation**: {}\n\n".format(self.risk_advice['correlation'])
        response += "📊 **Risk Metrics**: Monitor metrics like VaR, Sharpe ratio, and maximum drawdown"
        
        return ChatResponse(
            content=response,
            intent=IntentType.RISK_MANAGEMENT,
            confidence=confidence,
            suggested_actions=[
                "Calculate position sizes",
                "Set up stop-loss orders",
                "Analyze portfolio risk",
                "Learn about hedging strategies"
            ]
        )
    
    def _handle_technical_analysis(self, message: str, confidence: float) -> ChatResponse:
        """Handle technical analysis requests"""
        response = "Here's my technical analysis guidance:\n\n"
        response += "📊 **Key Indicators**: Focus on RSI, MACD, and moving averages for trend identification\n\n"
        response += "📈 **Support/Resistance**: Identify key levels where price action tends to reverse\n\n"
        response += "🔍 **Chart Patterns**: Look for classic patterns like head & shoulders, triangles, and flags\n\n"
        response += "📉 **Volume Analysis**: Confirm price movements with volume confirmation\n\n"
        response += "⏰ **Timeframes**: Use multiple timeframes for comprehensive analysis"
        
        return ChatResponse(
            content=response,
            intent=IntentType.TECHNICAL_ANALYSIS,
            confidence=confidence,
            suggested_actions=[
                "Get specific indicator analysis",
                "Learn chart pattern recognition",
                "Discuss timeframe analysis",
                "Explore advanced technical tools"
            ]
        )
    
    def _handle_general_question(self, message: str, confidence: float) -> ChatResponse:
        """Handle general questions"""
        response = "I'm here to help with your trading questions! Here are some topics I can assist with:\n\n"
        response += "📈 **Market Analysis**: Current conditions, trends, and outlook\n\n"
        response += "🎯 **Trading Strategies**: Strategy selection, optimization, and backtesting\n\n"
        response += "💼 **Portfolio Management**: Allocation, diversification, and rebalancing\n\n"
        response += "🛡️ **Risk Management**: Position sizing, stop losses, and risk metrics\n\n"
        response += "📊 **Technical Analysis**: Indicators, patterns, and chart analysis"
        
        return ChatResponse(
            content=response,
            intent=IntentType.GENERAL_QUESTION,
            confidence=confidence,
            suggested_actions=[
                "Ask about market conditions",
                "Get strategy recommendations",
                "Learn about risk management",
                "Discuss technical analysis"
            ]
        )
    
    def _handle_price_prediction(self, message: str, confidence: float) -> ChatResponse:
        """Handle price prediction requests using ML models"""
        symbols = self._extract_symbols(message)
        if not symbols:
            return ChatResponse(
                content="I can help predict prices! Please specify a stock symbol (e.g., 'Predict price for AAPL').",
                intent=IntentType.PRICE_PREDICTION,
                confidence=confidence,
                suggested_actions=["Predict AAPL", "Predict TSLA", "Predict MSFT"]
            )
        
        symbol = symbols[0].upper()
        prediction = self._predict_price(symbol)
        
        return ChatResponse(
            content=f"Based on my analysis, {symbol} is predicted to reach ${prediction.predicted_price:.2f} in the next {prediction.timeframe} with {prediction.confidence:.1%} confidence. Key factors: {', '.join(prediction.factors)}",
            intent=IntentType.PRICE_PREDICTION,
            confidence=confidence,
            suggested_actions=[f"Analyze {symbol} sentiment", f"Check {symbol} patterns", "Get risk assessment"],
            data={"prediction": asdict(prediction)}
        )
    
    def _handle_sentiment_analysis(self, message: str, confidence: float) -> ChatResponse:
        """Handle sentiment analysis requests"""
        symbols = self._extract_symbols(message)
        if not symbols:
            return ChatResponse(
                content="I can analyze market sentiment! Please specify a stock symbol (e.g., 'Analyze sentiment for AAPL').",
                intent=IntentType.SENTIMENT_ANALYSIS,
                confidence=confidence,
                suggested_actions=["Analyze AAPL sentiment", "Analyze TSLA sentiment", "Market mood check"]
            )
        
        symbol = symbols[0].upper()
        sentiment = self._analyze_sentiment(symbol)
        
        return ChatResponse(
            content=f"Sentiment analysis for {symbol}: {sentiment.sentiment_label} ({sentiment.sentiment_score:.2f}/10). Sources: {', '.join(sentiment.sources)}. Confidence: {sentiment.confidence:.1%}",
            intent=IntentType.SENTIMENT_ANALYSIS,
            confidence=confidence,
            suggested_actions=[f"Predict {symbol} price", f"Check {symbol} patterns", "Get trading strategy"],
            data={"sentiment": asdict(sentiment)}
        )
    
    def _handle_pattern_recognition(self, message: str, confidence: float) -> ChatResponse:
        """Handle pattern recognition requests"""
        symbols = self._extract_symbols(message)
        if not symbols:
            return ChatResponse(
                content="I can identify chart patterns! Please specify a stock symbol (e.g., 'Find patterns in AAPL').",
                intent=IntentType.PATTERN_RECOGNITION,
                confidence=confidence,
                suggested_actions=["Find AAPL patterns", "Find TSLA patterns", "Pattern overview"]
            )
        
        symbol = symbols[0].upper()
        pattern = self._identify_patterns(symbol)
        
        return ChatResponse(
            content=f"Pattern detected in {symbol}: {pattern.pattern_type} with {pattern.confidence:.1%} confidence. {pattern.description} Trading signal: {pattern.trading_signal}",
            intent=IntentType.PATTERN_RECOGNITION,
            confidence=confidence,
            suggested_actions=[f"Predict {symbol} price", f"Analyze {symbol} sentiment", "Get risk management"],
            data={"pattern": asdict(pattern)}
        )
    
    def _predict_price(self, symbol: str) -> PricePrediction:
        """Predict price using ML model (simulated for demo)"""
        # In real implementation, this would use historical data and trained model
        base_price = 100.0
        volatility = 0.15
        trend = 0.02
        
        # Simulate prediction with some randomness
        predicted_change = np.random.normal(trend, volatility)
        predicted_price = base_price * (1 + predicted_change)
        
        factors = ["Technical indicators", "Volume analysis", "Market trends", "Historical patterns"]
        
        return PricePrediction(
            symbol=symbol,
            predicted_price=max(predicted_price, 0),
            confidence=np.random.uniform(0.6, 0.9),
            timeframe="1 week",
            factors=factors
        )
    
    def _analyze_sentiment(self, symbol: str) -> SentimentResult:
        """Analyze sentiment using NLP (simulated for demo)"""
        # In real implementation, this would analyze news, social media, etc.
        sentiment_score = np.random.uniform(3, 8)
        
        if sentiment_score > 6:
            label = "Bullish"
        elif sentiment_score < 4:
            label = "Bearish"
        else:
            label = "Neutral"
        
        sources = ["News articles", "Social media", "Analyst reports", "Market commentary"]
        
        return SentimentResult(
            symbol=symbol,
            sentiment_score=sentiment_score,
            sentiment_label=label,
            sources=sources,
            confidence=np.random.uniform(0.7, 0.95)
        )
    
    def _identify_patterns(self, symbol: str) -> PatternResult:
        """Identify chart patterns (simulated for demo)"""
        patterns = [
            ("Head and Shoulders", "Bearish reversal pattern forming", "SELL"),
            ("Double Bottom", "Bullish reversal pattern", "BUY"),
            ("Ascending Triangle", "Bullish continuation pattern", "BUY"),
            ("Descending Triangle", "Bearish continuation pattern", "SELL"),
            ("Cup and Handle", "Bullish continuation pattern", "BUY")
        ]
        
        pattern = np.random.choice(patterns)
        
        return PatternResult(
            symbol=symbol,
            pattern_type=pattern[0],
            confidence=np.random.uniform(0.7, 0.95),
            description=pattern[1],
            trading_signal=pattern[2]
        )
    
    def _extract_symbols(self, message: str) -> List[str]:
        """Extract stock symbols from message"""
        # Simple pattern matching for common stock symbols
        symbol_pattern = r'\b[A-Z]{1,5}\b'
        symbols = re.findall(symbol_pattern, message)
        
        # Filter out common words that aren't stock symbols
        common_words = {'THE', 'AND', 'FOR', 'ARE', 'YOU', 'CAN', 'GET', 'SEE', 'NOW', 'HOW', 'WHAT', 'WHEN', 'WHERE'}
        symbols = [s for s in symbols if s not in common_words and len(s) >= 1]
        
        return symbols[:5]  # Limit to 5 symbols
    
    def _extract_strategy_type(self, message: str) -> Optional[str]:
        """Extract strategy type from message"""
        message_lower = message.lower()
        
        for strategy in self.strategy_knowledge.keys():
            if strategy.replace('_', ' ') in message_lower or strategy in message_lower:
                return strategy
        
        return None
    
    def _add_message_to_history(self, user_id: str, message: str, message_type: MessageType):
        """Add message to conversation history"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Keep only last 50 messages to prevent memory issues
        if len(self.conversation_history[user_id]) >= 50:
            self.conversation_history[user_id] = self.conversation_history[user_id][-49:]
        
        self.conversation_history[user_id].append(ChatMessage(
            message_id=f"msg_{datetime.now().timestamp()}",
            user_id=user_id,
            message_type=message_type,
            content=message,
            timestamp=datetime.now(),
            intent=None, # Intent will be set after classification
            confidence=0.0, # Confidence will be set after classification
            metadata={}
        ))
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[ChatMessage]:
        """Get recent conversation history for a user"""
        if user_id in self.conversation_history:
            return self.conversation_history[user_id][-limit:]
        return []
    
    def clear_conversation_history(self, user_id: str):
        """Clear conversation history for a user"""
        if user_id in self.conversation_history:
            self.conversation_history[user_id] = []
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Update user preferences for personalized responses"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        
        self.user_preferences[user_id].update(preferences)
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences"""
        return self.user_preferences.get(user_id, {})

# Global instance
ai_chatbot = TradingAIChatbot()
