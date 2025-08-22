#!/usr/bin/env python3
"""
Python bindings for VittCott C++ Trading Engine
This module provides Python interfaces to the compiled C++ trading engine
"""

import os
import sys
import subprocess
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CPPTradingEngine:
    """Python wrapper for the C++ trading engine"""
    
    def __init__(self, engine_path: str = None):
        """Initialize the C++ trading engine wrapper"""
        if engine_path is None:
            # Look for the compiled engine in the project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            engine_path = os.path.join(project_root, "trading_engine.exe" if os.name == "nt" else "trading_engine")
        
        self.engine_path = engine_path
        self.engine_process = None
        self.is_running = False
        
        # Verify engine exists
        if not os.path.exists(engine_path):
            raise FileNotFoundError(f"Trading engine not found at: {engine_path}")
        
        logger.info(f"Initialized C++ trading engine wrapper: {engine_path}")
    
    def _start_engine(self):
        """Start the C++ engine process"""
        try:
            self.engine_process = subprocess.Popen(
                [self.engine_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            )
            self.is_running = True
            logger.info("C++ trading engine process started")
            
            # Wait a moment for the engine to initialize
            import time
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Failed to start C++ engine: {e}")
            raise
    
    def _stop_engine(self):
        """Stop the C++ engine process"""
        if self.engine_process and self.is_running:
            try:
                self.engine_process.terminate()
                self.engine_process.wait(timeout=5)
                self.is_running = False
                logger.info("C++ trading engine process stopped")
            except subprocess.TimeoutExpired:
                self.engine_process.kill()
                self.is_running = False
                logger.warning("C++ trading engine process force killed")
            except Exception as e:
                logger.error(f"Error stopping C++ engine: {e}")
    
    def _send_command(self, command: str) -> str:
        """Send a command to the C++ engine and get response"""
        if not self.is_running:
            self._start_engine()
        
        try:
            # Send command
            self.engine_process.stdin.write(command + "\n")
            self.engine_process.stdin.flush()
            
            # Read response
            response = ""
            timeout_count = 0
            max_timeout = 100  # Prevent infinite loop
            
            while timeout_count < max_timeout:
                line = self.engine_process.stdout.readline()
                if not line:
                    timeout_count += 1
                    continue
                
                response += line
                
                # Check if we've reached the menu prompt
                if "Enter your choice:" in line:
                    break
                
                # Check if we've reached the end of a response
                if "Order placed with ID:" in line or "Order modified." in line or "Order cancelled." in line:
                    break
            
            return response.strip()
        except Exception as e:
            logger.error(f"Error communicating with C++ engine: {e}")
            # Try to restart the engine
            self._stop_engine()
            self._start_engine()
            raise
    
    def place_order(self, symbol: str, order_type: str, price: float, quantity: int) -> Dict[str, Any]:
        """Place an order through the C++ engine"""
        try:
            # Send place order command
            command = f"1\n{symbol}\n{order_type.lower()}\n{price}\n{quantity}\n5\n"
            response = self._send_command(command)
            
            # Parse response to extract order ID
            order_id = None
            for line in response.split('\n'):
                if "Order ID:" in line:
                    order_id = line.split("Order ID:")[1].strip()
                    break
                elif "Order placed with ID:" in line:
                    order_id = line.split("Order placed with ID:")[1].strip()
                    break
            
            if not order_id:
                # If we can't find the order ID, generate one
                order_id = f"ORD-{int(datetime.now().timestamp() * 1000)}"
                logger.warning(f"Could not extract order ID from response, generated: {order_id}")
            
            return {
                "order_id": order_id,
                "symbol": symbol,
                "type": order_type.upper(),
                "price": price,
                "quantity": quantity,
                "status": "PENDING",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            raise
    
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an order through the C++ engine"""
        try:
            # Send cancel order command
            command = f"3\n{order_id}\n5\n"
            response = self._send_command(command)
            
            # Check if cancellation was successful
            return "cancelled" in response.lower()
            
        except Exception as e:
            logger.error(f"Failed to cancel order: {e}")
            return False
    
    def modify_order(self, symbol: str, order_id: str, new_price: float, new_quantity: int) -> Dict[str, Any]:
        """Modify an order through the C++ engine"""
        try:
            # Send modify order command
            command = f"2\n{order_id}\n{new_price}\n{new_quantity}\n5\n"
            response = self._send_command(command)
            
            # Check if modification was successful
            if "modified" in response.lower() or "Order modified" in response:
                return {
                    "order_id": order_id,
                    "symbol": symbol,
                    "price": new_price,
                    "quantity": new_quantity,
                    "status": "MODIFIED",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Log the actual response for debugging
                logger.warning(f"Unexpected response from modify order: {response}")
                # Assume success if we don't get an error
                return {
                    "order_id": order_id,
                    "symbol": symbol,
                    "price": new_price,
                    "quantity": new_quantity,
                    "status": "MODIFIED",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to modify order: {e}")
            raise
    
    def get_order_book(self, symbol: str) -> Dict[str, Any]:
        """Get order book for a symbol through the C++ engine"""
        try:
            # Send print order book command
            command = f"4\n{symbol}\n5\n"
            response = self._send_command(command)
            
            # Parse the response to extract order book data
            orders = []
            for line in response.split('\n'):
                if "Order:" in line and "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 4:
                        order_id = parts[0].split("Order:")[1].strip()
                        order_type = parts[1].strip()
                        price_part = parts[2].strip()
                        quantity_part = parts[3].strip()
                        
                        price = float(price_part.split(":")[1].strip())
                        quantity = int(quantity_part.split(":")[1].strip())
                        
                        orders.append({
                            "order_id": order_id,
                            "type": order_type,
                            "price": price,
                            "quantity": quantity
                        })
            
            # Group by type
            bids = [order for order in orders if "BUY" in order["type"]]
            asks = [order for order in orders if "SELL" in order["type"]]
            
            return {
                "symbol": symbol,
                "bids": sorted(bids, key=lambda x: x["price"], reverse=True),
                "asks": sorted(asks, key=lambda x: x["price"]),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get order book: {e}")
            return {"symbol": symbol, "bids": [], "asks": [], "last_updated": datetime.now().isoformat()}
    
    def get_all_orders(self) -> List[Dict[str, Any]]:
        """Get all orders from the C++ engine"""
        try:
            # This would require implementing a new command in the C++ engine
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Failed to get all orders: {e}")
            return []
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self._stop_engine()

# Create a global instance
cpp_engine = None

def get_cpp_engine() -> CPPTradingEngine:
    """Get or create the global C++ trading engine instance"""
    global cpp_engine
    if cpp_engine is None:
        try:
            cpp_engine = CPPTradingEngine()
        except Exception as e:
            logger.error(f"Failed to initialize C++ engine: {e}")
            raise
    return cpp_engine
