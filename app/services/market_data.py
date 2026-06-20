"""
Market data service — unified interface over Alpaca and Binance.
Fetches live prices, candles, and calculates ATR automatically.
"""
from app.services.atr_calculator import calculate_atr
from app.services.cache import cache
from loguru import logger

async def get_live_price(broker: str, symbol: str) -> float:
    cache_key = f"price:{broker}:{symbol}"
    cached = await cache.get(cache_key)
    if cached:
        return cached["price"]
    try:
        if broker == "alpaca":
            from app.broker.alpaca.client import alpaca
            price = await alpaca.get_price(symbol)
        else:
            from app.broker.binance.client import binance_client
            price = await binance_client.get_price(symbol)
        await cache.set(cache_key, {"price": price}, ttl=10)
        return price
    except Exception as e:
        logger.error(f"Price fetch error {broker}/{symbol}: {e}")
        return 0.0

async def get_live_atr(broker: str, symbol: str, timeframe: str = "1d", period: int = 14) -> float:
    cache_key = f"atr:{broker}:{symbol}:{timeframe}:{period}"
    cached = await cache.get(cache_key)
    if cached:
        return cached["atr"]
    try:
        if broker == "alpaca":
            from app.broker.alpaca.client import alpaca
            candles = await alpaca.get_candles(symbol, timeframe, period + 5)
        else:
            from app.broker.binance.client import binance_client
            candles = await binance_client.get_candles(symbol, timeframe, period + 5)
        atr = calculate_atr(candles, period)
        await cache.set(cache_key, {"atr": atr}, ttl=300)
        return atr
    except Exception as e:
        logger.error(f"ATR fetch error {broker}/{symbol}: {e}")
        return 0.0

async def get_candles_with_patterns(broker: str, symbol: str, timeframe: str = "1d", limit: int = 50) -> dict:
    from app.patterns.detector import PatternDetector
    from app.config import settings
    try:
        if broker == "alpaca":
            from app.broker.alpaca.client import alpaca
            candles = await alpaca.get_candles(symbol, timeframe, limit)
        else:
            from app.broker.binance.client import binance_client
            candles = await binance_client.get_candles(symbol, timeframe, limit)
        det = PatternDetector(settings.pattern_min_confidence)
        patterns = det.detect_all(candles)
        summary = det.summary(patterns)
        atr = calculate_atr(candles)
        return {
            "symbol":   symbol,
            "broker":   broker,
            "timeframe": timeframe,
            "candles":  candles,
            "atr":      atr,
            "patterns": summary,
        }
    except Exception as e:
        logger.error(f"Candles+patterns error {broker}/{symbol}: {e}")
        return {"error": str(e)}
