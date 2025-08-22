from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
from config import settings

# Database setup
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    accounts = relationship("TradingAccount", back_populates="user")
    orders = relationship("Order", back_populates="user")
    trades = relationship("Trade", back_populates="user")

# Trading Account Model
class TradingAccount(Base):
    __tablename__ = "trading_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_number = Column(String, unique=True, index=True, nullable=False)
    account_type = Column(String, default="INDIVIDUAL")  # INDIVIDUAL, CORPORATE
    balance = Column(Float, default=0.0)
    margin_used = Column(Float, default=0.0)
    available_margin = Column(Float, default=0.0)
    status = Column(String, default="ACTIVE")  # ACTIVE, SUSPENDED, CLOSED
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    positions = relationship("Position", back_populates="account")

# Order Model
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("trading_accounts.id"), nullable=False)
    symbol = Column(String, nullable=False)
    order_type = Column(String, nullable=False)  # MARKET, LIMIT, STOP, STOP_LIMIT
    side = Column(String, nullable=False)  # BUY, SELL
    quantity = Column(Integer, nullable=False)
    price = Column(Float)
    stop_price = Column(Float)
    status = Column(String, default="PENDING")  # PENDING, PARTIALLY_FILLED, FILLED, CANCELLED, REJECTED
    filled_quantity = Column(Integer, default=0)
    average_price = Column(Float)
    commission = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    trades = relationship("Trade", back_populates="order")

# Trade Model
class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String, unique=True, index=True, nullable=False)
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # BUY, SELL
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    commission = Column(Float, default=0.0)
    executed_at = Column(DateTime, default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="trades")
    user = relationship("User", back_populates="trades")

# Position Model
class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("trading_accounts.id"), nullable=False)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # LONG, SHORT
    quantity = Column(Integer, default=0)
    average_price = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    account = relationship("TradingAccount", back_populates="positions")

# Market Data Model
class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
    created_at = Column(DateTime, default=func.now())

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)
