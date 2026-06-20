# Trading Middleware — Phase 2 Backend

Behavioral-risk-aware trading middleware bridge with candlestick pattern detection,
broker integration (Alpaca + Binance), and psychological analytics.

## Quick Start (Windows)

```
1. scripts\setup.bat      ← installs everything
2. Edit .env              ← add your API keys
3. scripts\run_dev.bat    ← starts the server
4. Open http://localhost:8000/docs
```

## Requirements

- Python 3.12+
- Node.js 18+
- Docker Desktop (for PostgreSQL + Redis)
- Alpaca API keys → https://alpaca.markets (free paper trading)
- Binance API keys → https://binance.com (testnet available)

## API Endpoints

| Route | Description |
|-------|-------------|
| POST /api/v1/position/spot | Position size for stocks/crypto |
| POST /api/v1/position/crypto-futures/cross | Cross mode position |
| POST /api/v1/position/crypto-futures/isolated | Isolated mode position |
| POST /api/v1/risk/validate | Validate trade against risk rules |
| POST /api/v1/patterns/detect | Detect candlestick patterns |
| GET  /api/v1/patterns/catalog | All 45 supported patterns |
| GET  /api/v1/patterns/alerts/unread | Unread pattern alerts |
| POST /api/v1/broker/order | Place order on Alpaca or Binance |
| GET  /api/v1/broker/price/{broker}/{symbol} | Live price |
| GET  /api/v1/broker/candles/{broker}/{symbol} | OHLCV candles |
| POST /api/v1/broker/atr | Auto-calculate ATR from live data |
| POST /api/v1/behavioral/analyze | Behavioral score + bias detection |
| POST /api/v1/behavioral/decision | Allow/block trade decision |
| POST /api/v1/journal/trade | Log a trade |
| GET  /api/v1/journal/trades | Get trade history |
| GET  /api/v1/analytics/dashboard | Full dashboard data |
| GET  /api/v1/analytics/performance | Equity curve |
| WS   /api/v1/ws/alerts | Real-time pattern alerts |
| WS   /api/v1/ws/dashboard | Real-time dashboard updates |

## Candlestick Patterns Supported (45 total)

- **Single** (11): Doji, Hammer, Shooting Star, Marubozu, Dragonfly Doji...
- **Double** (11): Engulfing, Harami, Piercing Line, Dark Cloud Cover...
- **Triple** (12): Morning/Evening Star, Three White Soldiers, Abandoned Baby...
- **Continuation** (11): Rising/Falling Three Methods, Tasuki Gap, Mat Hold...

## Project Structure

```
trading-middleware/
├── app/
│   ├── api/routes/          API endpoints
│   ├── broker/              Alpaca + Binance clients
│   ├── risk/                Position sizing + risk engine
│   ├── patterns/            45 candlestick pattern detectors
│   ├── psychology/          Behavioral + bias analytics
│   ├── journal/             Auto trade journal
│   ├── analytics/           Performance + VaR
│   ├── models/              Database models
│   ├── database/            PostgreSQL connection
│   ├── services/            ATR + cache
│   └── websocket/           Real-time streaming
├── docker/                  Docker configs
├── scripts/                 Windows setup scripts
└── docs/                    API documentation
```
