from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database.connection import get_db
from app.models.behavioral import JournalEntry
from app.models.trade import Trade
from typing import Optional
from datetime import datetime

router = APIRouter()

class JournalCreateRequest(BaseModel):
    trade_id: Optional[int] = None
    emotion_score: int = 50
    pre_trade_notes: Optional[str] = None
    post_trade_notes: Optional[str] = None
    auto_notes: Optional[str] = None
    warnings: Optional[str] = None

class TradeCreateRequest(BaseModel):
    symbol: str
    asset_class: str = "STOCK"
    direction: str = "LONG"
    broker: Optional[str] = None
    margin_mode: str = "NONE"
    leverage: float = 1.0
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    quantity: float
    risk_amount: Optional[float] = None
    risk_pct: Optional[float] = None
    atr_value: Optional[float] = None
    emotion_score: Optional[int] = None
    notes: Optional[str] = None
    patterns_at_entry: Optional[str] = None

@router.post("/trade")
async def create_trade(req: TradeCreateRequest, db: AsyncSession = Depends(get_db)):
    trade = Trade(
        symbol=req.symbol, asset_class=req.asset_class,
        direction=req.direction, broker=req.broker,
        margin_mode=req.margin_mode, leverage=req.leverage,
        entry_price=req.entry_price, stop_loss=req.stop_loss,
        take_profit=req.take_profit, quantity=req.quantity,
        risk_amount=req.risk_amount, risk_pct=req.risk_pct,
        atr_value=req.atr_value, emotion_score=req.emotion_score,
        notes=req.notes, patterns_at_entry=req.patterns_at_entry,
        is_open=True
    )
    db.add(trade)
    await db.commit()
    await db.refresh(trade)
    return {"id": trade.id, "symbol": trade.symbol, "status": "created"}

@router.patch("/trade/{trade_id}/close")
async def close_trade(trade_id: int, exit_price: float, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    trade = result.scalar_one_or_none()
    if not trade:
        return {"error": "Trade not found"}
    trade.exit_price = exit_price
    trade.is_open = False
    trade.closed_at = datetime.utcnow()
    direction_mult = 1 if trade.direction == "LONG" else -1
    trade.pnl = (exit_price - trade.entry_price) * trade.quantity * direction_mult
    trade.pnl_pct = trade.pnl / (trade.entry_price * trade.quantity) * 100
    await db.commit()
    return {"id": trade.id, "pnl": trade.pnl, "pnl_pct": trade.pnl_pct, "status": "closed"}

@router.get("/trades")
async def get_trades(
    limit: int = Query(50), is_open: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    q = select(Trade).order_by(desc(Trade.created_at)).limit(limit)
    if is_open is not None:
        q = q.where(Trade.is_open == is_open)
    result = await db.execute(q)
    trades = result.scalars().all()
    return [{
        "id": t.id, "symbol": t.symbol, "direction": t.direction,
        "asset_class": t.asset_class, "entry_price": t.entry_price,
        "exit_price": t.exit_price, "quantity": t.quantity,
        "pnl": t.pnl, "pnl_pct": t.pnl_pct, "is_open": t.is_open,
        "emotion_score": t.emotion_score, "patterns_at_entry": t.patterns_at_entry,
        "opened_at": str(t.opened_at), "closed_at": str(t.closed_at) if t.closed_at else None,
    } for t in trades]

@router.post("/entry")
async def create_journal_entry(req: JournalCreateRequest, db: AsyncSession = Depends(get_db)):
    entry = JournalEntry(
        trade_id=req.trade_id, emotion_score=req.emotion_score,
        pre_trade_notes=req.pre_trade_notes, post_trade_notes=req.post_trade_notes,
        auto_notes=req.auto_notes, warnings=req.warnings
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return {"id": entry.id, "status": "created"}

@router.get("/entries")
async def get_journal_entries(limit: int = Query(50), db: AsyncSession = Depends(get_db)):
    q = select(JournalEntry).order_by(desc(JournalEntry.created_at)).limit(limit)
    result = await db.execute(q)
    entries = result.scalars().all()
    return [{
        "id": e.id, "trade_id": e.trade_id, "emotion_score": e.emotion_score,
        "pre_trade_notes": e.pre_trade_notes, "post_trade_notes": e.post_trade_notes,
        "auto_notes": e.auto_notes, "warnings": e.warnings,
        "created_at": str(e.created_at)
    } for e in entries]
