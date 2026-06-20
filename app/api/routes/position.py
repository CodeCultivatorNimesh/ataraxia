from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.risk.position_size import PositionSizeCalculator

router = APIRouter()

class SpotRequest(BaseModel):
    account_balance: float
    risk_pct: float = 1.0
    entry_price: float
    atr_value: float
    direction: str = "long"
    volatility: str = "medium"
    asset_type: str = "stock"

class FuturesCrossRequest(BaseModel):
    account_balance: float
    entry_price: float
    atr_value: float
    volatility: str = "medium"
    direction: str = "long"
    maintenance_margin_pct: float = 0.5

class FuturesIsoRequest(BaseModel):
    account_balance: float
    entry_price: float
    atr_value: float
    volatility: str = "medium"
    direction: str = "long"
    open_positions: int = 0

@router.post("/spot")
async def position_spot(req: SpotRequest):
    try:
        result = PositionSizeCalculator.calculate_spot(
            req.account_balance, req.risk_pct, req.entry_price,
            req.atr_value, req.direction, req.volatility, req.asset_type
        )
        return result.__dict__
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/crypto-futures/cross")
async def position_cross(req: FuturesCrossRequest):
    return PositionSizeCalculator.calculate_crypto_futures_cross(
        req.account_balance, req.entry_price, req.atr_value,
        req.volatility, req.direction, req.maintenance_margin_pct
    )

@router.post("/crypto-futures/isolated")
async def position_isolated(req: FuturesIsoRequest):
    return PositionSizeCalculator.calculate_crypto_futures_isolated(
        req.account_balance, req.entry_price, req.atr_value,
        req.volatility, req.direction, req.open_positions
    )
