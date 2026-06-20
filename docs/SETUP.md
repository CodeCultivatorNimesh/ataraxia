# Setup Guide — Trading Middleware Phase 2

## Prerequisites

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.12+ | https://python.org |
| Node.js | 18+ | https://nodejs.org |
| Docker Desktop | Latest | https://docker.com |
| Git | Any | https://git-scm.com |

## Step 1 — Clone / Extract

```
# Extract the zip into a folder, then open a terminal there
cd trading-middleware
```

## Step 2 — Run Setup

```
scripts\setup.bat
```

This will:
- Create a Python virtual environment
- Install all dependencies from requirements.txt
- Copy .env.example → .env
- Start PostgreSQL and Redis via Docker

## Step 3 — Add Your API Keys

Open `.env` in any text editor and fill in:

```
# Alpaca — free paper trading at https://alpaca.markets
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here

# Binance — testnet available at https://testnet.binancefuture.com
BINANCE_API_KEY=your_key_here
BINANCE_SECRET_KEY=your_secret_here
BINANCE_TESTNET=true
```

## Step 4 — Start the Server

```
scripts\run_dev.bat
```

## Step 5 — Verify

Open your browser:
- **API Docs**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health
- **Pattern catalog**: http://localhost:8000/api/v1/patterns/catalog

## Running Tests

```
# Activate venv first
venv\Scripts\activate.bat

# Unit tests (no API keys needed)
pytest tests/unit/ -v

# Integration tests (needs API keys + DB running)
pytest tests/integration/ -v -s
```

## Common Issues

**Docker not running**: Start Docker Desktop before running setup.bat

**Port 5432 in use**: Another PostgreSQL is running. Stop it or change POSTGRES_PORT in .env

**ModuleNotFoundError**: Make sure venv is activated: `venv\Scripts\activate.bat`

**Alpaca 403 error**: Check your API keys and make sure paper trading is enabled
