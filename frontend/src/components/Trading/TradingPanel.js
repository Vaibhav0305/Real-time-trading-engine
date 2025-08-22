import React, { useState, useEffect, useRef } from 'react';
import './TradingPanel.css';

const TradingPanel = () => {
  const [marketData, setMarketData] = useState({});
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [marketOverview, setMarketOverview] = useState({});
  const [watchlist, setWatchlist] = useState([]);
  const [orderType, setOrderType] = useState('MARKET');
  const [quantity, setQuantity] = useState(100);
  const [price, setPrice] = useState(0);
  const [orderSide, setOrderSide] = useState('BUY');
  const [isLoading, setIsLoading] = useState(false);

  const wsRef = useRef(null);
  const priceUpdateInterval = useRef(null);

  // Popular symbols for quick access
  const popularSymbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA', 'NFLX'];

  useEffect(() => {
    fetchInitialData();
    setupWebSocket();
    setupPriceUpdates();

    return () => {
      if (wsRef.current) wsRef.current.close();
      if (priceUpdateInterval.current) clearInterval(priceUpdateInterval.current);
    };
  }, []);

  const fetchInitialData = async () => {
    try {
      setIsLoading(true);
      
      // Fetch market overview
      const overviewResponse = await fetch('/api/v1/market/overview');
      const overview = await overviewResponse.json();
      setMarketOverview(overview);

      // Fetch watchlist
      const watchlistResponse = await fetch('/api/v1/market/watchlist');
      const watchlistData = await watchlistResponse.json();
      setWatchlist(watchlistData.watchlist);

      // Fetch initial symbol data
      if (selectedSymbol) {
        const priceResponse = await fetch(`/api/v1/market/price/${selectedSymbol}`);
        const priceData = await priceResponse.json();
        setMarketData(prev => ({ ...prev, [selectedSymbol]: priceData }));
      }
    } catch (error) {
      console.error('Error fetching initial data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const setupWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8000/api/v1/market/ws/market-data');
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      // Subscribe to selected symbol
      ws.send(JSON.stringify({ action: 'subscribe', symbol: selectedSymbol }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'price_update') {
          setMarketData(prev => ({ ...prev, [data.symbol]: data.data }));
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    wsRef.current = ws;
  };

  const setupPriceUpdates = () => {
    // Poll for price updates every 2 seconds
    priceUpdateInterval.current = setInterval(async () => {
      try {
        const symbols = [...popularSymbols, selectedSymbol];
        const response = await fetch(`/api/v1/market/prices?symbols=${symbols.join(',')}`);
        const data = await response.json();
        
        setMarketData(prev => ({ ...prev, ...data.prices }));
      } catch (error) {
        console.error('Error updating prices:', error);
      }
    }, 2000);
  };

  const handleSearch = async (query) => {
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }

    try {
      const response = await fetch(`/api/v1/market/search?query=${encodeURIComponent(query)}`);
      const data = await response.json();
      setSearchResults(data.results);
    } catch (error) {
      console.error('Error searching symbols:', error);
    }
  };

  const handleSymbolSelect = (symbol) => {
    setSelectedSymbol(symbol);
    setSearchQuery('');
    setSearchResults([]);
    
    // Subscribe to new symbol in WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'subscribe', symbol }));
    }
  };

  const handleOrderSubmit = async () => {
    try {
    setIsLoading(true);

      const orderData = {
        symbol: selectedSymbol,
        side: orderSide,
        type: orderType,
        quantity: parseInt(quantity),
        price: orderType === 'LIMIT' ? parseFloat(price) : null,
        timestamp: new Date().toISOString()
      };

      // Here you would send the order to your trading engine
      console.log('Submitting order:', orderData);
      
      // Simulate order submission
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      alert('Order submitted successfully!');
    } catch (error) {
      console.error('Error submitting order:', error);
      alert('Error submitting order');
    } finally {
      setIsLoading(false);
    }
  };

  const getCurrentPrice = (symbol) => {
    return marketData[symbol]?.current_price || 0;
  };

  const getPriceChange = (symbol) => {
    const data = marketData[symbol];
    if (!data) return { change: 0, changePercent: 0 };
    return { change: data.change || 0, changePercent: data.change_percent || 0 };
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
    <div className="trading-panel">
      {/* Header with Market Overview */}
      <div className="market-header">
        <div className="market-indices">
          {Object.entries(marketOverview.indices || {}).map(([key, index]) => (
            <div key={key} className="index-item">
              <span className="index-name">{index.name}</span>
              <span className="index-price">{formatPrice(index.current)}</span>
              <span className={`index-change ${index.change >= 0 ? 'positive' : 'negative'}`}>
                {index.change >= 0 ? '+' : ''}{index.change.toFixed(2)} ({index.changePercent.toFixed(2)}%)
              </span>
            </div>
          ))}
        </div>
        <div className="market-status">
          <span className={`status-indicator ${marketOverview.market_status === 'Open' ? 'open' : 'closed'}`}>
            {marketOverview.market_status}
          </span>
        </div>
      </div>

      <div className="trading-content">
        {/* Left Panel - Watchlist and Search */}
        <div className="left-panel">
          {/* Search */}
          <div className="search-section">
            <input
              type="text"
              placeholder="Search stocks, ETFs, indices..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                handleSearch(e.target.value);
              }}
              className="search-input"
            />
            {searchResults.length > 0 && (
              <div className="search-results">
                {searchResults.map((result) => (
                  <div
                    key={result.symbol}
                    className="search-result-item"
                    onClick={() => handleSymbolSelect(result.symbol)}
                  >
                    <span className="symbol">{result.symbol}</span>
                    <span className="name">{result.name}</span>
                    <span className="exchange">{result.exchange}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Watchlist */}
          <div className="watchlist-section">
            <h3>Watchlist</h3>
            <div className="watchlist-items">
              {watchlist.map((item) => (
                <div
                  key={item.symbol}
                  className={`watchlist-item ${selectedSymbol === item.symbol ? 'selected' : ''}`}
                  onClick={() => handleSymbolSelect(item.symbol)}
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
        </div>

        {/* Center Panel - Chart and Trading */}
        <div className="center-panel">
          {/* Symbol Header */}
          <div className="symbol-header">
            <div className="symbol-info">
              <h2>{selectedSymbol}</h2>
              <span className="company-name">
                {marketData[selectedSymbol]?.name || 'Loading...'}
              </span>
            </div>
            <div className="price-display">
              <span className="current-price-large">
                {formatPrice(getCurrentPrice(selectedSymbol))}
              </span>
              {formatChange(
                getPriceChange(selectedSymbol).change,
                getPriceChange(selectedSymbol).changePercent
              )}
            </div>
          </div>

          {/* Chart Placeholder */}
          <div className="chart-container">
            <div className="chart-placeholder">
              <h3>Chart Coming Soon</h3>
              <p>Real-time price charts will be integrated here</p>
            </div>
          </div>

          {/* Trading Form */}
          <div className="trading-form">
            <h3>Place Order</h3>
            <div className="form-row">
              <div className="form-group">
                <label>Order Type</label>
                <select
                  value={orderType}
                  onChange={(e) => setOrderType(e.target.value)}
                  className="form-select"
                >
                  <option value="MARKET">Market</option>
                  <option value="LIMIT">Limit</option>
                </select>
              </div>
              <div className="form-group">
                <label>Side</label>
                <select
                  value={orderSide}
                  onChange={(e) => setOrderSide(e.target.value)}
                  className="form-select"
                >
                  <option value="BUY">Buy</option>
                  <option value="SELL">Sell</option>
                </select>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Quantity</label>
                <input
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                  className="form-input"
                  min="1"
                />
              </div>
              {orderType === 'LIMIT' && (
                <div className="form-group">
                  <label>Price</label>
                  <input
                type="number"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                    className="form-input"
                    step="0.01"
                    min="0"
                  />
                </div>
              )}
            </div>
            <button
              onClick={handleOrderSubmit}
                  disabled={isLoading}
              className={`submit-button ${orderSide.toLowerCase()}`}
            >
              {isLoading ? 'Submitting...' : `${orderSide} ${selectedSymbol}`}
            </button>
          </div>
        </div>

        {/* Right Panel - Market Depth and Orders */}
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
                      <span className="price">$0.00</span>
                      <span className="quantity">0</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="spread">
                <span>Spread: $0.00</span>
              </div>
              <div className="bids">
                <h4>Bids (Buy)</h4>
                <div className="depth-rows">
                  {[1, 2, 3].map((level) => (
                    <div key={level} className="depth-row bid">
                      <span className="price">$0.00</span>
                      <span className="quantity">0</span>
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
              <div className="order-item">
                <span className="order-symbol">AAPL</span>
                <span className="order-side buy">BUY</span>
                <span className="order-quantity">100</span>
                <span className="order-status filled">Filled</span>
              </div>
              <div className="order-item">
                <span className="order-symbol">GOOGL</span>
                <span className="order-side sell">SELL</span>
                <span className="order-quantity">50</span>
                <span className="order-status pending">Pending</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingPanel;
