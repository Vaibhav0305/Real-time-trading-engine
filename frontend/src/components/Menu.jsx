import React from 'react';
import './Menu.css';

const Menu = ({ activeSection, setActiveSection }) => {
  const menuItems = [
    { id: 'home', label: 'Home', icon: '🏠' },
    { id: 'watchlist', label: 'Watchlist', icon: '👁️' },
    { id: 'holdings', label: 'Holdings', icon: '📊' },
    { id: 'positions', label: 'Positions', icon: '📈' },
    { id: 'orders', label: 'Orders', icon: '📋' },
    { id: 'funds', label: 'Funds', icon: '💰' }
  ];

  return (
    <nav className="menu">
      <ul className="menu-list">
        {menuItems.map((item) => (
          <li key={item.id}>
            <button
              className={`menu-item ${activeSection === item.id ? 'active' : ''}`}
              onClick={() => setActiveSection(item.id)}
            >
              <span className="menu-icon">{item.icon}</span>
              <span className="menu-label">{item.label}</span>
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Menu;


