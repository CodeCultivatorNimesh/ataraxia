"""
Binance market data helpers — prices, candles, order book, ticker.
"""
from binance.client import Client
from app.config import settings
from app.services.atr_calculator import calculate_atr
from loguru import logger

class BinanceMarketData:

    def __init__(self):
        self.client = Client(
            api_key    = settings.binance_api_key,
            api_secret = settings.binance_secret_key,
            testnet    = settings.binance_testnet,
        )

    def _sym(self, symbol: str) -> str:
        return symbol.replace("/", "").upper()

    def _tf(self, timeframe: str) -> str:
        m = {"1m":"1m","3m":"3m","5m":"5m","15m":"15m","30m":"30m",
             "1h":"1h","2h":"2h","4h":"4h","6h":"6h","8h":"8h","12h":"12h",
             "1d":"1d","3d":"3d","1w":"1w","1M":"1M"}
        return m.get(timeframe.lower(), "1d")

    async def get_price(self, symbol: str) -> float:
        t = self.client.get_symbol_ticker(symbol=self._sym(symbol))
        return float(t["price"])

    async def get_24h_ticker(self, symbol: str) -> dict:
        t = self.client.get_ticker(symbol=self._sym(symbol))
        return {
            "symbol":        self._sym(symbol),
            "price":         float(t["lastPrice"]),
            "price_change":  float(t["priceChange"]),
            "price_change_pct": float(t["priceChangePercent"]),
            "high":          float(t["highPrice"]),
            "low":           float(t["lowPrice"]),
            "volume":        float(t["volume"]),
            "quote_volume":  float(t["quoteVolume"]),
        }

    async def get_order_book(self, symbol: str, limit: int = 10) -> dict:
        book = self.client.get_order_book(symbol=self._sym(symbol), limit=limit)
        return {
            "symbol": self._sym(symbol),
            "bids":   [[float(b[0]), float(b[1])] for b in book["bids"]],
            "asks":   [[float(a[0]), float(a[1])] for a in book["asks"]],
            "best_bid": float(book["bids"][0][0]) if book["bids"] else 0,
            "best_ask": float(book["asks"][0][0]) if book["asks"] else 0,
        }

    async def get_candles(self, symbol: str, timeframe: str = "1d", limit: int = 100) -> list:
        klines = self.client.get_klines(
            symbol   = self._sym(symbol),
            interval = self._tf(timeframe),
            limit    = limit,
        )
        return [{
            "t": str(k[0]),
            "o": float(k[1]),
            "h": float(k[2]),
            "l": float(k[3]),
            "c": float(k[4]),
            "v": float(k[5]),
        } for k in klines]

    async def get_atr(self, symbol: str, timeframe: str = "1d", period: int = 14) -> float:
        candles = await self.get_candles(symbol, timeframe, period + 5)
        return calculate_atr(candles, period)

    async def get_exchange_info(self, symbol: str) -> dict:
        """Get min order qty, step size, price filters for a symbol."""
        info = self.client.get_symbol_info(self._sym(symbol))
        if not info:
            return {}
        filters = {f["filterType"]: f for f in info["filters"]}
        lot = filters.get("LOT_SIZE", {})
        price_f = filters.get("PRICE_FILTER", {})
        min_notional = filters.get("MIN_NOTIONAL", {})
        return {
            "symbol":       self._sym(symbol),
            "base_asset":   info["baseAsset"],
            "quote_asset":  info["quoteAsset"],
            "min_qty":      float(lot.get("minQty", 0)),
            "max_qty":      float(lot.get("maxQty", 0)),
            "step_size":    float(lot.get("stepSize", 0)),
            "min_price":    float(price_f.get("minPrice", 0)),
            "tick_size":    float(price_f.get("tickSize", 0)),
            "min_notional": float(min_notional.get("minNotional", 0)),
        }

binance_data = BinanceMarketData()
