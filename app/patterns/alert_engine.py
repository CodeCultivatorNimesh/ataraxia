from datetime import datetime
from loguru import logger

class PatternAlertEngine:

    def __init__(self):
        self.subscribers = {}  # symbol -> list of websocket connections

    def subscribe(self, symbol: str, websocket):
        if symbol not in self.subscribers:
            self.subscribers[symbol] = []
        self.subscribers[symbol].append(websocket)

    def unsubscribe(self, symbol: str, websocket):
        if symbol in self.subscribers:
            self.subscribers[symbol] = [
                ws for ws in self.subscribers[symbol] if ws != websocket
            ]

    async def process_patterns(self, symbol: str, timeframe: str, patterns: list, price: float):
        if not patterns:
            return []

        alerts = []
        for pattern in patterns:
            alert = self._build_alert(symbol, timeframe, pattern, price)
            alerts.append(alert)
            logger.info(f"Pattern alert: {symbol} {pattern['pattern_name']} ({pattern['confidence']:.0%} confidence)")
            await self._broadcast(symbol, alert)

        return alerts

    def _build_alert(self, symbol, timeframe, pattern, price):
        ptype = pattern["pattern_type"]
        emoji = "🟢" if ptype == "bullish" else "🔴" if ptype == "bearish" else "⚪"
        return {
            "id":           f"{symbol}_{pattern['pattern_name']}_{datetime.utcnow().timestamp()}",
            "symbol":       symbol,
            "timeframe":    timeframe,
            "pattern_name": pattern["pattern_name"],
            "pattern_type": ptype,
            "category":     pattern["category"],
            "confidence":   pattern["confidence"],
            "price":        price,
            "message":      f"{emoji} {pattern['pattern_name']} detected on {symbol} ({timeframe}) — {pattern['description']}",
            "description":  pattern["description"],
            "is_read":      False,
            "created_at":   datetime.utcnow().isoformat(),
        }

    async def _broadcast(self, symbol: str, alert: dict):
        if symbol not in self.subscribers:
            return
        dead = []
        for ws in self.subscribers[symbol]:
            try:
                await ws.send_json({"type": "pattern_alert", "data": alert})
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.unsubscribe(symbol, ws)

alert_engine = PatternAlertEngine()
