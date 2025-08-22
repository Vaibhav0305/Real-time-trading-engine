import sys
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

# Import our C++ engine bindings
try:
    from cpp_bindings import get_cpp_engine
    logging.info("Successfully imported C++ trading engine bindings")
    USE_CPP = True
except ImportError as e:
    logging.warning(f"Failed to import C++ trading engine bindings: {e}")
    logging.info("Falling back to mock trading engine for development")
    USE_CPP = False
    
    # Add the mock module to the path
    mock_path = os.path.join(os.path.dirname(__file__), '..', 'mock_trading_engine')
    if mock_path not in sys.path:
        sys.path.insert(0, mock_path)
    
    try:
        from mock_trading_engine import MockOrderType, MockOrder, MockTrade, MockLogger, MockEmailNotifier, MockOrderBook, MockMatchingEngine
        logging.info("Successfully imported mock trading engine")
    except ImportError as e2:
        logging.error(f"Failed to import mock trading engine: {e2}")
        raise

from models.schemas import Order, OrderCreate, OrderUpdate, OrderType, OrderStatus, Trade

class TradingEngineService:
    def __init__(self):
        """Initialize the trading engine service with C++ or mock components"""
        try:
            if USE_CPP:
                # Use C++ engine through bindings
                self.cpp_engine = get_cpp_engine()
                logging.info("Trading engine service initialized with C++ engine")
            else:
                # Use mock components
                self.logger = MockLogger("trading_engine.log")
                self.email_notifier = MockEmailNotifier()
                self.matching_engine = MockMatchingEngine(self.logger, self.email_notifier)
                logging.info("Trading engine service initialized with MOCK components")

            # In-memory storage for orders and trades (in production, use a database)
            self.orders: Dict[str, Order] = {}
            self.trades: List[Trade] = []

        except Exception as e:
            logging.error(f"Failed to initialize trading engine service: {e}")
            raise

    def place_order(self, order_data: OrderCreate) -> Order:
        """Place a new order"""
        try:
            order_id = str(uuid.uuid4())
            
            if USE_CPP:
                # Use C++ engine
                result = self.cpp_engine.place_order(
                    order_data.symbol,
                    order_data.type.value,
                    order_data.price,
                    order_data.quantity
                )
                
                # Create order object from result
                order = Order(
                    order_id=result["order_id"],
                    symbol=result["symbol"],
                    type=OrderType(result["type"]),
                    price=result["price"],
                    quantity=result["quantity"],
                    status=OrderStatus.PENDING,
                    timestamp=datetime.fromisoformat(result["timestamp"]),
                    filled_quantity=0
                )
            else:
                # Use mock engine
                order_type = MockOrderType.BUY if order_data.type == OrderType.BUY else MockOrderType.SELL
                cpp_order = MockOrder(
                    order_id,
                    order_data.symbol,
                    order_type,
                    order_data.price,
                    order_data.quantity
                )
                
                self.matching_engine.placeOrder(cpp_order)
                
                order = Order(
                    order_id=order_id,
                    symbol=order_data.symbol,
                    type=order_data.type,
                    price=order_data.price,
                    quantity=order_data.quantity,
                    status=OrderStatus.PENDING,
                    timestamp=datetime.now(),
                    filled_quantity=0
                )
            
            self.orders[order_id] = order
            logging.info(f"Order placed successfully: {order_id}")
            return order
            
        except Exception as e:
            logging.error(f"Failed to place order: {e}")
            raise

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order"""
        try:
            if order_id not in self.orders:
                return False
            
            order = self.orders[order_id]
            
            if USE_CPP:
                # Use C++ engine
                success = self.cpp_engine.cancel_order(order.symbol, order_id)
            else:
                # Use mock engine
                success = self.matching_engine.cancelOrder(order.symbol, order_id)
            
            if success:
                order.status = OrderStatus.CANCELLED
                logging.info(f"Order cancelled successfully: {order_id}")
                return True
            else:
                logging.warning(f"Failed to cancel order: {order_id}")
                return False
                
        except Exception as e:
            logging.error(f"Failed to cancel order {order_id}: {e}")
            return False

    def modify_order(self, order_id: str, order_update: OrderUpdate) -> Optional[Order]:
        """Modify an existing order"""
        try:
            if order_id not in self.orders:
                return None
            
            order = self.orders[order_id]
            new_price = order_update.price if order_update.price is not None else order.price
            new_quantity = order_update.quantity if order_update.quantity is not None else order.quantity
            
            if USE_CPP:
                # Use C++ engine
                result = self.cpp_engine.modify_order(order.symbol, order_id, new_price, new_quantity)
                
                # Update order with new values
                order.price = new_price
                order.quantity = new_quantity
                order.status = OrderStatus.MODIFIED
                order.timestamp = datetime.fromisoformat(result["timestamp"])
            else:
                # Use mock engine
                self.matching_engine.modifyOrder(order.symbol, order_id, new_price, new_quantity)
                
                order.price = new_price
                order.quantity = new_quantity
            
            logging.info(f"Order modified successfully: {order_id}")
            return order
            
        except Exception as e:
            logging.error(f"Failed to modify order {order_id}: {e}")
            return None

    def get_all_orders(self) -> List[Order]:
        """Get all orders"""
        return list(self.orders.values())

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get a specific order by ID"""
        return self.orders.get(order_id)

    def get_trades(self) -> List[Trade]:
        """Get all trades"""
        return self.trades.copy()

    def get_order_book(self, symbol: str) -> Dict[str, Any]:
        """Get order book for a specific symbol"""
        try:
            if USE_CPP:
                # Use C++ engine
                return self.cpp_engine.get_order_book(symbol)
            else:
                # For mock engine, we can get orders from the matching engine
                all_orders = self.matching_engine.getAllOrders()
                symbol_orders = [order for order in all_orders if order.symbol == symbol]
                
                # Group by price
                bids = {}
                asks = {}
                
                for order in symbol_orders:
                    if order.order_type == MockOrderType.BUY:
                        if order.price not in bids:
                            bids[order.price] = 0
                        bids[order.price] += order.quantity
                    else:
                        if order.price not in asks:
                            asks[order.price] = 0
                        asks[order.price] += order.quantity
                
                # Convert to list format
                bid_entries = [{"price": price, "quantity": qty, "order_count": 1} for price, qty in bids.items()]
                ask_entries = [{"price": price, "quantity": qty, "order_count": 1} for price, qty in asks.items()]
                
                return {
                    "symbol": symbol,
                    "bids": sorted(bid_entries, key=lambda x: x["price"], reverse=True),
                    "asks": sorted(ask_entries, key=lambda x: x["price"]),
                    "last_updated": datetime.now()
                }
                
        except Exception as e:
            logging.error(f"Failed to get order book for {symbol}: {e}")
            return {"symbol": symbol, "bids": [], "asks": [], "last_updated": datetime.now().isoformat()}

# Create global instance
trading_service = TradingEngineService()
