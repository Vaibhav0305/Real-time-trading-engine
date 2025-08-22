import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import apiService from '../services/api';

const TradingContext = createContext();

export const useTrading = () => {
  const context = useContext(TradingContext);
  if (!context) {
    throw new Error('useTrading must be used within a TradingProvider');
  }
  return context;
};

export const TradingProvider = ({ children }) => {
  const [orders, setOrders] = useState([]);
  const [trades, setTrades] = useState([]);
  const [positions, setPositions] = useState([]);
  const [orderBook, setOrderBook] = useState({ bids: [], asks: [] });
  const [marketData, setMarketData] = useState({});
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [websocket, setWebsocket] = useState(null);

  // Available trading symbols
  const symbols = [
    { symbol: 'AAPL', name: 'Apple Inc.', exchange: 'NASDAQ' },
    { symbol: 'GOOGL', name: 'Alphabet Inc.', exchange: 'NASDAQ' },
    { symbol: 'MSFT', name: 'Microsoft Corporation', exchange: 'NASDAQ' },
    { symbol: 'AMZN', name: 'Amazon.com Inc.', exchange: 'NASDAQ' },
    { symbol: 'TSLA', name: 'Tesla Inc.', exchange: 'NASDAQ' },
    { symbol: 'NFLX', name: 'Netflix Inc.', exchange: 'NASDAQ' },
    { symbol: 'META', name: 'Meta Platforms Inc.', exchange: 'NASDAQ' },
    { symbol: 'NVDA', name: 'NVIDIA Corporation', exchange: 'NASDAQ' },
    { symbol: 'JPM', name: 'JPMorgan Chase & Co.', exchange: 'NYSE' },
    { symbol: 'JNJ', name: 'Johnson & Johnson', exchange: 'NYSE' },
  ];

  // Mock market data for demonstration
  const mockMarketData = {
    AAPL: { price: 150.25, change: 2.15, changePercent: 1.45, volume: 45678900 },
    GOOGL: { price: 2800.00, change: -15.50, changePercent: -0.55, volume: 12345600 },
    MSFT: { price: 380.50, change: 8.75, changePercent: 2.35, volume: 23456700 },
    TSLA: { price: 245.80, change: 12.30, changePercent: 5.27, volume: 34567800 },
    AMZN: { price: 3200.00, change: 45.20, changePercent: 1.43, volume: 5678900 },
    NFLX: { price: 450.75, change: -8.25, changePercent: -1.80, volume: 6789000 },
    META: { price: 320.50, change: 5.75, changePercent: 1.83, volume: 7890000 },
    NVDA: { price: 850.25, change: 25.50, changePercent: 3.09, volume: 8900000 },
    JPM: { price: 180.75, change: -2.25, changePercent: -1.23, volume: 4567000 },
    JNJ: { price: 165.50, change: 1.25, changePercent: 0.76, volume: 3456000 },
  };

  // Initialize market data
  useEffect(() => {
    setMarketData(mockMarketData);
  }, []);

  // Fetch orders from API
  const fetchOrders = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getOrders();
      setOrders(response || []);
    } catch (err) {
      setError('Failed to fetch orders');
      console.error('Error fetching orders:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch trades from API
  const fetchTrades = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getTrades();
      setTrades(response || []);
    } catch (err) {
      setError('Failed to fetch trades');
      console.error('Error fetching trades:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch order book for selected symbol
  const fetchOrderBook = useCallback(async (symbol) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getOrderBook(symbol);
      setOrderBook(response || { bids: [], asks: [] });
    } catch (err) {
      setError('Failed to fetch order book');
      console.error('Error fetching order book:', err);
      // Use mock data as fallback
      setOrderBook({
        bids: [
          { price: 150.20, quantity: 100 },
          { price: 150.15, quantity: 200 },
          { price: 150.10, quantity: 150 },
        ],
        asks: [
          { price: 150.30, quantity: 120 },
          { price: 150.35, quantity: 180 },
          { price: 150.40, quantity: 90 },
        ],
      });
    } finally {
      setLoading(false);
    }
  }, []);

  // Place a new order
  const placeOrder = useCallback(async (orderData) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.placeOrder(orderData);
      
      // Add the new order to the local state
      const newOrder = {
        ...orderData,
        id: Date.now(),
        order_id: `ORD-${Date.now()}`,
        status: 'pending',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      
      setOrders(prev => [newOrder, ...prev]);
      
      return { success: true, order: newOrder };
    } catch (err) {
      setError('Failed to place order');
      console.error('Error placing order:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Cancel an order
  const cancelOrder = useCallback(async (orderId) => {
    try {
      setLoading(true);
      setError(null);
      
      await apiService.cancelOrder(orderId);
      
      // Update the order status in local state
      setOrders(prev => 
        prev.map(order => 
          order.id === orderId 
            ? { ...order, status: 'cancelled', updated_at: new Date().toISOString() }
            : order
        )
      );
      
      return { success: true };
    } catch (err) {
      setError('Failed to cancel order');
      console.error('Error cancelling order:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Modify an existing order
  const modifyOrder = useCallback(async (orderId, orderUpdate) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.modifyOrder(orderId, orderUpdate);
      
      // Update the order in local state
      setOrders(prev => 
        prev.map(order => 
          order.id === orderId 
            ? { ...order, ...orderUpdate, updated_at: new Date().toISOString() }
            : order
        )
      );
      
      return { success: true, order: response };
    } catch (err) {
      setError('Failed to modify order');
      console.error('Error modifying order:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Update market data (simulated real-time updates)
  const updateMarketData = useCallback((symbol, newData) => {
    setMarketData(prev => ({
      ...prev,
      [symbol]: { ...prev[symbol], ...newData },
    }));
  }, []);

  // Simulate real-time price updates
  useEffect(() => {
    const interval = setInterval(() => {
      symbols.forEach(({ symbol }) => {
        const currentData = marketData[symbol];
        if (currentData) {
          // Simulate small price movements
          const change = (Math.random() - 0.5) * 2; // -1 to +1
          const newPrice = currentData.price + change;
          const newChange = currentData.change + change;
          const newChangePercent = (newChange / (newPrice - newChange)) * 100;
          
          updateMarketData(symbol, {
            price: parseFloat(newPrice.toFixed(2)),
            change: parseFloat(newChange.toFixed(2)),
            changePercent: parseFloat(newChangePercent.toFixed(2)),
          });
        }
      });
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, [marketData, symbols, updateMarketData]);

  // Fetch initial data when component mounts
  useEffect(() => {
    fetchOrders();
    fetchTrades();
    fetchOrderBook(selectedSymbol);
  }, [fetchOrders, fetchTrades, fetchOrderBook, selectedSymbol]);

  const value = {
    // State
    orders,
    trades,
    positions,
    orderBook,
    marketData,
    selectedSymbol,
    loading,
    error,
    symbols,
    
    // Actions
    setSelectedSymbol,
    placeOrder,
    cancelOrder,
    modifyOrder,
    fetchOrders,
    fetchTrades,
    fetchOrderBook,
    updateMarketData,
    
    // Computed values
    getCurrentPrice: (symbol) => marketData[symbol]?.price || 0,
    getPriceChange: (symbol) => marketData[symbol]?.change || 0,
    getPriceChangePercent: (symbol) => marketData[symbol]?.changePercent || 0,
  };

  return (
    <TradingContext.Provider value={value}>
      {children}
    </TradingContext.Provider>
  );
};
