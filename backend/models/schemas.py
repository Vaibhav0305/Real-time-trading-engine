from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class PositionSide(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"

# Base schemas
class OrderBase(BaseModel):
    symbol: str = Field(..., description="Trading symbol (e.g., AAPL, GOOGL)")
    order_type: OrderType = Field(..., description="Type of order")
    side: OrderSide = Field(..., description="Buy or Sell")
    quantity: int = Field(..., gt=0, description="Number of shares")
    price: Optional[float] = Field(None, gt=0, description="Limit price (required for LIMIT orders)")
    stop_price: Optional[float] = Field(None, gt=0, description="Stop price (required for STOP orders)")

class OrderCreate(OrderBase):
    order_id: str = Field(..., description="Unique order identifier")

class OrderUpdate(BaseModel):
    price: Optional[float] = Field(None, gt=0, description="New limit price")
    quantity: Optional[int] = Field(None, gt=0, description="New quantity")
    stop_price: Optional[float] = Field(None, gt=0, description="New stop price")

class OrderResponse(OrderBase):
    id: int
    order_id: str
    user_id: int
    account_id: int
    status: OrderStatus
    filled_quantity: int
    average_price: Optional[float]
    commission: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Trade schemas
class TradeBase(BaseModel):
    symbol: str
    side: OrderSide
    quantity: int
    price: float
    commission: float

class TradeResponse(TradeBase):
    id: int
    trade_id: str
    order_id: str
    user_id: int
    executed_at: datetime

    class Config:
        from_attributes = True

# Position schemas
class PositionBase(BaseModel):
    symbol: str
    side: PositionSide
    quantity: int
    average_price: float
    unrealized_pnl: float
    realized_pnl: float

class PositionResponse(PositionBase):
    id: int
    account_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Account schemas
class AccountBase(BaseModel):
    account_number: str
    account_type: str
    balance: float
    margin_used: float
    available_margin: float
    status: str

class AccountResponse(AccountBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Order Book schemas
class OrderBookEntry(BaseModel):
    price: float
    quantity: int
    total_quantity: int

class OrderBookResponse(BaseModel):
    symbol: str
    timestamp: datetime
    bids: List[OrderBookEntry]
    asks: List[OrderBookEntry]
    spread: float
    last_price: Optional[float]
    volume: int

# Market Data schemas
class MarketDataResponse(BaseModel):
    symbol: str
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    change: float
    change_percent: float

# User schemas
class UserBase(BaseModel):
    email: str
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# WebSocket message schemas
class WebSocketMessage(BaseModel):
    type: str
    data: Optional[dict] = None
    symbol: Optional[str] = None
    message: Optional[str] = None

# Portfolio schemas
class PortfolioSummary(BaseModel):
    total_value: float
    total_pnl: float
    unrealized_pnl: float
    realized_pnl: float
    available_cash: float
    margin_used: float
    positions_count: int

# Watchlist schemas
class WatchlistEntry(BaseModel):
    symbol: str
    name: str
    current_price: float
    change: float
    change_percent: float
    added_at: datetime

class WatchlistResponse(BaseModel):
    id: int
    name: str
    entries: List[WatchlistEntry]
    created_at: datetime
    updated_at: datetime

# Notification schemas
class NotificationBase(BaseModel):
    title: str
    message: str
    type: str  # INFO, WARNING, ERROR, SUCCESS
    is_read: bool = False

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
