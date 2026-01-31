# 🔥 Jager Burn Calculator

A complete application for monitoring and projecting Jager token burns, with an interactive dashboard and robust API.

[![Live Demo](https://img.shields.io/badge/demo-live-success?style=for-the-badge&logo=vercel)](https://jager-calculator.vercel.app/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2.0-000000?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)

**🌐 [Live Demo](https://jager-calculator.vercel.app/)** | **📖 [API Docs](https://jager-burn-backend.fly.dev/docs)** | **🐛 [Report Bug](../../issues)** | **✨ [Request Feature](../../issues)**

## Preview

<img width="1919" height="732" alt="image" src="https://github.com/user-attachments/assets/5f964a98-5e60-4bb9-9c6d-986d2a96a46a" />

<img width="1726" height="675" alt="image" src="https://github.com/user-attachments/assets/19faf70a-0791-41df-90ad-7fc53ce99b18" />

<img width="1559" height="787" alt="image" src="https://github.com/user-attachments/assets/9a50cbb5-a710-400b-91cd-2e58e241c636" />

## 📋 About the Project

The **Jager Burn Calculator** is a tool that allows you to track in real-time the burning of Jager tokens sent to the dead address. The application offers:

- 📊 **Interactive Dashboard**: Real-time metrics visualization with charts and informative cards
- 📈 **Historical Analysis**: Daily burn tracking with different viewing periods
- 🔮 **Future Projections**: Burn projection calculations using statistical models (mean and linear regression)
- 💰 **Tokenomics**: Visualization of max supply, total burned, burn percentage, and current price
- ⚡ **Smart Cache**: Local cache system to save Moralis API credits
- 🌐 **RESTful API**: Complete backend with documented endpoints

## 🏗️ Architecture

The project is divided into two main parts:

### Backend (FastAPI + Python)
- RESTful API built with FastAPI
- Integration with Moralis API for on-chain data
- SQLite cache system for query optimization
- Historical data backfill support
- Protection against excessive API credit consumption

### Frontend (Next.js + React)
- Modern interface built with Next.js 14
- React components with TypeScript
- Styling with TailwindCSS
- Interactive charts with Recharts
- Responsive and optimized design

## 🚀 Getting Started

This project has two components that need to be run:

1. **Backend**: API that fetches and processes data
2. **Frontend**: Web interface for visualization

### Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 18+** (for frontend)
- **Moralis API Key** (free at [moralis.io](https://moralis.io))

### Quick Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd jager_burn
```

2. **Configure and run the backend**
   - See detailed instructions in [`backend/README.md`](./backend/README.md)

3. **Configure and run the frontend**
   - See detailed instructions in [`frontend/README.md`](./frontend/README.md)

## 📚 Detailed Documentation

- **[Backend README](./backend/README.md)**: Complete instructions to configure and run the backend
- **[Frontend README](./frontend/README.md)**: Complete instructions to configure and run the frontend

## 🎯 Main Features

### Token Metrics
- Configurable max supply
- Total tokens burned (dead address balance)
- Burn percentage
- Remaining supply
- Current price via Moralis

### Burn Analysis
- Daily summary (yesterday vs today)
- Historical series with configurable windows (7, 14, 30, 60, 90, 180, 365 days)
- Interactive daily burn charts

### Projections
- Simple mean model
- Linear regression model
- Configurable projection horizons
- Estimates of when important milestones will be reached

## 🔧 Technologies Used

### Backend
- **FastAPI**: Modern and fast web framework
- **Uvicorn**: High-performance ASGI server
- **Pydantic**: Data validation
- **HTTPX**: Asynchronous HTTP client
- **SQLite**: Database for caching
- **Moralis API**: Blockchain data

### Frontend
- **Next.js 14**: React framework with App Router
- **React 18**: UI library
- **TypeScript**: Static typing
- **TailwindCSS**: Utility-first CSS framework
- **Recharts**: Charting library
- **Vercel Analytics**: Usage analytics

## 💡 Important Tips

### Saving Moralis Credits
The backend has protections to avoid excessive credit consumption:
- Local cache for historical data
- Automatic fetching of past days disabled by default
- Configurable TTL for cache

### Data Backfill
To fill the initial history, run once:
```bash
cd backend
python -m app.backfill --start 2025-04-28
```

### Cache Reuse
If you already have a `cache.sqlite3` file with historical data, just copy it to the backend directory.

## 📝 License

This project is open source and available for free use.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or pull requests.

---

**Built with ❤️ for the Jager community**
