import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

class VittCottHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Route the requests
        if path == '/health':
            response = {"status": "healthy", "service": "VittCott Backend", "message": "Server is running!"}
        elif path == '/':
            response = {"message": "VittCott Trading Platform API - WORKING!"}
        elif path.startswith('/api/v1/chatbot/chat/history/'):
            user_id = path.split('/')[-1]
            response = {
                "success": True,
                "messages": [
                    {"id": 1, "content": "Welcome to VittCott!", "timestamp": "2024-01-01T00:00:00Z"},
                    {"id": 2, "content": "How can I help you with trading today?", "timestamp": "2024-01-01T00:00:01Z"}
                ]
            }
        elif path == '/api/v1/portfolio/overview':
            response = {
                "total_value": 50000.00,
                "total_pnl": 2500.00,
                "holdings": 5
            }
        elif path == '/api/v1/watchlist':
            response = {
                "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"],
                "count": 5
            }
        else:
            response = {"error": "Endpoint not found", "path": path}
        
        # Send response
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    PORT = 8000
    
    print("🚀 Starting VittCott Simple HTTP Server...")
    print(f"📍 Server will run on: http://localhost:{PORT}")
    print(f"🔗 Health check: http://localhost:{PORT}/health")
    print("📱 Frontend should connect to: http://localhost:3000")
    print("🔄 Press Ctrl+C to stop the server")
    
    with socketserver.TCPServer(("", PORT), VittCottHandler) as httpd:
        print(f"✅ Server started successfully on port {PORT}")
        print("🌐 VittCott Trading Platform Backend is now running!")
        httpd.serve_forever()
