from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.broker.alpaca.client import alpaca
from app.broker.binance.client import binance_client
from app.broker.binance.futures import binance_futures
from app.broker.base import OrderRequest

router = APIRouter()

class OrderReq(BaseModel):
    broker: str              # alpaca / binance / binance_futures
    symbol: str
    side: str                # buy / sell / long / short
    qty: float
    order_type: str = "market"
    limit_price: Optional[float] = None
    leverage: Optional[int] = None
    margin_mode: Optional[str] = "CROSS"

class AtrRequest(BaseModel):
    broker: str
    symbol: str
    timeframe: str = "1d"
    period: int = 14

def _require(client, name: str):
    if client is None:
        raise HTTPException(503, f"{name} API keys not configured")
    return client

@router.get("/account/{broker}")
async def get_account(broker: str):
    try:
        if broker == "alpaca":
            return await _require(alpaca, "Alpaca").get_account()
        elif broker == "binance":
            return await _require(binance_client, "Binance").get_account()
        elif broker == "binance_futures":
            return await _require(binance_futures, "Binance Futures").get_account()
        raise HTTPException(400, f"Unknown broker: {broker}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/positions/{broker}")
async def get_positions(broker: str):
    try:
        if broker == "alpaca":
            return await _require(alpaca, "Alpaca").get_positions()
        elif broker == "binance":
            return await _require(binance_client, "Binance").get_positions()
        elif broker == "binance_futures":
            return await _require(binance_futures, "Binance Futures").get_positions()
        raise HTTPException(400, f"Unknown broker: {broker}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/price/{broker}/{symbol}")
async def get_price(broker: str, symbol: str):
    try:
        if broker == "alpaca":
            price = await _require(alpaca, "Alpaca").get_price(symbol)
        elif broker in ("binance", "binance_futures"):
            price = await _require(binance_client, "Binance").get_price(symbol)
        else:
            raise HTTPException(400, f"Unknown broker: {broker}")
        return {"symbol": symbol, "price": price, "broker": broker}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/candles/{broker}/{symbol}")
async def get_candles(broker: str, symbol: str, timeframe: str = "1d", limit: int = 50):
    try:
        if broker == "alpaca":
            return await _require(alpaca, "Alpaca").get_candles(symbol, timeframe, limit)
        elif broker in ("binance", "binance_futures"):
            return await _require(binance_client, "Binance").get_candles(symbol, timeframe, limit)
        raise HTTPException(400, f"Unknown broker: {broker}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/atr")
async def get_atr(req: AtrRequest):
    try:
        if req.broker == "alpaca":
            atr = await _require(alpaca, "Alpaca").calculate_atr(req.symbol, req.timeframe, req.period)
        elif req.broker in ("binance", "binance_futures"):
            atr = await _require(binance_client, "Binance").calculate_atr(req.symbol, req.timeframe, req.period)
        else:
            raise HTTPException(400, f"Unknown broker: {req.broker}")
        return {"symbol": req.symbol, "atr": atr, "timeframe": req.timeframe, "period": req.period}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/order")
async def place_order(req: OrderReq):
    try:
        if req.broker == "alpaca":
            order = OrderRequest(symbol=req.symbol, side=req.side, qty=req.qty,
                                 order_type=req.order_type, limit_price=req.limit_price)
            return (await _require(alpaca, "Alpaca").place_order(order)).__dict__
        elif req.broker == "binance":
            order = OrderRequest(symbol=req.symbol, side=req.side, qty=req.qty,
                                 order_type=req.order_type, limit_price=req.limit_price)
            return (await _require(binance_client, "Binance").place_order(order)).__dict__
        elif req.broker == "binance_futures":
            return await _require(binance_futures, "Binance Futures").place_futures_order(
                symbol=req.symbol, side=req.side, qty=req.qty,
                leverage=req.leverage or 1, margin_mode=req.margin_mode or "CROSS"
            )
        raise HTTPException(400, f"Unknown broker: {req.broker}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/futures/cross-check")
async def cross_mode_check():
    return await _require(binance_futures, "Binance Futures").check_cross_mode_block()

@router.get("/futures/isolated-slots")
async def isolated_slots():
    return await _require(binance_futures, "Binance Futures").check_isolated_slots()
