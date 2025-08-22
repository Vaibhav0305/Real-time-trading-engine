import asyncio
import aiohttp
import logging
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import yfinance as yf
from config.production import config

logger = logging.getLogger(__name__)

@dataclass
class MarketDataPoint:
    symbol: str
    price: float
    volume: int
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    change: float
    change_percent: float

@dataclass
class MarketQuote:
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    timestamp: datetime = None

class LiveMarketDataService:
    """Service for fetching live market data from multiple providers"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, float] = {}
        self.rate_limit_counters: Dict[str, int] = {}
        self.rate_limit_reset_times: Dict[str, float] = {}
        
        # API rate limits (requests per minute)
        self.rate_limits = {
            'alpha_vantage': 5,  # 5 requests per minute (free tier)
            'polygon': 100,      # 100 requests per minute
            'finnhub': 60,       # 60 requests per minute
            'yahoo': 100         # 100 requests per minute
        }
        
        # Initialize rate limit tracking
        for provider in self.rate_limits:
            self.rate_limit_counters[provider] = 0
            self.rate_limit_reset_times[provider] = time.time() + 60
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'VittCott-Trading-Platform/2.0.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_live_quote(self, symbol: str) -> Optional[MarketQuote]:
        """Get live quote for a symbol from multiple providers"""
        try:
            # Check cache first
            cache_key = f"quote_{symbol}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]
            
            # Try different providers in order of preference
            providers = ['yahoo', 'polygon', 'alpha_vantage', 'finnhub']
            
            for provider in providers:
                if await self._check_rate_limit(provider):
                    quote = await self._fetch_quote_from_provider(symbol, provider)
                    if quote:
                        # Cache the result
                        self._cache_data(cache_key, quote)
                        return quote
                
                # Wait before trying next provider
                await asyncio.sleep(0.1)
            
            logger.warning(f"Failed to get live quote for {symbol} from all providers")
            return None
            
        except Exception as e:
            logger.error(f"Error getting live quote for {symbol}: {e}")
            return None
    
    async def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> List[MarketDataPoint]:
        """Get historical market data"""
        try:
            cache_key = f"historical_{symbol}_{period}_{interval}"
            if self._is_cache_valid(cache_key, ttl=3600):  # 1 hour cache for historical data
                return self.cache[cache_key]
            
            # Use Yahoo Finance for historical data
            data = await self._fetch_yahoo_historical(symbol, period, interval)
            if data:
                self._cache_data(cache_key, data, ttl=3600)
                return data
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return []
    
    async def get_market_summary(self) -> Dict[str, Any]:
        """Get market summary including major indices"""
        try:
            cache_key = "market_summary"
            if self._is_cache_valid(cache_key, ttl=300):  # 5 minutes cache
                return self.cache[cache_key]
            
            indices = ['^GSPC', '^IXIC', '^DJI', '^VIX']  # S&P 500, NASDAQ, DOW, VIX
            summary = {}
            
            for index in indices:
                quote = await self.get_live_quote(index)
                if quote:
                    summary[index] = {
                        'price': quote.price,
                        'change': quote.change,
                        'change_percent': quote.change_percent,
                        'volume': quote.volume
                    }
            
            # Add market sentiment
            summary['sentiment'] = await self._calculate_market_sentiment()
            
            self._cache_data(cache_key, summary, ttl=300)
            return summary
            
        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
            return {}
    
    async def get_top_movers(self, market: str = "US") -> List[MarketQuote]:
        """Get top gainers and losers"""
        try:
            cache_key = f"top_movers_{market}"
            if self._is_cache_valid(cache_key, ttl=300):  # 5 minutes cache
                return self.cache[cache_key]
            
            # Popular stocks for top movers
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC']
            quotes = []
            
            for symbol in symbols:
                quote = await self.get_live_quote(symbol)
                if quote:
                    quotes.append(quote)
            
            # Sort by absolute change percentage
            quotes.sort(key=lambda x: abs(x.change_percent), reverse=True)
            
            self._cache_data(cache_key, quotes, ttl=300)
            return quotes
            
        except Exception as e:
            logger.error(f"Error getting top movers: {e}")
            return []
    
    async def _fetch_quote_from_provider(self, symbol: str, provider: str) -> Optional[MarketQuote]:
        """Fetch quote from specific provider"""
        try:
            if provider == 'yahoo':
                return await self._fetch_yahoo_quote(symbol)
            elif provider == 'polygon':
                return await self._fetch_polygon_quote(symbol)
            elif provider == 'alpha_vantage':
                return await self._fetch_alpha_vantage_quote(symbol)
            elif provider == 'finnhub':
                return await self._fetch_finnhub_quote(symbol)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching quote from {provider} for {symbol}: {e}")
            return None
    
    async def _fetch_yahoo_quote(self, symbol: str) -> Optional[MarketQuote]:
        """Fetch quote from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if 'regularMarketPrice' not in info or info['regularMarketPrice'] is None:
                return None
            
            current_price = info['regularMarketPrice']
            previous_close = info.get('regularMarketPreviousClose', current_price)
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close else 0
            
            return MarketQuote(
                symbol=symbol,
                price=current_price,
                change=change,
                change_percent=change_percent,
                volume=info.get('volume', 0),
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                dividend_yield=info.get('dividendYield'),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance quote for {symbol}: {e}")
            return None
    
    async def _fetch_polygon_quote(self, symbol: str) -> Optional[MarketQuote]:
        """Fetch quote from Polygon API"""
        if not config.POLYGON_API_KEY:
            return None
        
        try:
            url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev"
            params = {'apiKey': config.POLYGON_API_KEY}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('results'):
                        result = data['results'][0]
                        current_price = result['c']
                        previous_close = result['o']
                        change = current_price - previous_close
                        change_percent = (change / previous_close) * 100
                        
                        return MarketQuote(
                            symbol=symbol,
                            price=current_price,
                            change=change,
                            change_percent=change_percent,
                            volume=result.get('v', 0),
                            timestamp=datetime.now()
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching Polygon quote for {symbol}: {e}")
            return None
    
    async def _fetch_alpha_vantage_quote(self, symbol: str) -> Optional[MarketQuote]:
        """Fetch quote from Alpha Vantage API"""
        if not config.ALPHA_VANTAGE_API_KEY:
            return None
        
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': config.ALPHA_VANTAGE_API_KEY
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    quote = data.get('Global Quote')
                    
                    if quote:
                        current_price = float(quote['05. price'])
                        change = float(quote['09. change'])
                        change_percent = float(quote['10. change percent'].rstrip('%'))
                        volume = int(quote['06. volume'])
                        
                        return MarketQuote(
                            symbol=symbol,
                            price=current_price,
                            change=change,
                            change_percent=change_percent,
                            volume=volume,
                            timestamp=datetime.now()
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage quote for {symbol}: {e}")
            return None
    
    async def _fetch_finnhub_quote(self, symbol: str) -> Optional[MarketQuote]:
        """Fetch quote from Finnhub API"""
        if not config.FINNHUB_API_KEY:
            return None
        
        try:
            url = f"https://finnhub.io/api/v1/quote"
            params = {
                'symbol': symbol,
                'token': config.FINNHUB_API_KEY
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'c' in data and 'pc' in data:
                        current_price = data['c']
                        previous_close = data['pc']
                        change = current_price - previous_close
                        change_percent = (change / previous_close) * 100
                        
                        return MarketQuote(
                            symbol=symbol,
                            price=current_price,
                            change=change,
                            change_percent=change_percent,
                            volume=data.get('v', 0),
                            timestamp=datetime.now()
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching Finnhub quote for {symbol}: {e}")
            return None
    
    async def _fetch_yahoo_historical(self, symbol: str, period: str, interval: str) -> List[MarketDataPoint]:
        """Fetch historical data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            data_points = []
            for index, row in hist.iterrows():
                data_point = MarketDataPoint(
                    symbol=symbol,
                    price=row['Close'],
                    volume=row['Volume'],
                    timestamp=index.to_pydatetime(),
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    change=row['Close'] - row['Open'],
                    change_percent=((row['Close'] - row['Open']) / row['Open']) * 100
                )
                data_points.append(data_point)
            
            return data_points
            
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance historical data for {symbol}: {e}")
            return []
    
    async def _calculate_market_sentiment(self) -> str:
        """Calculate overall market sentiment"""
        try:
            # Simple sentiment calculation based on VIX and major indices
            vix_quote = await self.get_live_quote('^VIX')
            if vix_quote:
                vix_level = vix_quote.price
                
                if vix_level < 15:
                    return "Bullish"
                elif vix_level < 25:
                    return "Neutral"
                else:
                    return "Bearish"
            
            return "Neutral"
            
        except Exception as e:
            logger.error(f"Error calculating market sentiment: {e}")
            return "Neutral"
    
    async def _check_rate_limit(self, provider: str) -> bool:
        """Check if we can make a request to the provider"""
        current_time = time.time()
        
        # Reset counter if time has passed
        if current_time > self.rate_limit_reset_times[provider]:
            self.rate_limit_counters[provider] = 0
            self.rate_limit_reset_times[provider] = current_time + 60
        
        # Check if we're under the limit
        if self.rate_limit_counters[provider] < self.rate_limits[provider]:
            self.rate_limit_counters[provider] += 1
            return True
        
        return False
    
    def _is_cache_valid(self, key: str, ttl: int = None) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache_timestamps:
            return False
        
        cache_ttl = ttl or config.CACHE_TTL
        return (time.time() - self.cache_timestamps[key]) < cache_ttl
    
    def _cache_data(self, key: str, data: Any, ttl: int = None):
        """Cache data with timestamp"""
        self.cache[key] = data
        self.cache_timestamps[key] = time.time()
        
        # Clean old cache entries
        self._cleanup_cache()
    
    def _cleanup_cache(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = []
        
        for key, timestamp in self.cache_timestamps.items():
            if current_time - timestamp > config.CACHE_TTL:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
            del self.cache_timestamps[key]
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get status of all market data providers"""
        status = {
            'yahoo': {'enabled': True, 'rate_limit': self.rate_limits['yahoo']},
            'polygon': {'enabled': bool(config.POLYGON_API_KEY), 'rate_limit': self.rate_limits['polygon']},
            'alpha_vantage': {'enabled': bool(config.ALPHA_VANTAGE_API_KEY), 'rate_limit': self.rate_limits['alpha_vantage']},
            'finnhub': {'enabled': bool(config.FINNHUB_API_KEY), 'rate_limit': self.rate_limits['finnhub']}
        }
        
        # Add current usage
        for provider in status:
            status[provider]['current_usage'] = self.rate_limit_counters[provider]
            status[provider]['reset_time'] = self.rate_limit_reset_times[provider] - time.time()
        
        return status

# Global instance
live_market_data_service = LiveMarketDataService()
