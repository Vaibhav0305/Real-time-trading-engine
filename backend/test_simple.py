#!/usr/bin/env python3
"""
Simple test to check if C++ bindings import is working
"""

import socket

def test_port(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        if result == 0:
            print(f"Port {port} is open")
        else:
            print(f"Port {port} is closed")
    except Exception as e:
        print(f"Error testing port {port}: {e}")

if __name__ == "__main__":
    print("Testing ports...")
    test_port(8000)
    test_port(8080)
    test_port(3000)
    
    print("\nTrying to create a simple server...")
    try:
        import http.server
        import socketserver
        
        PORT = 3000
        Handler = http.server.SimpleHTTPRequestHandler
        
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Server started at port {PORT}")
            print("Press Ctrl+C to stop")
            httpd.serve_forever()
    except Exception as e:
        print(f"Error starting server: {e}")
