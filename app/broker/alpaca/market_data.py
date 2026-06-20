"""
Alpaca market data helpers — live quotes, bars, screeners.
"""
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import (
    StockBarsRequest, StockLatestQuoteRequest,
    StockLatestBarRequest, StockSnapshotRequest,
)
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime, timedelta
from app.config import settings
from app.services.atr_calculator import calculate_atr
from loguru import logger

class AlpacaMarketData:

    def __init__(self):
        self.client = StockHistoricalDataClient(
            api_key    = settings.alpaca_api_key,
            secret_key = settings.alpaca_secret_key,
        )

    def _tf(self, timeframe: str) -> TimeFrame:
        m = {"1m": TimeFrame(1,TimeFrameUnit.Minute), "5m": TimeFrame(5,TimeFrameUnit.Minute),
             "15m":TimeFrame(15,TimeFrameUnit.Minute),"30m":TimeFrame(30,TimeFrameUnit.Minute),
             "1h": TimeFrame(1,TimeFrameUnit.Hour),   "4h": TimeFrame(4,TimeFrameUnit.Hour),
             "1d": TimeFrame(1,TimeFrameUnit.Day),    "1w": TimeFrame(1,TimeFrameUnit.Week)}
        return m.get(timeframe.lower(), TimeFrame(1, TimeFrameUnit.Day))

    async def get_quote(self, symbol: str) -> dict:
        req = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        q = self.client.get_stock_latest_quote(req)[symbol]
        return {
            "symbol":    symbol,
            "ask_price": float(q.ask_price),
            "bid_price": float(q.bid_price),
            "spread":    round(float(q.ask_price) - float(q.bid_price), 4),
            "timestamp": str(q.timestamp),
        }

    async def get_bars(self, symbol: str, timeframe: str = "1d", limit: int = 100) -> list:
        req = StockBarsRequest(
            symbol_or_symbols = symbol,
            timeframe         = self._tf(timeframe),
            start             = datetime.utcnow() - timedelta(days=limit * 2),
            limit             = limit,
        )
        bars = self.client.get_stock_bars(req)
        return [{
            "t": str(b.timestamp),
            "o": float(b.open),
            "h": float(b.high),
            "l": float(b.low),
            "c": float(b.close),
            "v": float(b.volume),
        } for b in bars[symbol]]

    async def get_snapshot(self, symbol: str) -> dict:
        """Get full snapshot: latest bar, quote, daily bar, prev daily bar."""
        req = StockSnapshotRequest(symbol_or_symbols=symbol)
        snap = self.client.get_stock_snapshot(req)[symbol]
        return {
            "symbol":         symbol,
            "latest_trade":   float(snap.latest_trade.price) if snap.latest_trade else None,
            "latest_quote":   {"ask": float(snap.latest_quote.ask_price),
                               "bid": float(snap.latest_quote.bid_price)} if snap.latest_quote else None,
            "daily_bar":      {"o": float(snap.daily_bar.open), "h": float(snap.daily_bar.high),
                               "l": float(snap.daily_bar.low),  "c": float(snap.daily_bar.close),
                               "v": float(snap.daily_bar.volume)} if snap.daily_bar else None,
            "prev_daily_bar": {"c": float(snap.previous_daily_bar.close)} if snap.previous_daily_bar else None,
        }

    async def get_atr(self, symbol: str, timeframe: str = "1d", period: int = 14) -> float:
        bars = await self.get_bars(symbol, timeframe, period + 5)
        return calculate_atr(bars, period)

alpaca_data = AlpacaMarketData()
