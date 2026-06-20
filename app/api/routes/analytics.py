from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database.connection import get_db
from app.models.trade import Trade
from app.models.behavioral import BehavioralMetric
from app.models.pattern import CandlestickPattern
from app.analytics.performance import full_performance_report, asset_breakdown
from app.analytics.dashboard import build_dashboard_payload
from app.risk.var_engine import historical_var

router = APIRouter()

def _trade_dict(t: Trade) -> dict:
    return {
        "id":          t.id,
        "symbol":      t.symbol,
        "direction":   t.direction,
        "asset_class": t.asset_class,
        "pnl":         t.pnl,
        "pnl_pct":     t.pnl_pct,
        "entry_price": t.entry_price,
        "exit_price":  t.exit_price,
        "quantity":    t.quantity,
        "is_open":     t.is_open,
        "opened_at":   str(t.opened_at) if t.opened_at else None,
        "closed_at":   str(t.closed_at) if t.closed_at else None,
        "created_at":  str(t.created_at) if t.created_at else None,
    }

@router.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db)):
    trades_q = await db.execute(
        select(Trade).order_by(desc(Trade.created_at)).limit(200)
    )
    trades = [_trade_dict(t) for t in trades_q.scalars().all()]
    closed = [t for t in trades if not t["is_open"] and t["pnl"] is not None]
    open_trades = [t for t in trades if t["is_open"]]

    bs_q = await db.execute(
        select(BehavioralMetric).order_by(desc(BehavioralMetric.recorded_at)).limit(1)
    )
    latest_bs = bs_q.scalar_one_or_none()
    behavioral_score = latest_bs.behavioral_score if latest_bs else 100

    pattern_q = await db.execute(
        select(CandlestickPattern.pattern_name, func.count(CandlestickPattern.id).label("count"))
        .group_by(CandlestickPattern.pattern_name)
        .order_by(desc("count")).limit(5)
    )
    top_patterns = [{"pattern": r.pattern_name, "count": r.count} for r in pattern_q]

    payload = build_dashboard_payload(
        trades=closed,
        behavioral_score=behavioral_score,
        open_trades=open_trades,
        top_patterns=top_patterns,
    )
    return payload

@router.get("/performance")
async def performance(db: AsyncSession = Depends(get_db)):
    trades_q = await db.execute(
        select(Trade).where(Trade.is_open == False).order_by(Trade.closed_at)
    )
    trades = [_trade_dict(t) for t in trades_q.scalars().all()]
    closed = [t for t in trades if t["pnl"] is not None]
    report = full_performance_report(closed)
    report.pop("equity_curve", None)  # return separately
    return report

@router.get("/performance/equity-curve")
async def equity_curve(db: AsyncSession = Depends(get_db)):
    trades_q = await db.execute(
        select(Trade).where(Trade.is_open == False).order_by(Trade.closed_at)
    )
    trades = [_trade_dict(t) for t in trades_q.scalars().all()]
    closed = [t for t in trades if t["pnl"] is not None]
    report = full_performance_report(closed)
    return {"equity_curve": report["equity_curve"]}

@router.get("/performance/by-asset")
async def performance_by_asset(db: AsyncSession = Depends(get_db)):
    trades_q = await db.execute(
        select(Trade).where(Trade.is_open == False)
    )
    trades = [_trade_dict(t) for t in trades_q.scalars().all()]
    return asset_breakdown([t for t in trades if t["pnl"] is not None])

@router.get("/var")
async def portfolio_var(db: AsyncSession = Depends(get_db)):
    trades_q = await db.execute(
        select(Trade).where(Trade.is_open == False, Trade.pnl_pct != None)
        .order_by(desc(Trade.closed_at)).limit(200)
    )
    trades = trades_q.scalars().all()
    returns = [t.pnl_pct for t in trades if t.pnl_pct is not None]
    if len(returns) < 5:
        return {"error": "Not enough trade history. Need at least 5 closed trades."}
    return historical_var(returns)

@router.get("/patterns/summary")
async def pattern_summary(days: int = Query(30), db: AsyncSession = Depends(get_db)):
    q = await db.execute(
        select(
            CandlestickPattern.pattern_name,
            CandlestickPattern.pattern_type,
            CandlestickPattern.category,
            func.count(CandlestickPattern.id).label("count"),
            func.avg(CandlestickPattern.confidence).label("avg_confidence"),
        )
        .group_by(
            CandlestickPattern.pattern_name,
            CandlestickPattern.pattern_type,
            CandlestickPattern.category,
        )
        .order_by(desc("count"))
    )
    rows = q.all()
    return [{
        "pattern_name":     r.pattern_name,
        "pattern_type":     r.pattern_type,
        "category":         r.category,
        "count":            r.count,
        "avg_confidence":   round(float(r.avg_confidence), 2),
    } for r in rows]
