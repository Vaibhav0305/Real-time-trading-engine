#!/usr/bin/env python3
"""
Test script for VittCott Trading Platform API
"""

import requests
import time
import sys

def test_api():
    """Test the API endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing VittCott Trading Platform API...")
    print("=" * 50)
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False
    
    # Test symbols endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/symbols")
        print(f"✅ Symbols endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Symbols endpoint failed: {e}")
        return False
    
    # Test orders endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/orders")
        print(f"✅ Orders endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Orders endpoint failed: {e}")
        return False
    
    print("=" * 50)
    print("🎉 All API tests completed!")
    return True

if __name__ == "__main__":
    print("Starting VittCott Trading Platform Backend...")
    
    # Start the server in background
    import subprocess
    import os
    
    # Start uvicorn server
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "127.0.0.1",
        "--port", "8000"
    ]
    
    print(f"Starting server with: {' '.join(cmd)}")
    
    # Start server in background
    process = subprocess.Popen(cmd, cwd=os.getcwd())
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    # Test the API
    success = test_api()
    
    # Stop the server
    print("Stopping server...")
    process.terminate()
    process.wait()
    
    if success:
        print("🎉 API test completed successfully!")
    else:
        print("❌ API test failed!")
        sys.exit(1)
