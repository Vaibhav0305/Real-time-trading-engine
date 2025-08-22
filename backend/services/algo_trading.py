import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import random
import json

logger = logging.getLogger(__name__)

class StrategyType(Enum):
    MOVING_AVERAGE_CROSSOVER = "moving_average_crossover"
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM_BREAKOUT = "momentum_breakout"
    PAIRS_TRADING = "pairs_trading"
    ARBITRAGE = "arbitrage"
    OPTIONS_STRATEGY = "options_strategy"
    VOLATILITY_BREAKOUT = "volatility_breakout"
    MEAN_REVERSION_ENHANCED = "mean_reversion_enhanced"

class StrategyStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    ERROR = "error"

@dataclass
class StrategyConfig:
    strategy_type: StrategyType
    symbols: List[str]
    parameters: Dict[str, Any]
    risk_management: Dict[str, float]
    execution_frequency: str = "1m"
    max_position_size: float = 1000.0
    max_risk_per_trade: float = 0.02
    stop_loss_pct: float = 0.05
    take_profit_pct: float = 0.10

@dataclass
class BacktestResult:
    strategy_name: str
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    start_date: datetime
    end_date: datetime
    trades: List[Dict] = field(default_factory=list)

@dataclass
class TradingSignal:
    symbol: str
    action: str  # "BUY", "SELL", "HOLD"
    confidence: float
    price: float
    timestamp: datetime
    reason: str
    strategy_name: str

class BaseStrategy:
    """Base class for all trading strategies"""
    
    def __init__(self, config: StrategyConfig):
        self.config = config
        self.status = StrategyStatus.INACTIVE
        self.last_execution = None
        self.total_trades = 0
        self.total_pnl = 0.0
        
    async def execute(self, market_data: Dict[str, Any]) -> Optional[TradingSignal]:
        """Execute strategy logic and return trading signal"""
        raise NotImplementedError("Subclasses must implement execute method")
    
    def calculate_risk_adjusted_position_size(self, available_capital: float, current_price: float) -> float:
        """Calculate position size based on risk management rules"""
        max_risk_amount = available_capital * self.config.max_risk_per_trade
        stop_loss_amount = current_price * self.config.stop_loss_pct
        
        if stop_loss_amount > 0:
            position_size = max_risk_amount / stop_loss_amount
            return min(position_size, self.config.max_position_size)
        return 0.0

class MovingAverageCrossoverStrategy(BaseStrategy):
    """Moving average crossover strategy"""
    
    async def execute(self, market_data: Dict[str, Any]) -> Optional[TradingSignal]:
        if not market_data.get('prices'):
            return None
            
        prices = market_data['prices']
        if len(prices) < 50:
            return None
            
        # Calculate moving averages
        short_ma = np.mean(prices[-10:])  # 10-period MA
        long_ma = np.mean(prices[-50:])   # 50-period MA
        
        current_price = prices[-1]
        previous_short_ma = np.mean(prices[-11:-1])
        previous_long_ma = np.mean(prices[-51:-1])
        
        # Check for crossover
        if short_ma > long_ma and previous_short_ma <= previous_long_ma:
            return TradingSignal(
                symbol=self.config.symbols[0],
                action="BUY",
                confidence=0.8,
                price=current_price,
                timestamp=datetime.now(),
                reason="Golden cross detected",
                strategy_name="Moving Average Crossover"
            )
        elif short_ma < long_ma and previous_short_ma >= previous_long_ma:
            return TradingSignal(
                symbol=self.config.symbols[0],
                action="SELL",
                confidence=0.8,
                price=current_price,
                timestamp=datetime.now(),
                reason="Death cross detected",
                strategy_name="Moving Average Crossover"
            )
        
        return None

class MeanReversionStrategy(BaseStrategy):
    """Mean reversion strategy using Bollinger Bands"""
    
    async def execute(self, market_data: Dict[str, Any]) -> Optional[TradingSignal]:
        if not market_data.get('prices'):
            return None
            
        prices = market_data['prices']
        if len(prices) < 20:
            return None
            
        # Calculate Bollinger Bands
        sma = np.mean(prices[-20:])
        std = np.std(prices[-20:])
        
        upper_band = sma + (2 * std)
        lower_band = sma - (2 * std)
        
        current_price = prices[-1]
        
        # Check for mean reversion signals
        if current_price < lower_band:
            return TradingSignal(
                symbol=self.config.symbols[0],
                action="BUY",
                confidence=0.75,
                price=current_price,
                timestamp=datetime.now(),
                reason="Price below lower Bollinger Band",
                strategy_name="Mean Reversion"
            )
        elif current_price > upper_band:
            return TradingSignal(
                symbol=self.config.symbols[0],
                action="SELL",
                confidence=0.75,
                price=current_price,
                timestamp=datetime.now(),
                reason="Price above upper Bollinger Band",
                strategy_name="Mean Reversion"
            )
        
        return None

