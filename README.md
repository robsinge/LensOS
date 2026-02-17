# LensOS — Predictive Lens Manufacturing & Intelligence

LensOS is an AI-powered supply chain and demand intelligence platform designed for modern lens manufacturing. It provides executives and operations managers with predictive insights, optimized production plans, and "what-if" scenario simulations.

---

## 🚀 Key Features

- **Executive Intelligence Dashboard**: Real-time KPIs for revenue, loss risk, and capacity utilization.
- **Demand Forecasting**: SKU-level forecasting using LightGBM and time-series analysis with confidence bands.
- **Production Optimization**: Linear Programming (LP) based capacity-constrained manufacturing planning.
- **Scenario Simulator**: Strategic planning tool for demand multipliers, price sensitivity, and capacity changes.
- **Inventory Allocation**: Geographic-aware distribution planning across major city tiers.
- **Guided Product Tour**: Built-in 12-step onboarding tour for new users.
- **Responsive Design**: Premium mobile and desktop experience built with Tailwind CSS.

---

## 🏗️ Technical Architecture

### Backend (Python/FastAPI)
- **Framework**: FastAPI (high-performance ASGI)
- **Optimization**: SciPy (`linprog`) for production planning
- **Machine Learning**: LightGBM and Scikit-learn for demand prediction
- **Data Engine**: Pandas and NumPy for real-time simulation datasets

### Frontend (React/Vite)
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS & Framer Motion
- **Visualization**: Recharts & Lucide Icons
- **State Management**: Axios with centralized API configuration

---

## 📂 Project Structure

```text
LensOS/
├── api.py              # FastAPI server and endpoint definitions
├── requirements.txt    # Backend dependencies
├── src/                # Core logic & ML modules
│   ├── capacity_optimizer.py  # LP-based optimization engine
│   ├── scenario_simulator.py  # Scenario recomputation logic
│   └── train_forecast.py      # ML forecasting models
├── models/             # Trained .pkl models
├── data/               # Production runtime datasets (CSV)
├── training_data/      # Massive historical logs (Git ignored)
└── frontend/           # Vite/React application
    ├── src/
    │   ├── components/ # Modular UI components
    │   └── lib/        # API and utility functions
    └── .env            # Frontend environment config
```

---

## 🛠️ Installation & Setup

### 1. Backend Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn api:app --host 0.0.0.0 --port 8001
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Configure environment (copy example or create .env)
# VITE_API_URL=http://localhost:8001

# Start development server
npm run dev
```

---

## 🌐 Deployment

### Frontend (Vercel)
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Environment Variable**: `VITE_API_URL` (Set to your Render backend URL)

### Backend (Render)
- **Environment**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`

---

## 📊 Monitoring

LensOS includes a health monitoring endpoint for cloud platforms:
`GET /health` -> `{"status": "ok"}`

---

## 📝 License

Demo project for educational and operational excellence demonstration.