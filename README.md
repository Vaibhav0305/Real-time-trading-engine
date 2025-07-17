# VittCott Trading Engine

A simple C++ CLI-based trading engine that supports placing, modifying, and canceling buy/sell orders, matching trades, logging to CSV, and simulating email notifications.

## Features
- Place, modify, and cancel buy/sell orders
- Order matching engine with FIFO/price priority
- Trade and order logging to CSV files
- Simulated email notifications for trades and order events
- Robust error handling and logging
- Colorful CLI notifications

## Build Instructions

1. **Install CMake and a C++17 compiler**
2. **Build the project:**
   ```sh
   cmake -S . -B build
   cmake --build build
   ```
3. **Run the executable:**
   ```sh
   ./build/VittCott.exe
   ```

## Usage
- Follow the CLI menu to place, modify, cancel orders, or view the order book.
- All trades and orders are logged to CSV files in the project directory.
- Notifications and errors are logged to `notifications.log` and `error.log`.

## File Structure
- `main.cpp` - CLI entry point
- `Order.h/cpp`, `Trade.h/cpp` - Core data structures
- `OrderBook.h/cpp`, `MatchingEngine.h/cpp` - Matching logic
- `TradeLogger.h/cpp` - CSV logging
- `Logger.h/cpp` - Logging utility
- `EmailNotifier.h` - Simulated notifications

## License
MIT
