import React from 'react';
import './Home.css';

const Home = ({ portfolio, stockData }) => {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatChange = (change, changePercent) => {
    const isPositive = change >= 0;
    const sign = isPositive ? '+' : '';
    return (
      <span className={`change ${isPositive ? 'positive' : 'negative'}`}>
        {sign}{formatCurrency(change)} ({sign}{changePercent.toFixed(2)}%)
      </span>
    );
  };

  return (
    <div className="home">
      <div className="welcome-section">
        <h2>Welcome to VittCott Trading Platform</h2>
        <p>Your professional trading dashboard</p>
      </div>

      <div className="portfolio-summary">
        <h3>Portfolio Summary</h3>
        <div className="summary-cards">
          <div className="summary-card">
            <h4>Total Value</h4>
            <p className="value">{formatCurrency(portfolio.totalValue)}</p>
          </div>
          <div className="summary-card">
            <h4>Total P&L</h4>
            <p className={`value ${portfolio.totalPnL >= 0 ? 'positive' : 'negative'}`}>
              {formatCurrency(portfolio.totalPnL)}
            </p>
          </div>
          <div className="summary-card">
            <h4>Holdings</h4>
            <p className="value">{portfolio.holdings.length}</p>
          </div>
        </div>
      </div>

      <div className="market-overview">
        <h3>Market Overview</h3>
        <div className="stock-grid">
          {stockData.slice(0, 4).map((stock) => (
            <div key={stock.symbol} className="stock-card">
              <div className="stock-header">
                <h4>{stock.symbol}</h4>
                <span className="stock-name">{stock.name}</span>
              </div>
              <div className="stock-price">
                <span className="current-price">{formatCurrency(stock.current_price)}</span>
                {formatChange(stock.change, stock.change_percent)}
              </div>
              <div className="stock-volume">
                Volume: {stock.volume.toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="action-buttons">
          <button className="action-btn buy">Buy Stock</button>
          <button className="action-btn sell">Sell Stock</button>
          <button className="action-btn">Add to Watchlist</button>
          <button className="action-btn">View Charts</button>
        </div>
      </div>
    </div>
  );
};

export default Home;


