import React from 'react';
import './WatchList.css';

const WatchList = ({ stockData }) => {
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
    <div className="watchlist">
      <h2>Watchlist</h2>
      <div className="watchlist-table">
        <div className="table-header">
          <div className="header-cell">Symbol</div>
          <div className="header-cell">Name</div>
          <div className="header-cell">Price</div>
          <div className="header-cell">Change</div>
          <div className="header-cell">Volume</div>
          <div className="header-cell">Actions</div>
        </div>
        {stockData.map((stock) => (
          <div key={stock.symbol} className="table-row">
            <div className="cell symbol">{stock.symbol}</div>
            <div className="cell name">{stock.name}</div>
            <div className="cell price">{formatCurrency(stock.current_price)}</div>
            <div className="cell change">{formatChange(stock.change, stock.change_percent)}</div>
            <div className="cell volume">{stock.volume.toLocaleString()}</div>
            <div className="cell actions">
              <button className="action-btn buy">Buy</button>
              <button className="action-btn sell">Sell</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WatchList;


