import http.server
import socketserver

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

print(f"Starting simple HTTP server on port {PORT}...")
print("This will help us test if the port is accessible")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server started at http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()

