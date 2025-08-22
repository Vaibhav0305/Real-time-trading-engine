import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const [portfolioData, setPortfolioData] = useState({
    totalValue: 125000,
    dailyChange: 1250,
    dailyChangePercent: 1.01,
    positions: [
      { symbol: 'AAPL', quantity: 100, avgPrice: 150, currentPrice: 155, change: 5, changePercent: 3.33 },
      { symbol: 'TSLA', quantity: 50, avgPrice: 200, currentPrice: 210, change: 10, changePercent: 5.00 },
      { symbol: 'MSFT', quantity: 75, avgPrice: 300, currentPrice: 310, change: 10, changePercent: 3.33 }
    ]
  });
  
  const [marketData, setMarketData] = useState({
    indices: [
      { name: 'S&P 500', value: 4567.89, change: 12.34, changePercent: 0.27 },
      { name: 'NASDAQ', value: 14234.56, change: 45.67, changePercent: 0.32 },
      { name: 'DOW', value: 34567.89, change: 89.12, changePercent: 0.26 }
    ],
    trending: [
      { symbol: 'NVDA', name: 'NVIDIA Corp', price: 485.67, change: 15.23, changePercent: 3.24 },
      { symbol: 'AMD', name: 'Advanced Micro Devices', price: 123.45, change: 8.76, changePercent: 7.64 },
      { symbol: 'GOOGL', name: 'Alphabet Inc', price: 134.56, change: 2.34, changePercent: 1.77 }
    ]
  });
  
  const [recentActivity, setRecentActivity] = useState([
    { type: 'buy', symbol: 'AAPL', quantity: 25, price: 155.00, time: '2 hours ago' },
    { type: 'sell', symbol: 'TSLA', quantity: 10, price: 210.00, time: '4 hours ago' },
    { type: 'buy', symbol: 'MSFT', quantity: 15, price: 310.00, time: '6 hours ago' }
  ]);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatPercent = (percent) => {
    return `${percent > 0 ? '+' : ''}${percent.toFixed(2)}%`;
  };

  const getChangeColor = (change) => {
    return change >= 0 ? 'positive' : 'negative';
  };

  const getActivityIcon = (type) => {
    return type === 'buy' ? '📈' : '📉';
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="welcome-section">
          <h1>Welcome back, {user?.username || 'Trader'}! 👋</h1>
          <p>Here's what's happening with your portfolio today</p>
        </div>
        <div className="quick-actions">
          <button className="action-btn primary">
            <i className="fas fa-plus"></i>
            New Trade
          </button>
          <button className="action-btn secondary">
            <i className="fas fa-chart-line"></i>
            View Charts
          </button>
        </div>
      </div>

      {/* Portfolio Overview */}
      <div className="portfolio-overview">
        <div className="portfolio-card main">
          <div className="portfolio-header">
            <h2>Portfolio Value</h2>
            <span className="portfolio-change">
              <i className={`fas fa-arrow-${portfolioData.dailyChange >= 0 ? 'up' : 'down'}`}></i>
              {formatCurrency(portfolioData.dailyChange)} ({formatPercent(portfolioData.dailyChangePercent)})
            </span>
          </div>
          <div className="portfolio-value">
            {formatCurrency(portfolioData.totalValue)}
          </div>
          <div className="portfolio-stats">
            <div className="stat">
              <span className="stat-label">Total Positions</span>
              <span className="stat-value">{portfolioData.positions.length}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Today's P&L</span>
              <span className={`stat-value ${getChangeColor(portfolioData.dailyChange)}`}>
                {formatCurrency(portfolioData.dailyChange)}
              </span>
            </div>
          </div>
        </div>

        {/* Market Indices */}
        <div className="market-indices">
          {marketData.indices.map((index, idx) => (
            <div key={idx} className="index-card">
              <h3>{index.name}</h3>
              <div className="index-value">{index.value.toLocaleString()}</div>
              <div className={`index-change ${getChangeColor(index.change)}`}>
                {formatPercent(index.changePercent)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="dashboard-grid">
        {/* Positions */}
        <div className="dashboard-card positions">
          <div className="card-header">
            <h3>Your Positions</h3>
            <button className="view-all-btn">View All</button>
          </div>
          <div className="positions-list">
            {portfolioData.positions.map((position, idx) => (
              <div key={idx} className="position-item">
                <div className="position-info">
                  <div className="position-symbol">{position.symbol}</div>
                  <div className="position-details">
                    <span>{position.quantity} shares</span>
                    <span className="position-avg">Avg: {formatCurrency(position.avgPrice)}</span>
                  </div>
                </div>
                <div className="position-pricing">
                  <div className="position-current">{formatCurrency(position.currentPrice)}</div>
                  <div className={`position-change ${getChangeColor(position.change)}`}>
                    {formatCurrency(position.change)} ({formatPercent(position.changePercent)})
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Trending Stocks */}
        <div className="dashboard-card trending">
          <div className="card-header">
            <h3>Trending Today</h3>
            <button className="view-all-btn">View All</button>
          </div>
          <div className="trending-list">
            {marketData.trending.map((stock, idx) => (
              <div key={idx} className="trending-item">
                <div className="trending-info">
                  <div className="trending-symbol">{stock.symbol}</div>
                  <div className="trending-name">{stock.name}</div>
                </div>
                <div className="trending-pricing">
                  <div className="trending-price">{formatCurrency(stock.price)}</div>
                  <div className={`trending-change ${getChangeColor(stock.change)}`}>
                    {formatCurrency(stock.change)} ({formatPercent(stock.changePercent)})
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="dashboard-card activity">
          <div className="card-header">
            <h3>Recent Activity</h3>
            <button className="view-all-btn">View All</button>
          </div>
          <div className="activity-list">
            {recentActivity.map((activity, idx) => (
              <div key={idx} className="activity-item">
                <div className="activity-icon">
                  {getActivityIcon(activity.type)}
                </div>
                <div className="activity-details">
                  <div className="activity-action">
                    {activity.type.toUpperCase()} {activity.symbol}
                  </div>
                  <div className="activity-info">
                    {activity.quantity} shares @ {formatCurrency(activity.price)}
                  </div>
                  <div className="activity-time">{activity.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="dashboard-card quick-actions-card">
          <div className="card-header">
            <h3>Quick Actions</h3>
          </div>
          <div className="quick-actions-grid">
            <button className="quick-action-btn">
              <i className="fas fa-chart-bar"></i>
              <span>Market Analysis</span>
            </button>
            <button className="quick-action-btn">
              <i className="fas fa-robot"></i>
              <span>AI Chatbot</span>
            </button>
            <button className="quick-action-btn">
              <i className="fas fa-cog"></i>
              <span>Settings</span>
            </button>
            <button className="quick-action-btn">
              <i className="fas fa-question-circle"></i>
              <span>Help</span>
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Stats */}
      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-trophy"></i>
          </div>
          <div className="stat-content">
            <div className="stat-number">87.5%</div>
            <div className="stat-label">Win Rate</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-clock"></i>
          </div>
          <div className="stat-content">
            <div className="stat-number">24</div>
            <div className="stat-label">Active Strategies</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-chart-line"></i>
          </div>
          <div className="stat-content">
            <div className="stat-number">156</div>
            <div className="stat-label">Total Trades</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-dollar-sign"></i>
          </div>
          <div className="stat-content">
            <div className="stat-number">$12,450</div>
            <div className="stat-label">Total Profit</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
