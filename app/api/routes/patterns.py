from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.patterns.detector import PatternDetector
from app.patterns.alert_engine import alert_engine
from app.patterns.pattern_store import pattern_store
from app.config import settings

router = APIRouter()

class CandleData(BaseModel):
    symbol: str
    timeframe: str = "1d"
    candles: list  # [{o,h,l,c,v,t}]
    current_price: float = 0.0

@router.post("/detect")
async def detect_patterns(req: CandleData, db: AsyncSession = Depends(get_db)):
    det = PatternDetector(settings.pattern_min_confidence)
    results = det.detect_all(req.candles)
    summary = det.summary(results)
    if results:
        await pattern_store.save_detections(db, req.symbol, req.timeframe, results)
        price = req.current_price or (req.candles[-1]["c"] if req.candles else 0)
        alerts = await alert_engine.process_patterns(req.symbol, req.timeframe, results, price)
        await pattern_store.save_alerts(db, alerts)
    return summary

@router.get("/history/{symbol}")
async def pattern_history(
    symbol: str,
    timeframe: str = Query(None),
    limit: int = Query(50),
    db: AsyncSession = Depends(get_db)
):
    records = await pattern_store.get_recent(db, symbol.upper(), timeframe, limit)
    return [{"id": r.id, "pattern_name": r.pattern_name, "pattern_type": r.pattern_type,
             "category": r.category, "confidence": r.confidence, "timeframe": r.timeframe,
             "candle_time": str(r.candle_time), "detected_at": str(r.detected_at)} for r in records]

@router.get("/alerts/unread")
async def unread_alerts(db: AsyncSession = Depends(get_db)):
    alerts = await pattern_store.get_unread_alerts(db)
    return [{"id": a.id, "symbol": a.symbol, "pattern_name": a.pattern_name,
             "message": a.message, "confidence": a.confidence, "created_at": str(a.created_at)} for a in alerts]

@router.get("/catalog")
async def pattern_catalog():
    from app.patterns.single_candle import SINGLE_PATTERNS
    from app.patterns.double_candle import DOUBLE_PATTERNS
    from app.patterns.triple_candle import TRIPLE_PATTERNS
    from app.patterns.continuation import CONTINUATION_PATTERNS
    return {
        "single":       [{"name": k, "type": v["type"], "desc": v["desc"]} for k,v in SINGLE_PATTERNS.items()],
        "double":       [{"name": k, "type": v["type"], "desc": v["desc"]} for k,v in DOUBLE_PATTERNS.items()],
        "triple":       [{"name": k, "type": v["type"], "desc": v["desc"]} for k,v in TRIPLE_PATTERNS.items()],
        "continuation": [{"name": k, "type": v["type"], "desc": v["desc"]} for k,v in CONTINUATION_PATTERNS.items()],
        "total":        len(SINGLE_PATTERNS) + len(DOUBLE_PATTERNS) + len(TRIPLE_PATTERNS) + len(CONTINUATION_PATTERNS)
    }