class MomentumBreakoutStrategy(BaseStrategy):
    """Momentum breakout strategy using volume and price action"""
    
    async def execute(self, market_data: Dict[str, Any]) -> Optional[TradingSignal]:
        if not market_data.get('prices') or not market_data.get('volumes'):
            return None
            
        prices = market_data['prices']
        volumes = market_data['volumes']
        
        if len(prices) < 20:
            return None
            
        current_price = prices[-1]
        current_volume = volumes[-1]
        
        # Calculate momentum indicators
        price_momentum = (current_price - prices[-5]) / prices[-5]
        volume_momentum = current_volume / np.mean(volumes[-20:])
        
        # Check for breakout conditions
        if price_momentum > 0.02 and volume_momentum > 1.5:
            return TradingSignal(
                symbol=self.config.symbols[0],
                action="BUY",
                confidence=0.7,
                price=current_price,
                timestamp=datetime.now(),
                reason="High momentum breakout with volume confirmation",
                strategy_name="Momentum Breakout"
            )
        elif price_momentum < -0.02 and volume_momentum > 1.5:
            return TradingSignal(
                symbol=self.config.symbols[0],
                action="SELL",
                confidence=0.7,
                price=current_price,
                timestamp=datetime.now(),
                reason="Downward momentum breakout with volume confirmation",
                strategy_name="Momentum Breakout"
            )
        
        return None

class PairsTradingStrategy(BaseStrategy):
    """Pairs trading strategy using correlation and mean reversion"""
    
    async def execute(self, market_data: Dict[str, Any]) -> Optional[TradingSignal]:
        if len(self.config.symbols) < 2:
            return None
            
        symbol1, symbol2 = self.config.symbols[0], self.config.symbols[1]
        
        if not market_data.get(symbol1) or not market_data.get(symbol2):
            return None
            
        prices1 = market_data[symbol1].get('prices', [])
        prices2 = market_data[symbol2].get('prices', [])
        
        if len(prices1) < 30 or len(prices2) < 30:
            return None
            
        # Calculate spread
        spread = np.array(prices1[-30:]) - np.array(prices2[-30:])
        spread_mean = np.mean(spread)
        spread_std = np.std(spread)
        
        current_spread = spread[-1]
        z_score = (current_spread - spread_mean) / spread_std
        
        # Trading signals based on z-score
        if z_score > 2.0:  # Spread is too wide
            return TradingSignal(
                symbol=symbol1,
                action="SELL",
                confidence=0.8,
                price=prices1[-1],
                timestamp=datetime.now(),
                reason=f"Pairs trading: Short {symbol1}, Long {symbol2} (z-score: {z_score:.2f})",
                strategy_name="Pairs Trading"
            )
        elif z_score < -2.0:  # Spread is too narrow
            return TradingSignal(
                symbol=symbol1,
                action="BUY",
                confidence=0.8,
                price=prices1[-1],
                timestamp=datetime.now(),
                reason=f"Pairs trading: Long {symbol1}, Short {symbol2} (z-score: {z_score:.2f})",
                strategy_name="Pairs Trading"
            )
        
        return None

class ArbitrageStrategy(BaseStrategy):
    """Arbitrage strategy detecting price differences across exchanges"""
    
    async def execute(self, market_data: Dict[str, Any]) -> Optional[TradingSignal]:
        if not market_data.get('exchange_prices'):
            return None
            
        exchange_prices = market_data['exchange_prices']
        symbol = self.config.symbols[0]
        
        if symbol not in exchange_prices:
            return None
            
        prices = exchange_prices[symbol]
        if len(prices) < 2:
            return None
            
        # Find best bid and ask across exchanges
        best_bid = max(prices.values(), key=lambda x: x.get('bid', 0))
        best_ask = min(prices.values(), key=lambda x: x.get('ask', float('inf')))
        
        if best_bid.get('bid', 0) > best_ask.get('ask', float('inf')):
            # Arbitrage opportunity detected
            profit_pct = (best_bid['bid'] - best_ask['ask']) / best_ask['ask']
            
            if profit_pct > 0.001:  # 0.1% minimum profit
                return TradingSignal(
                    symbol=symbol,
                    action="ARBITRAGE",
                    confidence=0.95,
                    price=best_ask['ask'],
                    timestamp=datetime.now(),
                    reason=f"Arbitrage opportunity: Buy at {best_ask['exchange']} ${best_ask['ask']:.2f}, Sell at {best_bid['exchange']} ${best_bid['bid']:.2f}",
                    strategy_name="Arbitrage"
                )
        
        return None

