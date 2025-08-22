from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

class OrderType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"

class OrderCreate(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL)")
    type: OrderType = Field(..., description="Order type: BUY or SELL")
    price: float = Field(..., gt=0, description="Order price")
    quantity: int = Field(..., gt=0, description="Order quantity")

class OrderUpdate(BaseModel):
    price: Optional[float] = Field(None, gt=0, description="New order price")
    quantity: Optional[int] = Field(None, gt=0, description="New order quantity")

class Order(BaseModel):
    order_id: str = Field(..., description="Unique order identifier")
    symbol: str = Field(..., description="Stock symbol")
    type: OrderType = Field(..., description="Order type")
    price: float = Field(..., description="Order price")
    quantity: int = Field(..., description="Order quantity")
    status: OrderStatus = Field(..., description="Order status")
    timestamp: datetime = Field(..., description="Order timestamp")
    filled_quantity: int = Field(default=0, description="Quantity filled so far")

class Trade(BaseModel):
    trade_id: str = Field(..., description="Unique trade identifier")
    buy_order_id: str = Field(..., description="Buy order ID")
    sell_order_id: str = Field(..., description="Sell order ID")
    symbol: str = Field(..., description="Stock symbol")
    price: float = Field(..., description="Trade price")
    quantity: int = Field(..., description="Trade quantity")
    timestamp: datetime = Field(..., description="Trade timestamp")

class OrderBookEntry(BaseModel):
    price: float = Field(..., description="Price level")
    quantity: int = Field(..., description="Total quantity at this price")
    order_count: int = Field(..., description="Number of orders at this price")

class OrderBook(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    bids: list[OrderBookEntry] = Field(..., description="Buy orders")
    asks: list[OrderBookEntry] = Field(..., description="Sell orders")
    last_updated: datetime = Field(..., description="Last update timestamp")
