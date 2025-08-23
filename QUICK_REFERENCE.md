# 🚀 VittCott Trading Platform - Quick Reference

## 🎯 **What This Is**
A **hybrid trading platform** combining:
- **C++ Core**: High-performance order matching engine
- **Python Backend**: FastAPI with real-time WebSocket data
- **React Frontend**: Modern web trading interface

## 🚀 **Quick Start (5 minutes)**

### 1. Backend (Port 8000)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python advanced_trading_api.py
```
**API Docs**: http://localhost:8000/docs

### 2. Frontend (Port 3000)
```bash
cd frontend
npm install
npm run dev
```

### 3. C++ Engine
```bash
cmake -S . -B build
cmake --build build
./build/VittCott.exe
```

## 🔑 **Key Files**
- **`backend/advanced_trading_api.py`** - Main API (541 lines)
- **`main.cpp`** - C++ entry point (180 lines)
- **`OrderBook.h/cpp`** - Order matching logic
- **`frontend/src/App.jsx`** - React main component

## 📊 **Current Status**
- ✅ **Backend**: Complete with 20+ endpoints
- ✅ **C++ Engine**: Order matching, CSV logging
- 🚧 **Frontend**: Basic structure, needs components
- 📋 **Database**: SQLite with sample data

## 🌐 **Main Endpoints**
- `GET /api/v1/market/overview` - Market data
- `POST /api/v1/orders/place` - Place orders
- `GET /api/v1/portfolio/overview` - Portfolio
- `WS /api/v1/ws/market-data` - Real-time updates

## 🔧 **Tech Stack**
- **Backend**: FastAPI + SQLite + Redis
- **Frontend**: React + Vite
- **Engine**: C++17 + CMake
- **Deploy**: Docker + docker-compose

## 📚 **Full Documentation**
See `PROJECT_COMPLETE_OVERVIEW.md` for complete details.

---

**Need help? Check the full overview document first!**