class OptionsStrategy(BaseStrategy):
    """Options trading strategy using volatility and Greeks"""
    
    async def execute(self, market_data: Dict[str, Any]) -> Optional[TradingSignal]:
        if not market_data.get('options_data'):
            return None
            
        options_data = market_data['options_data']
        symbol = self.config.symbols[0]
        
        if symbol not in options_data:
            return None
            
        option = options_data[symbol]
        
        # Check for volatility skew opportunities
        implied_vol = option.get('implied_volatility', 0)
        historical_vol = option.get('historical_volatility', 0)
        
        if implied_vol > historical_vol * 1.2:  # IV is significantly higher
            return TradingSignal(
                symbol=symbol,
                action="SELL_OPTION",
                confidence=0.7,
                price=option.get('price', 0),
                timestamp=datetime.now(),
                reason=f"High implied volatility ({implied_vol:.2%}) vs historical ({historical_vol:.2%})",
                strategy_name="Options Strategy"
            )
        elif implied_vol < historical_vol * 0.8:  # IV is significantly lower
            return TradingSignal(
                symbol=symbol,
                action="BUY_OPTION",
                confidence=0.7,
                price=option.get('price', 0),
                timestamp=datetime.now(),
                reason=f"Low implied volatility ({implied_vol:.2%}) vs historical ({historical_vol:.2%})",
                strategy_name="Options Strategy"
            )
        
        return None

class VolatilityBreakoutStrategy(BaseStrategy):
    """Volatility breakout strategy using ATR and volume"""
    
    async def execute(self, market_data: Dict[str, Any]) -> Optional[TradingSignal]:
        if not market_data.get('prices') or not market_data.get('volumes'):
            return None
            
        prices = market_data['prices']
        volumes = market_data['volumes']
        
        if len(prices) < 14:
            return None
            
        # Calculate Average True Range (ATR)
        high_low = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        atr = np.mean(high_low[-14:])
        
        current_price = prices[-1]
        current_volume = volumes[-1]
        
        # Check for volatility breakout
        price_change = abs(current_price - prices[-2]) / prices[-2]
        volume_ratio = current_volume / np.mean(volumes[-20:])
        
        if price_change > atr * 2 and volume_ratio > 1.3:
            direction = "BUY" if current_price > prices[-2] else "SELL"
            return TradingSignal(
                symbol=self.config.symbols[0],
                action=direction,
                confidence=0.75,
                price=current_price,
                timestamp=datetime.now(),
                reason=f"Volatility breakout: {price_change:.2%} change with {volume_ratio:.1f}x volume",
                strategy_name="Volatility Breakout"
            )
        
        return None

class MeanReversionEnhancedStrategy(BaseStrategy):
    """Enhanced mean reversion using multiple timeframes and indicators"""
    
    async def execute(self, market_data: Dict[str, Any]) -> Optional[TradingSignal]:
        if not market_data.get('prices'):
            return None
            
        prices = market_data['prices']
        if len(prices) < 50:
            return None
            
        # Multiple timeframe analysis
        short_sma = np.mean(prices[-10:])
        medium_sma = np.mean(prices[-20:])
        long_sma = np.mean(prices[-50:])
        
        current_price = prices[-1]
        
        # RSI calculation
        gains = [max(0, prices[i] - prices[i-1]) for i in range(1, len(prices))]
        losses = [max(0, prices[i-1] - prices[i]) for i in range(1, len(prices))]
        
        avg_gain = np.mean(gains[-14:])
        avg_loss = np.mean(losses[-14:])
        
        if avg_loss != 0:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = 100
        
        # Enhanced mean reversion signals
        if (current_price < short_sma < medium_sma < long_sma and rsi < 30):
            return TradingSignal(
                symbol=self.config.symbols[0],
                action="BUY",
                confidence=0.85,
                price=current_price,
                timestamp=datetime.now(),
                reason="Multi-timeframe oversold condition with RSI confirmation",
                strategy_name="Enhanced Mean Reversion"
            )
        elif (current_price > short_sma > medium_sma > long_sma and rsi > 70):
            return TradingSignal(
                symbol=self.config.symbols[0],
                action="SELL",
                confidence=0.85,
                price=current_price,
                timestamp=datetime.now(),
                reason="Multi-timeframe overbought condition with RSI confirmation",
                strategy_name="Enhanced Mean Reversion"
            )
        
        return None

