#!/usr/bin/env python3
"""
Startup script for VittCott Trading Platform Backend
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        # Check FastAPI and Uvicorn
        import fastapi
        import uvicorn
        logger.info("FastAPI and Uvicorn available")
        
        # Check if C++ trading engine exists
        engine_path = Path("../trading_engine.exe")
        if not engine_path.exists():
            logger.error(f"C++ trading engine not found at: {engine_path}")
            return False
        
        logger.info(f"C++ trading engine found at: {engine_path}")
        return True
        
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        return False

def start_backend():
    """Start the FastAPI backend server"""
    try:
        logger.info("Starting VittCott Trading Platform Backend...")
        
        # Get the current directory
        current_dir = Path(__file__).parent
        
        # Start the server using uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn",
            "main:app",  # Use the correct import string
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        logger.info(f"Starting server with command: {' '.join(cmd)}")
        logger.info(f"Server will be available at: http://localhost:8000")
        logger.info("Press Ctrl+C to stop the server")
        
        # Start the server
        subprocess.run(cmd, cwd=current_dir)
        
    except Exception as e:
        logger.error(f"Failed to start backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Checking dependencies...")
    if check_dependencies():
        start_backend()
    else:
        logger.error("Dependency check failed. Please install missing dependencies.")
        sys.exit(1)
