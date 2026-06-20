from fastapi import APIRouter
from pydantic import BaseModel
from app.risk.engine import RiskEngine

router = APIRouter()
engine = RiskEngine()

class ValidateRequest(BaseModel):
    account_balance: float
    current_daily_loss_pct: float
    risk_pct: float
    open_positions: int
    behavioral_score: int = 100

class VaRRequest(BaseModel):
    returns: list
    confidence: float = 0.95

@router.post("/validate")
async def validate_trade(req: ValidateRequest):
    return engine.validate_trade(
        req.account_balance, req.current_daily_loss_pct,
        req.risk_pct, req.open_positions, req.behavioral_score
    )

@router.post("/var")
async def value_at_risk(req: VaRRequest):
    return engine.calculate_var(req.returns, req.confidence)
