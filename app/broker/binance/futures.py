from binance.client import Client
from binance.exceptions import BinanceAPIException
from app.config import settings
from loguru import logger

class BinanceFuturesClient:

    def __init__(self):
        self.client = Client(
            api_key    = settings.binance_api_key,
            api_secret = settings.binance_secret_key,
            testnet    = settings.binance_testnet
        )

    async def get_account(self) -> dict:
        acc = self.client.futures_account()
        return {
            "total_balance":  float(acc["totalWalletBalance"]),
            "available":      float(acc["availableBalance"]),
            "unrealized_pnl": float(acc["totalUnrealizedProfit"]),
            "margin_balance": float(acc["totalMarginBalance"]),
        }

    async def get_positions(self) -> list:
        positions = self.client.futures_position_information()
        return [{
            "symbol":          p["symbol"],
            "side":            p["positionSide"],
            "qty":             float(p["positionAmt"]),
            "entry_price":     float(p["entryPrice"]),
            "unrealized_pnl":  float(p["unRealizedProfit"]),
            "leverage":        float(p["leverage"]),
            "margin_type":     p["marginType"],  # cross / isolated
            "liquidation_price": float(p["liquidationPrice"]),
        } for p in positions if float(p["positionAmt"]) != 0]

    async def set_leverage(self, symbol: str, leverage: int) -> dict:
        result = self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
        logger.info(f"Binance leverage set: {symbol} → {leverage}×")
        return result

    async def set_margin_mode(self, symbol: str, mode: str) -> bool:
        """mode: 'CROSSED' or 'ISOLATED'"""
        try:
            self.client.futures_change_margin_type(symbol=symbol, marginType=mode.upper())
            logger.info(f"Binance margin mode: {symbol} → {mode}")
            return True
        except BinanceAPIException as e:
            if "No need to change margin type" in str(e):
                return True
            raise

    async def place_futures_order(
        self,
        symbol: str,
        side: str,
        qty: float,
        leverage: int,
        margin_mode: str = "CROSS",
        order_type: str = "MARKET",
        reduce_only: bool = False
    ) -> dict:
        clean = symbol.replace("/", "")
        await self.set_margin_mode(clean, "CROSSED" if margin_mode == "CROSS" else "ISOLATED")
        await self.set_leverage(clean, leverage)
        params = {
            "symbol":     clean,
            "side":       "BUY" if side == "long" else "SELL",
            "type":       order_type,
            "quantity":   qty,
            "reduceOnly": reduce_only,
        }
        result = self.client.futures_create_order(**params)
        logger.info(f"Binance futures order: {clean} {side} {qty} {leverage}× {margin_mode}")
        return {
            "order_id":    str(result["orderId"]),
            "symbol":      clean,
            "side":        side,
            "qty":         qty,
            "leverage":    leverage,
            "margin_mode": margin_mode,
            "status":      result["status"],
            "broker":      "binance_futures",
        }

    async def close_position(self, symbol: str, qty: float, side: str) -> dict:
        close_side = "SELL" if side == "long" else "BUY"
        result = self.client.futures_create_order(
            symbol=symbol.replace("/", ""),
            side=close_side,
            type="MARKET",
            quantity=abs(qty),
            reduceOnly=True,
        )
        return {"status": result["status"], "order_id": str(result["orderId"])}

    async def get_open_positions_count(self) -> int:
        positions = await self.get_positions()
        return len(positions)

    async def check_cross_mode_block(self) -> dict:
        """Enforce: only 1 cross-mode position at a time"""
        positions = await self.get_positions()
        cross_positions = [p for p in positions if p["margin_type"] == "cross"]
        return {
            "has_open_cross_position": len(cross_positions) > 0,
            "cross_position_count":    len(cross_positions),
            "new_cross_trade_allowed": len(cross_positions) == 0,
            "positions":               cross_positions,
        }

    async def check_isolated_slots(self) -> dict:
        """Enforce: max 3 isolated positions at a time"""
        positions = await self.get_positions()
        isolated = [p for p in positions if p["margin_type"] == "isolated"]
        max_slots = settings.max_crypto_positions_isolated
        return {
            "slots_used":      len(isolated),
            "slots_remaining": max(0, max_slots - len(isolated)),
            "new_trade_allowed": len(isolated) < max_slots,
            "positions":       isolated,
        }

binance_futures = BinanceFuturesClient() if settings.binance_api_key and settings.binance_secret_key else None
