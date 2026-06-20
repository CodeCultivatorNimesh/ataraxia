"""
Alpaca order management helpers.
Wraps the trading client with order-specific utilities.
"""
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    MarketOrderRequest, LimitOrderRequest,
    StopOrderRequest, StopLimitOrderRequest,
    TrailingStopOrderRequest,
)
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from app.config import settings
from loguru import logger

class AlpacaOrderManager:

    def __init__(self):
        self.client = TradingClient(
            api_key    = settings.alpaca_api_key,
            secret_key = settings.alpaca_secret_key,
            paper      = "paper" in settings.alpaca_base_url,
        )

    def _side(self, side: str) -> OrderSide:
        return OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL

    def _tif(self, tif: str) -> TimeInForce:
        mapping = {"gtc": TimeInForce.GTC, "day": TimeInForce.DAY, "ioc": TimeInForce.IOC}
        return mapping.get(tif.lower(), TimeInForce.GTC)

    async def market_order(self, symbol: str, side: str, qty: float, tif: str = "day") -> dict:
        req = MarketOrderRequest(symbol=symbol, qty=qty, side=self._side(side), time_in_force=self._tif(tif))
        result = self.client.submit_order(req)
        logger.info(f"Alpaca market order: {symbol} {side} {qty}")
        return {"order_id": str(result.id), "status": str(result.status), "type": "market"}

    async def limit_order(self, symbol: str, side: str, qty: float, limit_price: float, tif: str = "gtc") -> dict:
        req = LimitOrderRequest(symbol=symbol, qty=qty, side=self._side(side),
                                limit_price=limit_price, time_in_force=self._tif(tif))
        result = self.client.submit_order(req)
        logger.info(f"Alpaca limit order: {symbol} {side} {qty} @ {limit_price}")
        return {"order_id": str(result.id), "status": str(result.status), "type": "limit"}

    async def stop_order(self, symbol: str, side: str, qty: float, stop_price: float) -> dict:
        req = StopOrderRequest(symbol=symbol, qty=qty, side=self._side(side),
                               stop_price=stop_price, time_in_force=TimeInForce.GTC)
        result = self.client.submit_order(req)
        logger.info(f"Alpaca stop order: {symbol} {side} {qty} stop@{stop_price}")
        return {"order_id": str(result.id), "status": str(result.status), "type": "stop"}

    async def bracket_order(self, symbol: str, side: str, qty: float,
                            take_profit: float, stop_loss: float) -> dict:
        """Place entry + take profit + stop loss in one order."""
        from alpaca.trading.requests import OrderRequest
        req = MarketOrderRequest(
            symbol=symbol, qty=qty, side=self._side(side),
            time_in_force=TimeInForce.DAY,
            order_class="bracket",
            take_profit={"limit_price": take_profit},
            stop_loss={"stop_price": stop_loss},
        )
        result = self.client.submit_order(req)
        logger.info(f"Alpaca bracket: {symbol} {side} {qty} TP:{take_profit} SL:{stop_loss}")
        return {"order_id": str(result.id), "status": str(result.status), "type": "bracket"}

    async def get_open_orders(self) -> list:
        orders = self.client.get_orders()
        return [{
            "order_id": str(o.id),
            "symbol":   o.symbol,
            "side":     str(o.side),
            "qty":      float(o.qty),
            "type":     str(o.order_type),
            "status":   str(o.status),
        } for o in orders]

    async def cancel_all_orders(self) -> bool:
        self.client.cancel_orders()
        logger.info("All Alpaca orders cancelled")
        return True

alpaca_orders = AlpacaOrderManager()
