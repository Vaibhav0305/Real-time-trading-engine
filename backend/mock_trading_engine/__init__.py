
"""
Mock trading engine module for development/testing
"""
from typing import List, Dict, Any
from datetime import datetime
import uuid
from enum import Enum

class MockOrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"

class MockOrder:
    def __init__(self, order_id, symbol, order_type, price, quantity):
        self.order_id = order_id
        self.symbol = symbol
        self.order_type = order_type
        self.price = price
        self.quantity = quantity
    
    def toString(self):
        return f"Order({self.order_id}, {self.symbol}, {self.order_type}, {self.price}, {self.quantity})"

class MockTrade:
    def __init__(self, trade_id, buy_order_id, sell_order_id, symbol, price, quantity):
        self.trade_id = trade_id
        self.buy_order_id = buy_order_id
        self.sell_order_id = sell_order_id
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
    
    def toString(self):
        return f"Trade({self.trade_id}, {self.symbol}, {self.price}, {self.quantity})"

class MockLogger:
    def __init__(self, log_file="mock_trading.log"):
        self.log_file = log_file
    
    def log(self, message):
        print(f"[MOCK LOG] {message}")
    
    def consoleLog(self, message):
        print(f"[MOCK CONSOLE] {message}")

class MockEmailNotifier:
    def __init__(self):
        pass
    
    def sendOrderPlacedNotification(self, order):
        print(f"[MOCK EMAIL] Order placed notification for {order.toString()}")
    
    def sendTradeExecutedNotification(self, trade):
        print(f"[MOCK EMAIL] Trade executed notification for {trade.toString()}")
    
    def sendOrderCancelledNotification(self, order):
        print(f"[MOCK EMAIL] Order cancelled notification for {order.toString()}")

class MockOrderBook:
    def __init__(self, symbol, logger, email_notifier):
        self.symbol = symbol
        self.logger = logger
        self.email_notifier = email_notifier
        self.orders = []
        self.trades = []
    
    def addOrder(self, order):
        self.orders.append(order)
        self.logger.log(f"Added order to {self.symbol}: {order.toString()}")
        # Simulate some trades
        if len(self.orders) > 1:
            mock_trade = MockTrade(
                str(uuid.uuid4()),
                self.orders[-2].order_id,
                self.orders[-1].order_id,
                self.symbol,
                order.price,
                min(self.orders[-2].quantity, order.quantity)
            )
            self.trades.append(mock_trade)
            return [mock_trade]
        return []
    
    def modifyOrder(self, order_id, new_price, new_quantity):
        for order in self.orders:
            if order.order_id == order_id:
                order.price = new_price
                order.quantity = new_quantity
                self.logger.log(f"Modified order {order_id}")
                return []
        return []
    
    def cancelOrder(self, order_id):
        for i, order in enumerate(self.orders):
            if order.order_id == order_id:
                del self.orders[i]
                self.logger.log(f"Cancelled order {order_id}")
                return True
        return False
    
    def getAllOrders(self):
        return self.orders
    
    def matchOrders(self):
        # Simple matching logic
        if len(self.orders) < 2:
            return []
        
        trades = []
        for i in range(len(self.orders) - 1):
            for j in range(i + 1, len(self.orders)):
                order1 = self.orders[i]
                order2 = self.orders[j]
                
                if (order1.order_type != order2.order_type and 
                    order1.symbol == order2.symbol and
                    order1.price == order2.price):
                    
                    trade_quantity = min(order1.quantity, order2.quantity)
                    if trade_quantity > 0:
                        mock_trade = MockTrade(
                            str(uuid.uuid4()),
                            order1.order_id,
                            order2.order_id,
                            order1.symbol,
                            order1.price,
                            trade_quantity
                        )
                        trades.append(mock_trade)
        
        return trades

class MockMatchingEngine:
    def __init__(self, logger, email_notifier):
        self.logger = logger
        self.email_notifier = email_notifier
        self.order_books = {}
    
    def placeOrder(self, order):
        if order.symbol not in self.order_books:
            self.order_books[order.symbol] = MockOrderBook(order.symbol, self.logger, self.email_notifier)
        
        order_book = self.order_books[order.symbol]
        trades = order_book.addOrder(order)
        
        self.email_notifier.sendOrderPlacedNotification(order)
        for trade in trades:
            self.email_notifier.sendTradeExecutedNotification(trade)
    
    def cancelOrder(self, symbol, order_id):
        if symbol in self.order_books:
            return self.order_books[symbol].cancelOrder(order_id)
        return False
    
    def modifyOrder(self, symbol, order_id, new_price, new_quantity):
        if symbol in self.order_books:
            return self.order_books[symbol].modifyOrder(order_id, new_price, new_quantity)
        return []
    
    def getAllOrders(self):
        all_orders = []
        for order_book in self.order_books.values():
            all_orders.extend(order_book.getAllOrders())
        return all_orders
    
    def matchOrders(self):
        for order_book in self.order_books.values():
            trades = order_book.matchOrders()
            for trade in trades:
                self.email_notifier.sendTradeExecutedNotification(trade)

# Create mock instances
def create_mock_instances():
    logger = MockLogger()
    email_notifier = MockEmailNotifier()
    matching_engine = MockMatchingEngine(logger, email_notifier)
    return logger, email_notifier, matching_engine

# Export classes for pybind11 compatibility
__all__ = [
    'MockOrderType', 'MockOrder', 'MockTrade', 'MockLogger', 'MockEmailNotifier', 
    'MockOrderBook', 'MockMatchingEngine', 'create_mock_instances'
]
