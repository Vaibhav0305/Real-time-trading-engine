#!/usr/bin/env python3
"""
Database initialization script for VittCott Trading Platform
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from models.database import Base, engine, SessionLocal
from models.user import User
from models.order import Order
from models.schemas import OrderSide, OrderType
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database and create tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
        
        # Create a test user and account
        create_sample_data()
        
        logger.info("🎉 Database initialization completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    try:
        db = SessionLocal()
        
        # Check if sample data already exists
        existing_user = db.query(User).filter(User.email == "test@vittcott.com").first()
        if existing_user:
            logger.info("Sample data already exists, skipping...")
            return
        
        # Create test user
        test_user = User(
            email="test@vittcott.com",
            username="testuser",
            hashed_password="hashed_password_here",  # In production, use proper hashing
            full_name="Test User",
            is_active=True,
            is_verified=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Create test trading account
        from models.database import TradingAccount
        test_account = TradingAccount(
            user_id=test_user.id,
            account_number="ACC001",
            account_type="INDIVIDUAL",
            balance=10000.0,
            margin_used=0.0,
            available_margin=10000.0,
            status="ACTIVE"
        )
        db.add(test_account)
        db.commit()
        db.refresh(test_account)
        
        # Create sample orders
        sample_orders = [
            Order(
                order_id="ORD001",
                user_id=test_user.id,
                account_id=test_account.id,
                symbol="AAPL",
                order_type=OrderType.LIMIT.value,
                side=OrderSide.BUY.value,
                quantity=100,
                price=150.0,
                status="PENDING"
            ),
            Order(
                order_id="ORD002",
                user_id=test_user.id,
                account_id=test_account.id,
                symbol="GOOGL",
                order_type=OrderType.MARKET.value,
                side=OrderSide.SELL.value,
                quantity=50,
                price=2800.0,
                status="FILLED",
                filled_quantity=50,
                average_price=2800.0
            )
        ]
        
        for order in sample_orders:
            db.add(order)
        
        db.commit()
        logger.info("✅ Sample data created successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to create sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting VittCott Trading Platform Database Initialization...")
    success = init_database()
    
    if success:
        logger.info("🎉 Database is ready for use!")
        sys.exit(0)
    else:
        logger.error("❌ Database initialization failed!")
        sys.exit(1)
