# API Reference — Trading Middleware

Base URL: `http://localhost:8000/api/v1`
Interactive docs: `http://localhost:8000/docs`

## Position Sizing

### POST /position/spot
Calculate position size for stocks or crypto spot.

**Request:**
```json
{
  "account_balance": 10000,
  "risk_pct": 1.0,
  "entry_price": 150,
  "atr_value": 3.5,
  "direction": "long",
  "volatility": "medium",
  "asset_type": "stock"
}
```

### POST /position/crypto-futures/cross
Cross mode futures position sizing.

### POST /position/crypto-futures/isolated
Isolated mode — max 3 positions enforced.

## Risk Engine

### POST /risk/validate
Validate a trade against all risk rules.

### POST /risk/var
Calculate Value at Risk from trade returns list.

## Candlestick Patterns

### POST /patterns/detect
Detect patterns from OHLCV candle data. Saves to DB, triggers alerts.

### GET /patterns/catalog
Returns all 45 supported patterns with descriptions.

### GET /patterns/history/{symbol}
Historical pattern detections for a symbol.

### GET /patterns/alerts/unread
Unread pattern alerts.

## Broker

### GET /broker/account/{broker}
Fetch account info. broker = alpaca | binance | binance_futures

### GET /broker/price/{broker}/{symbol}
Live price for a symbol.

### GET /broker/candles/{broker}/{symbol}
OHLCV candles. Params: timeframe, limit

### POST /broker/atr
Auto-calculate ATR from live candle data.

### POST /broker/order
Place an order. broker = alpaca | binance | binance_futures

### GET /broker/futures/cross-check
Check if a cross-mode position is already open.

### GET /broker/futures/isolated-slots
Check available isolated position slots.

## Behavioral

### POST /behavioral/analyze
Run behavioral analysis on recent trades.

### POST /behavioral/decision
Get allow/block decision based on psychological state.

### GET /behavioral/history
Historical behavioral scores.

## Journal

### POST /journal/trade
Log a new trade.

### PATCH /journal/trade/{id}/close
Close a trade with exit price, auto-calculates PnL.

### GET /journal/trades
Trade history.

### POST /journal/entry
Create a journal entry with notes.

### GET /journal/entries
Journal entry history.

## Analytics

### GET /analytics/dashboard
Full dashboard: PnL, win rate, Sharpe ratio, top patterns.

### GET /analytics/performance
Equity curve by day.

### GET /analytics/var
Portfolio-level Value at Risk.

## WebSocket

### WS /ws/alerts?symbol=BTCUSDT
Real-time pattern alerts for a symbol.

### WS /ws/dashboard
Real-time dashboard updates.
