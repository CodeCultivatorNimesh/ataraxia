"""
Binance spot order management helpers.
"""
from binance.client import Client
from binance.exceptions import BinanceAPIException
from app.config import settings
from loguru import logger

class BinanceOrderManager:

    def __init__(self):
        self.client = Client(
            api_key    = settings.binance_api_key,
            api_secret = settings.binance_secret_key,
            testnet    = settings.binance_testnet,
        )

    def _sym(self, symbol: str) -> str:
        return symbol.replace("/", "").upper()

    async def market_order(self, symbol: str, side: str, qty: float) -> dict:
        s = self._sym(symbol)
        fn = self.client.order_market_buy if side.lower() == "buy" else self.client.order_market_sell
        result = fn(symbol=s, quantity=qty)
        logger.info(f"Binance market: {s} {side} {qty}")
        return {"order_id": str(result["orderId"]), "status": result["status"], "type": "market"}

    async def limit_order(self, symbol: str, side: str, qty: float, price: float) -> dict:
        s = self._sym(symbol)
        fn = self.client.order_limit_buy if side.lower() == "buy" else self.client.order_limit_sell
        result = fn(symbol=s, quantity=qty, price=str(price), timeInForce="GTC")
        logger.info(f"Binance limit: {s} {side} {qty} @ {price}")
        return {"order_id": str(result["orderId"]), "status": result["status"], "type": "limit"}

    async def stop_loss_limit(self, symbol: str, side: str, qty: float,
                               stop_price: float, limit_price: float) -> dict:
        s = self._sym(symbol)
        order_side = "SELL" if side.lower() in ("sell","short") else "BUY"
        result = self.client.create_order(
            symbol=s, side=order_side, type="STOP_LOSS_LIMIT",
            quantity=qty, price=str(limit_price),
            stopPrice=str(stop_price), timeInForce="GTC"
        )
        logger.info(f"Binance stop-loss-limit: {s} {qty} stop@{stop_price} limit@{limit_price}")
        return {"order_id": str(result["orderId"]), "status": result["status"], "type": "stop_loss_limit"}

    async def oco_order(self, symbol: str, side: str, qty: float,
                         price: float, stop_price: float, stop_limit_price: float) -> dict:
        """One-cancels-other: limit take-profit + stop-loss in one call."""
        s = self._sym(symbol)
        result = self.client.create_oco_order(
            symbol=s,
            side="SELL" if side.lower() in ("sell","short") else "BUY",
            quantity=qty,
            price=str(price),
            stopPrice=str(stop_price),
            stopLimitPrice=str(stop_limit_price),
            stopLimitTimeInForce="GTC",
        )
        logger.info(f"Binance OCO: {s} {qty} TP:{price} SL:{stop_price}")
        return {"order_list_id": result["orderListId"], "status": result["listOrderStatus"], "type": "oco"}

    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        try:
            self.client.cancel_order(symbol=self._sym(symbol), orderId=order_id)
            return True
        except BinanceAPIException as e:
            logger.error(f"Cancel error: {e}")
            return False

    async def get_open_orders(self, symbol: str = None) -> list:
        orders = self.client.get_open_orders(symbol=self._sym(symbol) if symbol else None)
        return [{
            "order_id": str(o["orderId"]),
            "symbol":   o["symbol"],
            "side":     o["side"],
            "type":     o["type"],
            "qty":      float(o["origQty"]),
            "price":    float(o["price"]),
            "status":   o["status"],
        } for o in orders]

binance_orders = BinanceOrderManager()
