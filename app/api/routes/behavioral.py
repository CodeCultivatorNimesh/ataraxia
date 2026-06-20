from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database.connection import get_db
from app.models.behavioral import BehavioralMetric
from app.models.trade import Trade
from app.psychology.behavioral_engine import behavioral_engine
from app.psychology.bias_detector import bias_detector
from app.psychology.decision_engine import decision_engine
from typing import Optional

router = APIRouter()

class BehavioralRequest(BaseModel):
    stress_level: int = 5
    sleep_hours: float = 7.0
    daily_loss_pct: float = 0.0
    trade_limit: int = 20

class DecisionRequest(BaseModel):
    behavioral_score: int
    daily_loss_pct: float
    consecutive_losses: int = 0
    stress_level: int = 5
    sleep_hours: float = 7.0

@router.post("/analyze")
async def analyze_behavior(req: BehavioralRequest, db: AsyncSession = Depends(get_db)):
    q = select(Trade).order_by(desc(Trade.created_at)).limit(req.trade_limit)
    result = await db.execute(q)
    trades = result.scalars().all()
    trade_dicts = [{
        "pnl": t.pnl or 0, "quantity": t.quantity,
        "hold_time": (t.closed_at - t.opened_at).seconds if t.closed_at and t.opened_at else 0,
        "created_at": t.created_at,
    } for t in trades]
    insights = behavioral_engine.analyze(trade_dicts, req.stress_level, req.sleep_hours, req.daily_loss_pct)
    biases = bias_detector.detect(trade_dicts)
    metric = BehavioralMetric(
        behavioral_score   = insights["emotional_score"],
        revenge_trading    = insights["revenge_trading"],
        overtrading        = insights["overtrading"],
        loss_aversion      = insights["loss_aversion"],
        overconfidence     = insights["overconfidence"],
        recency_bias       = insights["recency_bias"],
        consecutive_losses = sum(1 for t in trade_dicts if t["pnl"] < 0),
        stress_level       = req.stress_level,
        sleep_hours        = req.sleep_hours,
        daily_loss_pct     = req.daily_loss_pct,
    )
    db.add(metric)
    await db.commit()
    return {
        "behavioral_score": insights["emotional_score"],
        "insights":         insights,
        "biases":           biases,
        "trade_count":      len(trades),
    }

@router.post("/decision")
async def get_trade_decision(req: DecisionRequest):
    return decision_engine.evaluate(
        req.behavioral_score, req.daily_loss_pct,
        req.consecutive_losses, req.stress_level, req.sleep_hours
    )

@router.get("/history")
async def behavioral_history(limit: int = 30, db: AsyncSession = Depends(get_db)):
    q = select(BehavioralMetric).order_by(desc(BehavioralMetric.recorded_at)).limit(limit)
    result = await db.execute(q)
    records = result.scalars().all()
    return [{
        "id": r.id, "behavioral_score": r.behavioral_score,
        "revenge_trading": r.revenge_trading, "overtrading": r.overtrading,
        "loss_aversion": r.loss_aversion, "stress_level": r.stress_level,
        "sleep_hours": r.sleep_hours, "daily_loss_pct": r.daily_loss_pct,
        "recorded_at": str(r.recorded_at)
    } for r in records]
