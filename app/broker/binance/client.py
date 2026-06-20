from binance.client import Client
from binance.exceptions import BinanceAPIException
from app.config import settings
from app.broker.base import BrokerBase, OrderRequest, OrderResult
from loguru import logger

class BinanceClient(BrokerBase):

    def __init__(self):
        self.client = Client(
            api_key    = settings.binance_api_key,
            api_secret = settings.binance_secret_key,
            testnet    = settings.binance_testnet
        )

    async def get_account(self) -> dict:
        acc = self.client.get_account()
        balances = {b["asset"]: float(b["free"]) for b in acc["balances"] if float(b["free"]) > 0}
        return {"broker": "binance", "balances": balances, "can_trade": acc["canTrade"]}

    async def get_futures_account(self) -> dict:
        acc = self.client.futures_account()
        return {
            "broker":          "binance_futures",
            "total_balance":   float(acc["totalWalletBalance"]),
            "available":       float(acc["availableBalance"]),
            "unrealized_pnl":  float(acc["totalUnrealizedProfit"]),
            "margin_balance":  float(acc["totalMarginBalance"]),
        }

    async def place_order(self, order: OrderRequest) -> OrderResult:
        side = "BUY" if order.side == "buy" else "SELL"
        try:
            if order.order_type == "market":
                result = self.client.order_market(
                    symbol=order.symbol.replace("/", ""),
                    side=side,
                    quantity=order.qty
                )
            else:
                result = self.client.order_limit(
                    symbol=order.symbol.replace("/", ""),
                    side=side,
                    quantity=order.qty,
                    price=str(order.limit_price),
                    timeInForce="GTC"
                )
            logger.info(f"Binance spot order placed: {order.symbol} {order.side} {order.qty}")
            return OrderResult(
                order_id=str(result["orderId"]),
                symbol=order.symbol,
                side=order.side,
                qty=order.qty,
                status=result["status"],
                broker="binance"
            )
        except BinanceAPIException as e:
            logger.error(f"Binance order error: {e}")
            raise

    async def cancel_order(self, order_id: str, symbol: str = None) -> bool:
        try:
            self.client.cancel_order(symbol=symbol, orderId=order_id)
            return True
        except Exception as e:
            logger.error(f"Cancel error: {e}")
            return False

    async def get_positions(self) -> list:
        acc = self.client.get_account()
        return [{
            "symbol":  b["asset"],
            "qty":     float(b["free"]),
            "locked":  float(b["locked"]),
            "broker":  "binance"
        } for b in acc["balances"] if float(b["free"]) > 0 or float(b["locked"]) > 0]

    async def get_price(self, symbol: str) -> float:
        ticker = self.client.get_symbol_ticker(symbol=symbol.replace("/", ""))
        return float(ticker["price"])

    async def get_candles(self, symbol: str, timeframe: str = "1d", limit: int = 50) -> list:
        tf_map = {"1m":"1m","5m":"5m","15m":"15m","30m":"30m","1h":"1h","4h":"4h","1d":"1d","1w":"1w"}
        tf = tf_map.get(timeframe.lower(), "1d")
        klines = self.client.get_klines(
            symbol=symbol.replace("/", ""),
            interval=tf,
            limit=limit
        )
        return [{
            "t": str(k[0]),
            "o": float(k[1]),
            "h": float(k[2]),
            "l": float(k[3]),
            "c": float(k[4]),
            "v": float(k[5]),
        } for k in klines]

    async def calculate_atr(self, symbol: str, timeframe: str = "1d", period: int = 14) -> float:
        candles = await self.get_candles(symbol, timeframe, period + 5)
        if len(candles) < period:
            return 0.0
        trs = []
        for i in range(1, len(candles)):
            h, l, pc = candles[i]["h"], candles[i]["l"], candles[i-1]["c"]
            trs.append(max(h - l, abs(h - pc), abs(l - pc)))
        return round(sum(trs[-period:]) / period, 4)

binance_client = BinanceClient() if settings.binance_api_key and settings.binance_secret_key else None
