import sys
import os

# Get absolute path to build directory
BUILD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../build'))
sys.path.insert(0, BUILD_DIR)

import unittest
from trading_engine import Order, OrderBook, Logger, EmailNotifier, BUY, SELL

# ...rest of your test code remains the same...