// API service for communicating with the FastAPI backend

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${error.message}`);
            throw error;
        }
    }

    // Order management
    async placeOrder(orderData) {
        return this.request('/orders', {
            method: 'POST',
            body: JSON.stringify(orderData),
        });
    }

    async getOrders(symbol = null, status = null) {
        const params = new URLSearchParams();
        if (symbol) params.append('symbol', symbol);
        if (status) params.append('status', status);
        
        const queryString = params.toString();
        const endpoint = queryString ? `/orders?${queryString}` : '/orders';
        
        return this.request(endpoint);
    }

    async getOrder(orderId) {
        return this.request(`/orders/${orderId}`);
    }

    async modifyOrder(orderId, orderUpdate) {
        return this.request(`/orders/${orderId}`, {
            method: 'PUT',
            body: JSON.stringify(orderUpdate),
        });
    }

    async cancelOrder(orderId) {
        return this.request(`/orders/${orderId}`, {
            method: 'DELETE',
        });
    }

    // Trade management
    async getTrades(symbol = null) {
        const params = new URLSearchParams();
        if (symbol) params.append('symbol', symbol);
        
        const queryString = params.toString();
        const endpoint = queryString ? `/trades?${queryString}` : '/trades';
        
        return this.request(endpoint);
    }

    // Order book
    async getOrderBook(symbol) {
        return this.request(`/orderbook/${symbol}`);
    }

    // WebSocket connection for real-time updates
    connectWebSocket(onMessage, onError, onClose) {
        const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws';
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('WebSocket connected');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                onMessage(data);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            onError?.(error);
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected');
            onClose?.();
        };

        return ws;
    }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;
