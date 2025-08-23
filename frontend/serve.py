import http.server
import socketserver
import os

class VittCottHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

if __name__ == "__main__":
    PORT = 3000
    
    # Change to the directory where this script is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"🚀 Starting VittCott Server on port {PORT}")
    print(f"📍 Serving from: {os.getcwd()}")
    print(f"📁 index.html location: {os.path.join(os.getcwd(), 'index.html')}")
    print("🌐 VittCott Trading Platform will be available at: http://localhost:3000")
    
    with socketserver.TCPServer(("", PORT), VittCottHandler) as httpd:
        print(f"✅ Server started successfully on port {PORT}")
        print("🔄 Press Ctrl+C to stop the server")
        httpd.serve_forever()
