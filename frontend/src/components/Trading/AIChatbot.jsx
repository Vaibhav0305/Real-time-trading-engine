import React, { useState, useEffect, useRef } from 'react';
import './AIChatbot.css';

const AIChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [wsConnection, setWsConnection] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [showHelp, setShowHelp] = useState(false);
  const [suggestedActions, setSuggestedActions] = useState([]);

  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);
  const userId = 'user123'; // In production, get from auth context

  useEffect(() => {
    initializeChatbot();
    setupWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeChatbot = async () => {
    try {
      // Load chat history
      await loadChatHistory();
      
      // Add welcome message
      addBotMessage(
        "Hello! I'm your AI trading assistant. I can help you with market analysis, trading strategies, portfolio advice, risk management, and technical analysis. How can I assist you today?",
        'greeting',
        ['Ask about market conditions', 'Get strategy recommendations', 'Learn about risk management']
      );
      
    } catch (error) {
      console.error('Failed to initialize chatbot:', error);
    }
  };

  const setupWebSocket = () => {
    const ws = new WebSocket(`ws://127.0.0.1:8000/api/v1/chatbot/ws/chat/${userId}`);
    
    ws.onopen = () => {
      console.log('Chatbot WebSocket connected');
      setWsConnection(ws);
      
      // Request chat history
      ws.send(JSON.stringify({ type: 'get_history' }));
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'chat_response') {
        addBotMessage(
          data.response.content,
          data.response.intent,
          data.response.suggested_actions,
          data.response.metadata
        );
      } else if (data.type === 'chat_history') {
        setChatHistory(data.history);
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

  const loadChatHistory = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/chatbot/chat/history/${userId}`);
      if (response.ok) {
        const data = await response.json();
        setChatHistory(data.history);
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    
    // Add user message to chat
    addUserMessage(userMessage);
    
    // Send message through WebSocket if available
    if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
      wsConnection.send(JSON.stringify({
        type: 'chat_message',
        content: userMessage
      }));
    } else {
      // Fallback to HTTP API
      await sendMessageViaAPI(userMessage);
    }
  };

  const sendMessageViaAPI = async (message) => {
    try {
      setIsLoading(true);
      
      const response = await fetch('http://127.0.0.1:8000/api/v1/chatbot/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          message: message
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        addBotMessage(
          data.response.content,
          data.response.intent,
          data.response.suggested_actions,
          data.response.metadata
        );
      } else {
        addBotMessage(
          "I apologize, but I encountered an error processing your message. Please try again.",
          'general_question',
          ['Try rephrasing your question', 'Ask about market analysis']
        );
      }
    } catch (error) {
      console.error('Error sending message:', error);
      addBotMessage(
        "I'm having trouble connecting right now. Please try again in a moment.",
        'general_question',
        ['Try again', 'Check connection']
      );
    } finally {
      setIsLoading(false);
    }
  };

  const addUserMessage = (content) => {
    const newMessage = {
      id: Date.now(),
      type: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const addBotMessage = (content, intent, actions = [], metadata = null) => {
    const newMessage = {
      id: Date.now(),
      type: 'bot',
      content,
      intent,
      timestamp: new Date(),
      metadata
    };
    setMessages(prev => [...prev, newMessage]);
    setSuggestedActions(actions);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSuggestedAction = (action) => {
    setInputMessage(action);
    setSuggestedActions([]);
  };

  const clearChat = async () => {
    if (window.confirm('Are you sure you want to clear the chat history?')) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/v1/chatbot/chat/history/${userId}`, {
          method: 'DELETE',
        });
        
        if (response.ok) {
          setMessages([]);
          setChatHistory([]);
          initializeChatbot();
        }
      } catch (error) {
        console.error('Error clearing chat:', error);
      }
    }
  };

  const renderMessage = (message) => {
    const isUser = message.type === 'user';
    
    return (
      <div key={message.id} className={`message ${isUser ? 'user-message' : 'bot-message'}`}>
        <div className="message-content">
          {!isUser && (
            <div className="bot-avatar">
              <span>🤖</span>
            </div>
          )}
          
          <div className="message-bubble">
            <div className="message-text" dangerouslySetInnerHTML={{ __html: formatMessage(message.content) }} />
            <div className="message-timestamp">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
          
          {isUser && (
            <div className="user-avatar">
              <span>👤</span>
            </div>
          )}
        </div>
        
        {!isUser && message.intent && (
          <div className="message-intent">
            Intent: {message.intent.replace('_', ' ')}
          </div>
        )}
      </div>
    );
  };

  const formatMessage = (content) => {
    // Convert markdown-like formatting to HTML
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  };

  const renderSuggestedActions = () => {
    if (suggestedActions.length === 0) return null;
    
    return (
      <div className="suggested-actions">
        <div className="suggested-actions-label">Suggested actions:</div>
        <div className="suggested-actions-buttons">
          {suggestedActions.map((action, index) => (
            <button
              key={index}
              onClick={() => handleSuggestedAction(action)}
              className="suggested-action-btn"
            >
              {action}
            </button>
          ))}
        </div>
      </div>
    );
  };

  const renderHelpModal = () => (
    <div className="modal-overlay">
      <div className="modal-content help-modal">
        <div className="modal-header">
          <h2>How to use the AI Trading Assistant</h2>
          <button 
            onClick={() => setShowHelp(false)}
            className="close-btn"
          >
            ×
          </button>
        </div>
        
        <div className="modal-body">
          <div className="help-section">
            <h3>📈 Market Analysis</h3>
            <p>Ask about current market conditions, trends, and outlook:</p>
            <ul>
              <li>"What's the current market outlook?"</li>
              <li>"Analyze AAPL stock"</li>
              <li>"What's the trend for tech stocks?"</li>
            </ul>
          </div>
          
          <div className="help-section">
            <h3>🎯 Trading Strategies</h3>
            <p>Get recommendations and explanations for trading strategies:</p>
            <ul>
              <li>"Recommend a strategy for trending markets"</li>
              <li>"Explain moving average crossover"</li>
              <li>"What strategy works best for volatility?"</li>
            </ul>
          </div>
          
          <div className="help-section">
            <h3>💼 Portfolio Management</h3>
            <p>Get advice on portfolio optimization and management:</p>
            <ul>
              <li>"How should I diversify my portfolio?"</li>
              <li>"What's the optimal asset allocation?"</li>
              <li>"When should I rebalance?"</li>
            </ul>
          </div>
          
          <div className="help-section">
            <h3>🛡️ Risk Management</h3>
            <p>Learn about risk management principles:</p>
            <ul>
              <li>"How much should I risk per trade?"</li>
              <li>"Where should I set stop losses?"</li>
              <li>"How to manage portfolio risk?"</li>
            </ul>
          </div>
          
          <div className="help-section">
            <h3>📊 Technical Analysis</h3>
            <p>Get guidance on technical analysis:</p>
            <ul>
              <li>"What indicators should I use?"</li>
              <li>"How to identify support/resistance?"</li>
              <li>"Explain chart patterns"</li>
            </ul>
          </div>
          
          <div className="help-tips">
            <h3>💡 Tips for better responses:</h3>
            <ul>
              <li>Be specific with your questions</li>
              <li>Mention stock symbols (e.g., AAPL, GOOGL) for specific analysis</li>
              <li>Ask follow-up questions to dive deeper into topics</li>
              <li>Use the suggested actions to explore related topics</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="ai-chatbot">
      <div className="chatbot-header">
        <div className="header-info">
          <h2>🤖 AI Trading Assistant</h2>
          <p>Your intelligent companion for trading decisions and market insights</p>
        </div>
        
        <div className="header-actions">
          <button 
            onClick={() => setShowHelp(true)}
            className="btn btn-outline"
            title="Help"
          >
            ❓ Help
          </button>
          <button 
            onClick={clearChat}
            className="btn btn-secondary"
            title="Clear Chat"
          >
            🗑️ Clear
          </button>
        </div>
      </div>

      <div className="chat-container">
        <div className="messages-container">
          {messages.map(renderMessage)}
          
          {isLoading && (
            <div className="message bot-message">
              <div className="message-content">
                <div className="bot-avatar">
                  <span>🤖</span>
                </div>
                <div className="message-bubble">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {renderSuggestedActions()}

        <div className="input-container">
          <div className="input-wrapper">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask me about trading, markets, strategies, or risk management..."
              disabled={isLoading}
              className="message-input"
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="send-button"
            >
              {isLoading ? '⏳' : '📤'}
            </button>
          </div>
          
          <div className="input-hint">
            Press Enter to send • Use specific questions for better answers
          </div>
        </div>
      </div>

      {/* Help Modal */}
      {showHelp && renderHelpModal()}
    </div>
  );
};

export default AIChatbot;
