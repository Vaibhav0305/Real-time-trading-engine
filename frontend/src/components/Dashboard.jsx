import React, { useState, useEffect } from 'react';
import TopBar from './TopBar';
import Menu from './Menu';
import Home from './Home';
import Orders from './Orders';
import Holdings from './Holdings';
import Positions from './Positions';
import Funds from './Funds';
import WatchList from './WatchList';
import './Dashboard.css';

const Dashboard = () => {
  const [activeSection, setActiveSection] = useState('home');
  const [stockData, setStockData] = useState([]);
  const [portfolio, setPortfolio] = useState({
    totalValue: 0,
    totalPnL: 0,
    holdings: []
  });

  useEffect(() => {
    // Fetch initial data
    fetchStockData();
    fetchPortfolioData();
  }, []);

  const fetchStockData = async () => {
    try {
      const response = await fetch('/api/v1/watchlist');
      if (response.ok) {
        const data = await response.json();
        setStockData(data.data || []);
      }
    } catch (error) {
      console.error('Failed to fetch stock data:', error);
      // Use mock data if API fails
      setStockData([
        { symbol: 'AAPL', name: 'Apple Inc.', current_price: 180.50, change: 2.50, change_percent: 1.40, volume: 5000000 },
        { symbol: 'GOOGL', name: 'Alphabet Inc.', current_price: 3000.00, change: -15.00, change_percent: -0.50, volume: 3000000 },
        { symbol: 'MSFT', name: 'Microsoft Corporation', current_price: 350.00, change: 5.00, change_percent: 1.45, volume: 4000000 },
        { symbol: 'TSLA', name: 'Tesla Inc.', current_price: 250.00, change: 10.00, change_percent: 4.17, volume: 8000000 }
      ]);
    }
  };

  const fetchPortfolioData = async () => {
    try {
      const response = await fetch('/api/v1/portfolio/overview');
      if (response.ok) {
        const data = await response.json();
        setPortfolio(data.data || { totalValue: 0, totalPnL: 0, holdings: [] });
      }
    } catch (error) {
      console.error('Failed to fetch portfolio data:', error);
      // Use mock data if API fails
      setPortfolio({
        totalValue: 125750.00,
        totalPnL: 16750.00,
        holdings: [
          { symbol: 'AAPL', quantity: 100, avg_price: 150.00, current_price: 180.50, pnl: 3050.00 },
          { symbol: 'GOOGL', quantity: 50, avg_price: 2800.00, current_price: 3000.00, pnl: 10000.00 },
          { symbol: 'MSFT', quantity: 75, avg_price: 300.00, current_price: 350.00, pnl: 3750.00 }
        ]
      });
    }
  };

  const renderActiveSection = () => {
    switch (activeSection) {
      case 'home':
        return <Home portfolio={portfolio} stockData={stockData} />;
      case 'orders':
        return <Orders />;
      case 'holdings':
        return <Holdings portfolio={portfolio} />;
      case 'positions':
        return <Positions />;
      case 'funds':
        return <Funds />;
      case 'watchlist':
        return <WatchList stockData={stockData} />;
      default:
        return <Home portfolio={portfolio} stockData={stockData} />;
    }
  };

  return (
    <div className="dashboard">
      <TopBar />
      <div className="dashboard-content">
        <Menu activeSection={activeSection} setActiveSection={setActiveSection} />
        <main className="main-content">
          {renderActiveSection()}
        </main>
      </div>
    </div>
  );
};

export default Dashboard;


