import React from 'react';
import './TopBar.css';

const TopBar = () => {
  return (
    <div className="top-bar">
      <div className="logo">
        <h1>VittCott</h1>
        <span className="tagline">Trading Platform</span>
      </div>
      <div className="market-status">
        <span className="status-indicator open"></span>
        <span className="status-text">Market Open</span>
        <span className="time">{new Date().toLocaleTimeString()}</span>
      </div>
      <div className="user-info">
        <span className="username">Welcome, Trader</span>
        <span className="balance">Balance: $50,000.00</span>
      </div>
    </div>
  );
};

export default TopBar;


