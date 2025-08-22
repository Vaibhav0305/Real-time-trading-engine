import React, { useState, useEffect, useRef } from 'react';
import './AdvancedTradingDashboard.css';

const AdvancedTradingDashboard = () => {
  const [marketData, setMarketData] = useState({});
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [watchlist, setWatchlist] = useState([]);
  const [portfolio, setPortfolio] = useState([]);
  const [orders, setOrders] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [orderForm, setOrderForm] = useState({
    type: 'MARKET',
    side: 'BUY',
    quantity: 100,
    price: 0,
    validity: 'DAY'
  });

  const wsRef = useRef(null);
  const dataUpdateInterval = useRef(null);

  // Popular symbols for real-time data
  const popularSymbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA', 'NFLX', 'JPM', 'JNJ'];

  useEffect(() => {
    initializeDashboard();
    setupRealTimeUpdates();
    
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (dataUpdateInterval.current) clearInterval(dataUpdateInterval.current);
    };
  }, []);

  const initializeDashboard = async () => {
    try {
      setIsLoading(true);
      
      // Fetch initial market data
      await fetchMarketData();
      
      // Fetch watchlist
      await fetchWatchlist();
      
      // Fetch portfolio
      await fetchPortfolio();
      
      // Fetch orders
      await fetchOrders();
      
    } catch (error) {
      console.error('Dashboard initialization failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchMarketData = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/market/overview');
      const data = await response.json();
      setMarketData(data);
    } catch (error) {
      console.error('Failed to fetch market data:', error);
    }
  };

  const fetchWatchlist = async () => {
    // Simulated watchlist data
    const watchlistData = popularSymbols.map(symbol => ({
      symbol,
      name: getCompanyName(symbol),
      current_price: Math.random() * 1000 + 100,
      change: (Math.random() - 0.5) * 20,
      change_percent: (Math.random() - 0.5) * 5,
      volume: Math.floor(Math.random() * 1000000)
    }));
    setWatchlist(watchlistData);
  };

  const fetchPortfolio = async () => {
    // Simulated portfolio data
    const portfolioData = [
      { symbol: 'AAPL', quantity: 100, avg_price: 150, current_price: 180, pnl: 3000 },
      { symbol: 'GOOGL', quantity: 50, avg_price: 2800, current_price: 3000, pnl: 10000 },
      { symbol: 'MSFT', quantity: 75, avg_price: 300, current_price: 350, pnl: 3750 }
    ];
    setPortfolio(portfolioData);
  };

  const fetchOrders = async () => {
    // Simulated orders data
    const ordersData = [
      { id: '1', symbol: 'AAPL', side: 'BUY', quantity: 100, price: 180, status: 'FILLED', timestamp: '2024-01-01T10:00:00Z' },
      { id: '2', symbol: 'GOOGL', side: 'SELL', quantity: 50, price: 3000, status: 'PENDING', timestamp: '2024-01-01T09:30:00Z' }
    ];
    setOrders(ordersData);
  };

  const setupRealTimeUpdates = () => {
    // Poll for real-time updates every 2 seconds
    dataUpdateInterval.current = setInterval(async () => {
      try {
        await fetchMarketData();
        await updateWatchlistPrices();
      } catch (error) {
        console.error('Real-time update failed:', error);
      }
    }, 2000);
  };

  const updateWatchlistPrices = async () => {
    const updatedWatchlist = watchlist.map(item => ({
      ...item,
      current_price: item.current_price + (Math.random() - 0.5) * 2,
      change: (Math.random() - 0.5) * 1,
      change_percent: (Math.random() - 0.5) * 0.5
    }));
    setWatchlist(updatedWatchlist);
  };

  const getCompanyName = (symbol) => {
    const names = {
      'AAPL': 'Apple Inc.',
      'GOOGL': 'Alphabet Inc.',
      'MSFT': 'Microsoft Corporation',
      'TSLA': 'Tesla Inc.',
      'AMZN': 'Amazon.com Inc.',
      'META': 'Meta Platforms Inc.',
      'NVDA': 'NVIDIA Corporation',
      'NFLX': 'Netflix Inc.',
      'JPM': 'JPMorgan Chase & Co.',
      'JNJ': 'Johnson & Johnson'
    };
    return names[symbol] || symbol;
  };

  const handleOrderSubmit = async () => {
    try {
      setIsLoading(true);
      
      const orderData = {
        ...orderForm,
        symbol: selectedSymbol,
        timestamp: new Date().toISOString(),
        id: `ORDER_${Date.now()}`
      };

      // Add to orders list
      setOrders(prev => [orderData, ...prev]);
      
      // Reset form
      setOrderForm({
        type: 'MARKET',
        side: 'BUY',
        quantity: 100,
        price: 0,
        validity: 'DAY'
      });

      alert('Order submitted successfully!');
    } catch (error) {
      console.error('Order submission failed:', error);
      alert('Order submission failed!');
    } finally {
      setIsLoading(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(price);
  };

  const formatChange = (change, changePercent) => {
    const isPositive = change >= 0;
    const sign = isPositive ? '+' : '';
    return (
      <span className={`price-change ${isPositive ? 'positive' : 'negative'}`}>
        {sign}{formatPrice(change)} ({sign}{changePercent.toFixed(2)}%)
      </span>
    );
  };

  return (
    <div className="advanced-trading-dashboard">
      {/* Header with Market Overview */}
      <div className="dashboard-header">
        <div className="market-summary">
          <h1>VittCott Trading Platform</h1>
          <div className="market-indicators">
            <div className="indicator">
              <span className="label">Market Status:</span>
              <span className="status open">OPEN</span>
            </div>
            <div className="indicator">
              <span className="label">Last Updated:</span>
              <span className="time">{new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
        <div className="user-info">
          <span className="username">Welcome, Trader</span>
          <span className="balance">Balance: $50,000.00</span>
        </div>
      </div>

      <div className="dashboard-content">
        {/* Left Panel - Watchlist & Portfolio */}
        <div className="left-panel">
          {/* Watchlist */}
          <div className="watchlist-section">
            <h3>Watchlist</h3>
            <div className="watchlist-items">
              {watchlist.map((item) => (
                <div
                  key={item.symbol}
                  className={`watchlist-item ${selectedSymbol === item.symbol ? 'selected' : ''}`}
                  onClick={() => setSelectedSymbol(item.symbol)}
                >
                  <div className="symbol-info">
                    <span className="symbol">{item.symbol}</span>
                    <span className="name">{item.name}</span>
                  </div>
                  <div className="price-info">
                    <span className="current-price">{formatPrice(item.current_price)}</span>
                    {formatChange(item.change, item.change_percent)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Portfolio */}
          <div className="portfolio-section">
            <h3>Portfolio</h3>
            <div className="portfolio-summary">
              <div className="summary-item">
                <span className="label">Total Value:</span>
                <span className="value">$125,750.00</span>
              </div>
              <div className="summary-item">
                <span className="label">Total P&L:</span>
                <span className="value positive">+$16,750.00</span>
              </div>
            </div>
            <div className="portfolio-holdings">
              {portfolio.map((holding) => (
                <div key={holding.symbol} className="holding-item">
                  <div className="holding-symbol">{holding.symbol}</div>
                  <div className="holding-details">
                    <span>Qty: {holding.quantity}</span>
                    <span>Avg: {formatPrice(holding.avg_price)}</span>
                    <span className="pnl positive">+{formatPrice(holding.pnl)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Center Panel - Chart & Trading */}
        <div className="center-panel">
          {/* Symbol Header */}
          <div className="symbol-header">
            <div className="symbol-info">
              <h2>{selectedSymbol}</h2>
              <span className="company-name">{getCompanyName(selectedSymbol)}</span>
            </div>
            <div className="price-display">
              <span className="current-price-large">
                {formatPrice(watchlist.find(item => item.symbol === selectedSymbol)?.current_price || 0)}
              </span>
              {(() => {
                const item = watchlist.find(item => item.symbol === selectedSymbol);
                return item ? formatChange(item.change, item.change_percent) : null;
              })()}
            </div>
          </div>

          {/* Chart Area */}
          <div className="chart-container">
            <div className="chart-header">
              <div className="timeframe-selector">
                <button className="timeframe active">1D</button>
                <button className="timeframe">1W</button>
                <button className="timeframe">1M</button>
                <button className="timeframe">3M</button>
                <button className="timeframe">1Y</button>
              </div>
              <div className="chart-controls">
                <button className="chart-btn">📊</button>
                <button className="chart-btn">📈</button>
                <button className="chart-btn">📉</button>
              </div>
            </div>
            <div className="chart-placeholder">
              <h3>Real-time Chart Coming Soon</h3>
              <p>Interactive price charts with technical indicators</p>
              <div className="chart-mock">
                <div className="price-line"></div>
                <div className="volume-bars"></div>
              </div>
            </div>
          </div>

          {/* Trading Form */}
          <div className="trading-form">
            <h3>Place Order</h3>
            <div className="form-grid">
              <div className="form-group">
                <label>Order Type</label>
                <select
                  value={orderForm.type}
                  onChange={(e) => setOrderForm({...orderForm, type: e.target.value})}
                >
                  <option value="MARKET">Market</option>
                  <option value="LIMIT">Limit</option>
                  <option value="STOP">Stop</option>
                </select>
              </div>
              <div className="form-group">
                <label>Side</label>
                <select
                  value={orderForm.side}
                  onChange={(e) => setOrderForm({...orderForm, side: e.target.value})}
                >
                  <option value="BUY">Buy</option>
                  <option value="SELL">Sell</option>
                </select>
              </div>
              <div className="form-group">
                <label>Quantity</label>
                <input
                  type="number"
                  value={orderForm.quantity}
                  onChange={(e) => setOrderForm({...orderForm, quantity: parseInt(e.target.value)})}
                  min="1"
                />
              </div>
              {orderForm.type !== 'MARKET' && (
                <div className="form-group">
                  <label>Price</label>
                  <input
                    type="number"
                    value={orderForm.price}
                    onChange={(e) => setOrderForm({...orderForm, price: parseFloat(e.target.value)})}
                    step="0.01"
                    min="0"
                  />
                </div>
              )}
              <div className="form-group">
                <label>Validity</label>
                <select
                  value={orderForm.validity}
                  onChange={(e) => setOrderForm({...orderForm, validity: e.target.value})}
                >
                  <option value="DAY">Day</option>
                  <option value="GTC">Good Till Cancelled</option>
                  <option value="IOC">Immediate or Cancel</option>
                </select>
              </div>
            </div>
            <button
              className={`submit-order ${orderForm.side.toLowerCase()}`}
              onClick={handleOrderSubmit}
              disabled={isLoading}
            >
              {isLoading ? 'Submitting...' : `${orderForm.side} ${selectedSymbol}`}
            </button>
          </div>
        </div>

        {/* Right Panel - Market Depth & Orders */}
        <div className="right-panel">
          {/* Market Depth */}
          <div className="market-depth">
            <h3>Market Depth</h3>
            <div className="depth-container">
              <div className="asks">
                <h4>Asks (Sell)</h4>
                <div className="depth-rows">
                  {[3, 2, 1].map((level) => (
                    <div key={level} className="depth-row ask">
                      <span className="price">$180.50</span>
                      <span className="quantity">1,200</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="spread">
                <span>Spread: $0.05</span>
              </div>
              <div className="bids">
                <h4>Bids (Buy)</h4>
                <div className="depth-rows">
                  {[1, 2, 3].map((level) => (
                    <div key={level} className="depth-row bid">
                      <span className="price">$180.45</span>
                      <span className="quantity">800</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Recent Orders */}
          <div className="recent-orders">
            <h3>Recent Orders</h3>
            <div className="orders-list">
              {orders.map((order) => (
                <div key={order.id} className="order-item">
                  <div className="order-symbol">{order.symbol}</div>
                  <div className={`order-side ${order.side.toLowerCase()}`}>
                    {order.side}
                  </div>
                  <div className="order-quantity">{order.quantity}</div>
                  <div className={`order-status ${order.status.toLowerCase()}`}>
                    {order.status}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="quick-actions">
            <h3>Quick Actions</h3>
            <div className="action-buttons">
              <button className="action-btn buy">Buy {selectedSymbol}</button>
              <button className="action-btn sell">Sell {selectedSymbol}</button>
              <button className="action-btn">Add to Watchlist</button>
              <button className="action-btn">View Details</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedTradingDashboard;