class AlgoTradingService:
    """Main service for managing algorithmic trading strategies"""
    
    def __init__(self):
        self.strategies: Dict[str, BaseStrategy] = {}
        self.strategy_configs: Dict[str, StrategyConfig] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.running = False
        self.logger = logging.getLogger(__name__)
    
    async def add_strategy(self, config: StrategyConfig) -> bool:
        """Add a new trading strategy"""
        try:
            if config.strategy_type == StrategyType.MOVING_AVERAGE_CROSSOVER:
                strategy = MovingAverageCrossoverStrategy(config)
            elif config.strategy_type == StrategyType.MEAN_REVERSION:
                strategy = MeanReversionStrategy(config)
            else:
                self.logger.error(f"Unsupported strategy type: {config.strategy_type}")
                return False
            
            await strategy.initialize()
            self.strategies[config.strategy_id] = strategy
            self.strategy_configs[config.strategy_id] = config
            self.logger.info(f"Strategy added: {config.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add strategy: {e}")
            return False
    
    async def remove_strategy(self, strategy_id: str) -> bool:
        """Remove a trading strategy"""
        try:
            if strategy_id in self.strategies:
                await self.strategies[strategy_id].stop()
                del self.strategies[strategy_id]
                del self.strategy_configs[strategy_id]
                self.logger.info(f"Strategy removed: {strategy_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to remove strategy: {e}")
            return False
    
    async def start_strategy(self, strategy_id: str) -> bool:
        """Start a specific strategy"""
        try:
            if strategy_id in self.strategies:
                self.strategies[strategy_id].status = StrategyStatus.ACTIVE
                self.logger.info(f"Strategy started: {strategy_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to start strategy: {e}")
            return False
    
    async def stop_strategy(self, strategy_id: str) -> bool:
        """Stop a specific strategy"""
        try:
            if strategy_id in self.strategies:
                await self.strategies[strategy_id].stop()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to stop strategy: {e}")
            return False
    
    async def get_strategy_status(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific strategy"""
        if strategy_id in self.strategies:
            strategy = self.strategies[strategy_id]
            return {
                'strategy_id': strategy_id,
                'name': strategy.config.name,
                'status': strategy.status.value,
                'current_positions': strategy.current_positions,
                'trade_count': len(strategy.trade_history)
            }
        return None
    
    async def get_all_strategies(self) -> List[Dict[str, Any]]:
        """Get status of all strategies"""
        return [
            await self.get_strategy_status(strategy_id)
            for strategy_id in self.strategies.keys()
        ]
    
    async def backtest_strategy(self, config: StrategyConfig, 
                              start_date: datetime, 
                              end_date: datetime,
                              historical_data: Dict[str, List[float]]) -> BacktestResult:
        """Backtest a strategy with historical data"""
        try:
            # Create temporary strategy instance for backtesting
            if config.strategy_type == StrategyType.MOVING_AVERAGE_CROSSOVER:
                strategy = MovingAverageCrossoverStrategy(config)
            elif config.strategy_type == StrategyType.MEAN_REVERSION:
                strategy = MeanReversionStrategy(config)
            else:
                raise ValueError(f"Unsupported strategy type: {config.strategy_type}")
            
            strategy.status = StrategyStatus.BACKTESTING
            
            # Simulate strategy execution
            initial_capital = 100000
            current_capital = initial_capital
            trades = []
            
            for symbol in config.symbols:
                if symbol not in historical_data:
                    continue
                
                prices = historical_data[symbol]
                for i in range(len(prices)):
                    # Simulate market data
                    market_data = {symbol: {'prices': prices[:i+1]}}
                    await strategy.execute(market_data)
                    
                    # Calculate P&L from trades
                    for trade in strategy.trade_history:
                        if trade['symbol'] == symbol and trade not in trades:
                            trades.append(trade)
                            if trade['side'] == 'BUY':
                                current_capital -= trade['price'] * trade['quantity']
                            else:
                                current_capital += trade['price'] * trade['quantity']
            
            total_return = (current_capital - initial_capital) / initial_capital
            win_rate = len([t for t in trades if t.get('pnl', 0) > 0]) / len(trades) if trades else 0
            
            return BacktestResult(
                strategy_id=config.strategy_id,
                start_date=start_date,
                end_date=end_date,
                total_return=total_return,
                sharpe_ratio=0.0,  # Simplified calculation
                max_drawdown=0.0,   # Simplified calculation
                win_rate=win_rate,
                total_trades=len(trades),
                trades=trades
            )
            
        except Exception as e:
            self.logger.error(f"Backtest failed: {e}")
            raise
    
    async def execute_strategies(self, market_data: Dict[str, Any]):
        """Execute all active strategies with current market data"""
        if not self.running:
            return
        
        tasks = []
        for strategy_id, strategy in self.strategies.items():
            if strategy.status == StrategyStatus.ACTIVE:
                task = asyncio.create_task(strategy.execute(market_data))
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def start(self):
        """Start the algo trading service"""
        self.running = True
        self.logger.info("Algo trading service started")
    
    async def stop(self):
        """Stop the algo trading service"""
        self.running = False
        for strategy in self.strategies.values():
            await strategy.stop()
        self.logger.info("Algo trading service stopped")

# Global instance
algo_trading_service = AlgoTradingService()
