import finnhub
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from backend.config import settings

logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self):
        self.client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)
        self.price_cache: Dict[str, Dict] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        self.cache_duration = timedelta(seconds=2)  # Real-time: 2 second cache
        self.market_hours = {
            'start': '09:30',  # Market open (EST)
            'end': '16:00'     # Market close (EST)
        }
        
    async def get_real_time_price(self, symbol: str) -> Optional[Dict]:
        """Get real-time price for a symbol"""
        try:
            # Check cache first
            if self._is_cache_valid(symbol):
                return self.price_cache[symbol]
            
            # Fetch from Finnhub
            quote = self.client.quote(symbol)
            
            if quote and 'c' in quote:  # 'c' is current price
                # Calculate additional metrics
                current_price = quote['c']
                previous_close = quote.get('pc', 0)
                change = current_price - previous_close
                change_percent = (change / previous_close * 100) if previous_close > 0 else 0
                
                price_data = {
                    'symbol': symbol,
                    'current_price': current_price,
                    'change': round(change, 2),
                    'change_percent': round(change_percent, 2),
                    'high': quote.get('h', 0),
                    'low': quote.get('l', 0),
                    'open': quote.get('o', 0),
                    'previous_close': previous_close,
                    'volume': quote.get('v', 0),
                    'market_cap': quote.get('mkt_cap', 0),
                    'timestamp': datetime.now().isoformat(),
                    'is_market_open': self._is_market_open()
                }
                
                # Update cache
                self.price_cache[symbol] = price_data
                self.cache_expiry[symbol] = datetime.now()
                
                logger.info(f"Real-time price for {symbol}: ${current_price} ({change_percent:+.2f}%)")
                return price_data
            else:
                logger.warning(f"No price data available for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {str(e)}")
            return None
    
    async def get_market_depth(self, symbol: str) -> Optional[Dict]:
        """Get market depth (bid/ask orders) - like Zerodha"""
        try:
            # Note: Finnhub free tier doesn't provide real-time order book
            # This is a simulation for demo purposes
            current_price = await self.get_real_time_price(symbol)
            if not current_price:
                return None
                
            price = current_price['current_price']
            
            # Simulate market depth
            depth = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'bids': [
                    {'price': round(price * 0.999, 2), 'quantity': 1000},
                    {'price': round(price * 0.998, 2), 'quantity': 2500},
                    {'price': round(price * 0.997, 2), 'quantity': 5000},
                ],
                'asks': [
                    {'price': round(price * 1.001, 2), 'quantity': 1200},
                    {'price': round(price * 1.002, 2), 'quantity': 3000},
                    {'price': round(price * 1.003, 2), 'quantity': 6000},
                ]
            }
            
            return depth
            
        except Exception as e:
            logger.error(f"Error fetching market depth for {symbol}: {str(e)}")
            return None
    
    async def get_market_overview(self) -> Dict:
        """Get comprehensive market overview like Zerodha dashboard"""
        try:
            # Major indices
            indices = ['^GSPC', '^DJI', '^IXIC', '^NSEI']  # S&P 500, Dow, NASDAQ, Nifty
            index_data = {}
            
            for index in indices:
                try:
                    quote = self.client.quote(index)
                    if quote and 'c' in quote:
                        index_data[index] = {
                            'name': self._get_index_name(index),
                            'current': quote['c'],
                            'change': quote.get('d', 0),
                            'change_percent': quote.get('dp', 0)
                        }
                except:
                    continue
            
            # Sector performance (simulated for demo)
            sectors = [
                {'name': 'Technology', 'change': 1.2, 'leaders': ['AAPL', 'MSFT', 'GOOGL']},
                {'name': 'Healthcare', 'change': -0.8, 'leaders': ['JNJ', 'PFE', 'UNH']},
                {'name': 'Financial', 'change': 0.5, 'leaders': ['JPM', 'BAC', 'WFC']},
                {'name': 'Energy', 'change': -1.1, 'leaders': ['XOM', 'CVX', 'COP']}
            ]
            
            return {
                'indices': index_data,
                'sectors': sectors,
                'market_status': 'Open' if self._is_market_open() else 'Closed',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching market overview: {str(e)}")
            return {}
    
    async def search_symbols(self, query: str) -> List[Dict]:
        """Search for symbols like Zerodha's search functionality"""
        try:
            # Get all US symbols from Finnhub
            symbols = self.client.stock_symbols('US')
            
            # Filter by query
            results = []
            query_lower = query.lower()
            
            for symbol in symbols[:100]:  # Limit results
                if (query_lower in symbol['symbol'].lower() or 
                    query_lower in symbol['description'].lower()):
                    results.append({
                        'symbol': symbol['symbol'],
                        'name': symbol['description'],
                        'exchange': symbol['primaryExchange'],
                        'type': symbol['type']
                    })
            
            return results[:20]  # Return top 20 matches
            
        except Exception as e:
            logger.error(f"Error searching symbols: {str(e)}")
            return []
    
    def _get_index_name(self, symbol: str) -> str:
        """Get human-readable index names"""
        names = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'NASDAQ',
            '^NSEI': 'Nifty 50'
        }
        return names.get(symbol, symbol)
    
    def _is_market_open(self) -> bool:
        """Check if US market is open (simplified)"""
        now = datetime.now()
        # Simple check: Monday-Friday, 9:30 AM - 4:00 PM EST
        # In production, you'd use proper market calendar
        return now.weekday() < 5  # Monday = 0, Friday = 4
    
    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get real-time prices for multiple symbols"""
        tasks = [self.get_real_time_price(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching {symbol}: {str(result)}")
                continue
            if result:
                prices[symbol] = result
        
        return prices
    
    async def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """Get company profile information"""
        try:
            profile = self.client.company_profile2(symbol=symbol)
            if profile:
                return {
                    'symbol': symbol,
                    'name': profile.get('name', ''),
                    'exchange': profile.get('exchange', ''),
                    'currency': profile.get('currency', ''),
                    'country': profile.get('country', ''),
                    'industry': profile.get('finnhubIndustry', ''),
                    'market_cap': profile.get('marketCapitalization', 0),
                    'shares_outstanding': profile.get('shareOutstanding', 0)
                }
            return None
        except Exception as e:
            logger.error(f"Error fetching company profile for {symbol}: {str(e)}")
            return None
    
    async def get_symbols(self) -> List[Dict]:
        """Get available trading symbols"""
        try:
            # Popular symbols for demo
            popular_symbols = [
                {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
                {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
                {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ"},
                {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ"},
                {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ"},
                {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ"},
                {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ"},
                {"symbol": "NFLX", "name": "Netflix Inc.", "exchange": "NASDAQ"}
            ]
            
            # Add real-time prices to symbols
            symbols_with_prices = []
            for symbol_info in popular_symbols:
                price_data = await self.get_real_time_price(symbol_info['symbol'])
                if price_data:
                    symbol_info.update({
                        'current_price': price_data['current_price'],
                        'change': price_data['change'],
                        'change_percent': price_data['change_percent']
                    })
                symbols_with_prices.append(symbol_info)
            
            return symbols_with_prices
            
        except Exception as e:
            logger.error(f"Error fetching symbols: {str(e)}")
            return []
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """Check if cached price is still valid"""
        if symbol not in self.cache_expiry:
            return False
        return datetime.now() - self.cache_expiry[symbol] < self.cache_duration
    
    async def start_price_stream(self, symbols: List[str], callback):
        """Start streaming price updates (simulated with polling)"""
        while True:
            try:
                prices = await self.get_multiple_prices(symbols)
                if prices:
                    await callback(prices)
                await asyncio.sleep(5)  # Update every 5 seconds
            except Exception as e:
                logger.error(f"Error in price stream: {str(e)}")
                await asyncio.sleep(10)  # Wait longer on error

# Global instance
market_data_service = MarketDataService()
