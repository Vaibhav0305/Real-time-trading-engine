# Real-time-trading-engine
A low-latency, real-time stock trading engine built in C++ that simulates how professional trading platforms (like Zerodha or Upstox) process orders behind the scenes. This project features a high-performance order matching engine, basic risk management, and a multi-threaded TCP server to simulate real-world trading scenarios.

🚀 Features:
📥 Order Intake System: Accepts Buy/Sell orders from multiple clients

📊 Order Book Management: Maintains real-time limit order book (Bid/Ask side)

⚙️ Order Matching Engine: Matches orders using price-time priority

🛡 Risk Management Module: Validates orders based on user limits and capital

📬 Trade Execution Engine: Finalizes matched orders and sends confirmations

🔁 Multithreaded TCP Server: Simulates concurrent traders placing real-time orders

📡 Redis Integration (Optional): Publishes trades for downstream consumers

🧾 Logging Module: Tracks trades, errors, and order status

📺 Simple UI (Phase 5): Visualizes order book and trade logs in terminal or web

🧠 Architecture Overview
plaintext
Copy code
+---------------------+
|  Trading Clients    |
+---------------------+
          |
          v  (via TCP)
+---------------------+
|  Network Server     |  <-- Multithreaded, parses order messages
+---------------------+
          |
          v
+---------------------+          +---------------------+
|  Risk Management    |  ----->  |  Capital Limits DB  |
+---------------------+          +---------------------+
          |
          v
+---------------------+
|  Order Matching     |  <-- Price-Time Priority
+---------------------+
          |
          v
+---------------------+
|  Order Book (Buy/Sell)
+---------------------+
          |
          v
+---------------------+
|  Trade Engine       |
+---------------------+
          |
          v
+---------------------+    -->  Logs, Redis Pub/Sub
|  Logger & Publisher |
+---------------------+
📦 Technologies Used
Component	Tech
Language	C++ (C++14/17)
Networking	TCP Sockets (std::thread)
Order Book	STL (std::map, queue)
Logging	spdlog / fstream
Messaging (Opt.)	Redis (Pub/Sub)
Build System	CMake
Testing	GoogleTest (Optional)
UI (Optional)	Terminal/React Web Interface

🧑‍💻 Use Cases
Simulate real-world trading behavior

Learn systems design for stock exchanges

Build a portfolio-worthy backend systems project

Prepare for interviews involving distributed systems, trading, or concurrency

🗓 Project Phases
Phase 1: Design and Architecture ✅

Phase 2: Core Engine Development

Phase 3: Risk Management + Redis

Phase 4: TCP Networking Layer

Phase 5: Logging + UI + Testing

