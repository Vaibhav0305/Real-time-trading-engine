#!/usr/bin/env python3
"""
Test script for C++ trading engine integration
"""

import sys
import os
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cpp_engine():
    """Test the C++ engine integration"""
    try:
        from cpp_bindings import get_cpp_engine
        
        logger.info("Testing C++ engine integration...")
        
        # Get the engine instance
        engine = get_cpp_engine()
        logger.info("✅ C++ engine initialized successfully")
        
        # Test placing an order
        logger.info("Testing order placement...")
        result = engine.place_order("AAPL", "BUY", 150.50, 100)
        logger.info(f"✅ Order placed: {result}")
        
        # Test getting order book
        logger.info("Testing order book retrieval...")
        order_book = engine.get_order_book("AAPL")
        logger.info(f"✅ Order book retrieved: {order_book}")
        
        # Test order modification
        logger.info("Testing order modification...")
        modified = engine.modify_order("AAPL", result["order_id"], 155.00, 150)
        logger.info(f"✅ Order modified: {modified}")
        
        # Test order cancellation
        logger.info("Testing order cancellation...")
        cancelled = engine.cancel_order("AAPL", result["order_id"])
        logger.info(f"✅ Order cancelled: {cancelled}")
        
        logger.info("🎉 All C++ engine tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ C++ engine test failed: {e}")
        return False

def test_trading_service():
    """Test the trading service with C++ engine"""
    try:
        from services.trading_engine import trading_service
        
        logger.info("Testing trading service with C++ engine...")
        
        # Test placing an order through the service
        from models.order import OrderCreate, OrderType
        
        order_data = OrderCreate(
            symbol="MSFT",
            type=OrderType.SELL,
            price=300.00,
            quantity=50
        )
        
        order = trading_service.place_order(order_data)
        logger.info(f"✅ Order placed through service: {order}")
        
        # Test getting order book
        order_book = trading_service.get_order_book("MSFT")
        logger.info(f"✅ Order book through service: {order_book}")
        
        logger.info("🎉 Trading service tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Trading service test failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting VittCott C++ Engine Integration Tests...")
    
    # Test C++ engine directly
    cpp_success = test_cpp_engine()
    
    # Test trading service
    service_success = test_trading_service()
    
    if cpp_success and service_success:
        logger.info("🎉 All integration tests passed!")
        sys.exit(0)
    else:
        logger.error("💥 Some integration tests failed!")
        sys.exit(1)
