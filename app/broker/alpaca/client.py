from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from app.config import settings
from app.broker.base import BrokerBase, OrderRequest, OrderResult
from datetime import datetime, timedelta
from loguru import logger

class AlpacaClient(BrokerBase):

    def __init__(self):
        self.trading = TradingClient(
            api_key    = settings.alpaca_api_key,
            secret_key = settings.alpaca_secret_key,
            paper      = "paper" in settings.alpaca_base_url
        )
        self.data = StockHistoricalDataClient(
            api_key    = settings.alpaca_api_key,
            secret_key = settings.alpaca_secret_key,
        )

    async def get_account(self) -> dict:
        acc = self.trading.get_account()
        return {
            "broker":         "alpaca",
            "balance":        float(acc.equity),
            "cash":           float(acc.cash),
            "buying_power":   float(acc.buying_power),
            "portfolio_value":float(acc.portfolio_value),
            "day_trade_count":acc.daytrade_count,
            "pdt_check":      acc.pattern_day_trader,
        }

    async def place_order(self, order: OrderRequest) -> OrderResult:
        side = OrderSide.BUY if order.side == "buy" else OrderSide.SELL
        tif  = TimeInForce.GTC if order.time_in_force == "gtc" else TimeInForce.DAY
        try:
            if order.order_type == "market":
                req = MarketOrderRequest(symbol=order.symbol, qty=order.qty, side=side, time_in_force=tif)
            else:
                req = LimitOrderRequest(symbol=order.symbol, qty=order.qty, side=side,
                                        limit_price=order.limit_price, time_in_force=tif)
            result = self.trading.submit_order(req)
            logger.info(f"Alpaca order placed: {order.symbol} {order.side} {order.qty}")
            return OrderResult(
                order_id=str(result.id), symbol=order.symbol, side=order.side,
                qty=order.qty, status=str(result.status), broker="alpaca"
            )
        except Exception as e:
            logger.error(f"Alpaca order error: {e}")
            raise

    async def cancel_order(self, order_id: str) -> bool:
        try:
            self.trading.cancel_order_by_id(order_id)
            return True
        except Exception as e:
            logger.error(f"Cancel error: {e}")
            return False

    async def get_positions(self) -> list:
        positions = self.trading.get_all_positions()
        return [{
            "symbol":     p.symbol,
            "qty":        float(p.qty),
            "side":       p.side,
            "avg_entry":  float(p.avg_entry_price),
            "market_val": float(p.market_value),
            "unrealized_pnl": float(p.unrealized_pl),
            "unrealized_pnl_pct": float(p.unrealized_plpc),
            "broker":     "alpaca"
        } for p in positions]

    async def get_price(self, symbol: str) -> float:
        req = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        quote = self.data.get_stock_latest_quote(req)
        return float(quote[symbol].ask_price)

    async def get_candles(self, symbol: str, timeframe: str = "1Day", limit: int = 50) -> list:
        tf_map = {
            "1m": TimeFrame(1, TimeFrameUnit.Minute),
            "5m": TimeFrame(5, TimeFrameUnit.Minute),
            "15m": TimeFrame(15, TimeFrameUnit.Minute),
            "1h": TimeFrame(1, TimeFrameUnit.Hour),
            "4h": TimeFrame(4, TimeFrameUnit.Hour),
            "1d": TimeFrame(1, TimeFrameUnit.Day),
        }
        tf = tf_map.get(timeframe.lower(), TimeFrame(1, TimeFrameUnit.Day))
        req = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=tf,
            start=datetime.utcnow() - timedelta(days=limit * 2),
            limit=limit,
        )
        bars = self.data.get_stock_bars(req)
        return [{
            "t": str(bar.timestamp),
            "o": float(bar.open),
            "h": float(bar.high),
            "l": float(bar.low),
            "c": float(bar.close),
            "v": float(bar.volume),
        } for bar in bars[symbol]]

    async def calculate_atr(self, symbol: str, timeframe: str = "1d", period: int = 14) -> float:
        candles = await self.get_candles(symbol, timeframe, period + 5)
        if len(candles) < period:
            return 0.0
        trs = []
        for i in range(1, len(candles)):
            high, low, prev_close = candles[i]["h"], candles[i]["l"], candles[i-1]["c"]
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            trs.append(tr)
        return round(sum(trs[-period:]) / period, 4)

alpaca = AlpacaClient() if settings.alpaca_api_key and settings.alpaca_secret_key else None
