import React, { useState, useEffect, useRef } from 'react';
import './AlgorithmicTradingDashboard.css';

const AlgorithmicTradingDashboard = () => {
  const [strategies, setStrategies] = useState([]);
  const [strategyTemplates, setStrategyTemplates] = useState([]);
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [isCreatingStrategy, setIsCreatingStrategy] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [wsConnection, setWsConnection] = useState(null);
  const [activeStrategies, setActiveStrategies] = useState([]);

  // Form state for creating/editing strategies
  const [strategyForm, setStrategyForm] = useState({
    name: '',
    strategy_type: 'moving_average_crossover',
    symbols: [],
    parameters: {},
    risk_limits: {
      max_position_risk: 0.02,
      max_position_size: 1000,
      max_risk_per_trade: 1000
    },
    enabled: true
  });

  // Backtesting state
  const [backtestData, setBacktestData] = useState({
    start_date: '',
    end_date: '',
    historical_data: {}
  });
  const [backtestResults, setBacktestResults] = useState(null);

  const wsRef = useRef(null);

  useEffect(() => {
    initializeDashboard();
    setupWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const initializeDashboard = async () => {
    try {
      setIsLoading(true);
      
      // Fetch strategies
      await fetchStrategies();
      
      // Fetch strategy templates
      await fetchStrategyTemplates();
      
    } catch (error) {
      console.error('Dashboard initialization failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const setupWebSocket = () => {
    const ws = new WebSocket(`ws://127.0.0.1:8000/api/v1/algo/ws/strategy-updates/user123`);
    
    ws.onopen = () => {
      console.log('Algo trading WebSocket connected');
      setWsConnection(ws);
      
      // Request initial strategies
      ws.send(JSON.stringify({ type: 'get_strategies' }));
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'strategies_update') {
        setStrategies(data.strategies);
        updateActiveStrategies(data.strategies);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnection(null);
    };
    
    wsRef.current = ws;
  };

  const fetchStrategies = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/algo/strategies');
      const data = await response.json();
      setStrategies(data.strategies);
      updateActiveStrategies(data.strategies);
    } catch (error) {
      console.error('Failed to fetch strategies:', error);
    }
  };

  const fetchStrategyTemplates = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/algo/strategy-templates');
      const data = await response.json();
      setStrategyTemplates(data.templates);
    } catch (error) {
      console.error('Failed to fetch strategy templates:', error);
    }
  };

  const updateActiveStrategies = (strategiesList) => {
    const active = strategiesList.filter(s => s.status === 'active');
    setActiveStrategies(active);
  };

  const handleCreateStrategy = async () => {
    try {
      setIsLoading(true);
      
      const response = await fetch('http://127.0.0.1:8000/api/v1/algo/strategies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(strategyForm),
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Strategy created:', result);
        
        // Refresh strategies list
        await fetchStrategies();
        
        // Reset form and close modal
        setStrategyForm({
          name: '',
          strategy_type: 'moving_average_crossover',
          symbols: [],
          parameters: {},
          risk_limits: {
            max_position_risk: 0.02,
            max_position_size: 1000,
            max_risk_per_trade: 1000
          },
          enabled: true
        });
        setIsCreatingStrategy(false);
      } else {
        console.error('Failed to create strategy');
      }
    } catch (error) {
      console.error('Error creating strategy:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartStrategy = async (strategyId) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/v1/algo/strategies/${strategyId}/start`, {
        method: 'POST',
      });
      
      if (response.ok) {
        await fetchStrategies();
      }
    } catch (error) {
      console.error('Error starting strategy:', error);
    }
  };

  const handleStopStrategy = async (strategyId) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/v1/algo/strategies/${strategyId}/stop`, {
        method: 'POST',
      });
      
      if (response.ok) {
        await fetchStrategies();
      }
    } catch (error) {
      console.error('Error stopping strategy:', error);
    }
  };

  const handleDeleteStrategy = async (strategyId) => {
    if (window.confirm('Are you sure you want to delete this strategy?')) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/v1/algo/strategies/${strategyId}`, {
          method: 'DELETE',
        });
        
        if (response.ok) {
          await fetchStrategies();
        }
      } catch (error) {
        console.error('Error deleting strategy:', error);
      }
    }
  };

  const handleBacktest = async (strategyId) => {
    try {
      setIsLoading(true);
      
      const response = await fetch(`http://127.0.0.1:8000/api/v1/algo/strategies/${strategyId}/backtest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backtestData),
      });
      
      if (response.ok) {
        const result = await response.json();
        setBacktestResults(result.backtest_result);
      }
    } catch (error) {
      console.error('Error running backtest:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadTemplate = (template) => {
    setStrategyForm({
      name: template.name,
      strategy_type: template.type,
      symbols: ['AAPL', 'GOOGL', 'MSFT'], // Default symbols
      parameters: template.default_parameters,
      risk_limits: template.default_risk_limits,
      enabled: true
    });
    setIsCreatingStrategy(true);
  };

  const updateStrategyForm = (field, value) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setStrategyForm(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value
        }
      }));
    } else {
      setStrategyForm(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const renderStrategyCard = (strategy) => (
    <div key={strategy.strategy_id} className="strategy-card">
      <div className="strategy-header">
        <h3>{strategy.name}</h3>
        <span className={`status-badge ${strategy.status}`}>
          {strategy.status.toUpperCase()}
        </span>
      </div>
      
      <div className="strategy-details">
        <p><strong>Type:</strong> {strategy.strategy_type}</p>
        <p><strong>Symbols:</strong> {strategy.symbols?.join(', ') || 'N/A'}</p>
        <p><strong>Positions:</strong> {Object.keys(strategy.current_positions || {}).length}</p>
        <p><strong>Trades:</strong> {strategy.trade_count || 0}</p>
      </div>
      
      <div className="strategy-actions">
        {strategy.status === 'active' ? (
          <button 
            onClick={() => handleStopStrategy(strategy.strategy_id)}
            className="btn btn-warning"
          >
            Stop
          </button>
        ) : (
          <button 
            onClick={() => handleStartStrategy(strategy.strategy_id)}
            className="btn btn-success"
          >
            Start
          </button>
        )}
        
        <button 
          onClick={() => setSelectedStrategy(strategy)}
          className="btn btn-info"
        >
          View
        </button>
        
        <button 
          onClick={() => handleDeleteStrategy(strategy.strategy_id)}
          className="btn btn-danger"
        >
          Delete
        </button>
      </div>
    </div>
  );

  const renderCreateStrategyModal = () => (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Create New Strategy</h2>
          <button 
            onClick={() => setIsCreatingStrategy(false)}
            className="close-btn"
          >
            ×
          </button>
        </div>
        
        <div className="modal-body">
          <div className="form-group">
            <label>Strategy Name</label>
            <input
              type="text"
              value={strategyForm.name}
              onChange={(e) => updateStrategyForm('name', e.target.value)}
              placeholder="Enter strategy name"
            />
          </div>
          
          <div className="form-group">
            <label>Strategy Type</label>
            <select
              value={strategyForm.strategy_type}
              onChange={(e) => updateStrategyForm('strategy_type', e.target.value)}
            >
              <option value="moving_average_crossover">Moving Average Crossover</option>
              <option value="mean_reversion">Mean Reversion</option>
              <option value="momentum">Momentum</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>Symbols (comma-separated)</label>
            <input
              type="text"
              value={strategyForm.symbols.join(', ')}
              onChange={(e) => updateStrategyForm('symbols', e.target.value.split(',').map(s => s.trim()))}
              placeholder="AAPL, GOOGL, MSFT"
            />
          </div>
          
          <div className="form-group">
            <label>Max Position Risk (%)</label>
            <input
              type="number"
              step="0.01"
              value={strategyForm.risk_limits.max_position_risk * 100}
              onChange={(e) => updateStrategyForm('risk_limits.max_position_risk', parseFloat(e.target.value) / 100)}
            />
          </div>
          
          <div className="form-group">
            <label>Max Position Size</label>
            <input
              type="number"
              value={strategyForm.risk_limits.max_position_size}
              onChange={(e) => updateStrategyForm('risk_limits.max_position_size', parseInt(e.target.value))}
            />
          </div>
        </div>
        
        <div className="modal-footer">
          <button 
            onClick={() => setIsCreatingStrategy(false)}
            className="btn btn-secondary"
          >
            Cancel
          </button>
          <button 
            onClick={handleCreateStrategy}
            className="btn btn-primary"
            disabled={isLoading}
          >
            {isLoading ? 'Creating...' : 'Create Strategy'}
          </button>
        </div>
      </div>
    </div>
  );

  const renderBacktestModal = () => (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Backtest Strategy</h2>
          <button 
            onClick={() => setSelectedStrategy(null)}
            className="close-btn"
          >
            ×
          </button>
        </div>
        
        <div className="modal-body">
          <div className="form-group">
            <label>Start Date</label>
            <input
              type="date"
              value={backtestData.start_date}
              onChange={(e) => setBacktestData(prev => ({...prev, start_date: e.target.value}))}
            />
          </div>
          
          <div className="form-group">
            <label>End Date</label>
            <input
              type="date"
              value={backtestData.end_date}
              onChange={(e) => setBacktestData(prev => ({...prev, end_date: e.target.value}))}
            />
          </div>
          
          {backtestResults && (
            <div className="backtest-results">
              <h3>Backtest Results</h3>
              <div className="results-grid">
                <div className="result-item">
                  <span className="label">Total Return:</span>
                  <span className={`value ${backtestResults.total_return >= 0 ? 'positive' : 'negative'}`}>
                    {(backtestResults.total_return * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="result-item">
                  <span className="label">Win Rate:</span>
                  <span className="value">{(backtestResults.win_rate * 100).toFixed(1)}%</span>
                </div>
                <div className="result-item">
                  <span className="label">Total Trades:</span>
                  <span className="value">{backtestResults.total_trades}</span>
                </div>
                <div className="result-item">
                  <span className="label">Sharpe Ratio:</span>
                  <span className="value">{backtestResults.sharpe_ratio.toFixed(2)}</span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="modal-footer">
          <button 
            onClick={() => setSelectedStrategy(null)}
            className="btn btn-secondary"
          >
            Close
          </button>
          <button 
            onClick={() => handleBacktest(selectedStrategy.strategy_id)}
            className="btn btn-primary"
            disabled={isLoading}
          >
            {isLoading ? 'Running...' : 'Run Backtest'}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="algo-trading-dashboard">
      <div className="dashboard-header">
        <h1>Algorithmic Trading Dashboard</h1>
        <div className="header-actions">
          <button 
            onClick={() => setIsCreatingStrategy(true)}
            className="btn btn-primary"
          >
            Create Strategy
          </button>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="left-panel">
          <div className="panel-section">
            <h2>Strategy Templates</h2>
            <div className="templates-grid">
              {strategyTemplates.map(template => (
                <div key={template.type} className="template-card">
                  <h3>{template.name}</h3>
                  <p>{template.description}</p>
                  <button 
                    onClick={() => loadTemplate(template)}
                    className="btn btn-outline"
                  >
                    Use Template
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="panel-section">
            <h2>Active Strategies ({activeStrategies.length})</h2>
            <div className="active-strategies">
              {activeStrategies.map(strategy => (
                <div key={strategy.strategy_id} className="active-strategy-item">
                  <span className="strategy-name">{strategy.name}</span>
                  <span className="strategy-status active">ACTIVE</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="main-panel">
          <div className="panel-section">
            <h2>Your Strategies ({strategies.length})</h2>
            {strategies.length === 0 ? (
              <div className="empty-state">
                <p>No strategies created yet. Create your first strategy to get started!</p>
              </div>
            ) : (
              <div className="strategies-grid">
                {strategies.map(renderStrategyCard)}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      {isCreatingStrategy && renderCreateStrategyModal()}
      {selectedStrategy && renderBacktestModal()}
    </div>
  );
};

export default AlgorithmicTradingDashboard;
