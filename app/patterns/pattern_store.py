from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.pattern import CandlestickPattern, PatternAlert
from datetime import datetime

class PatternStore:

    async def save_detections(self, db: AsyncSession, symbol: str, timeframe: str, patterns: list):
        saved = []
        for p in patterns:
            record = CandlestickPattern(
                symbol       = symbol,
                timeframe    = timeframe,
                pattern_name = p["pattern_name"],
                pattern_type = p["pattern_type"],
                category     = p["category"],
                confidence   = p["confidence"],
                open         = p.get("open"),
                high         = p.get("high"),
                low          = p.get("low"),
                close        = p.get("close"),
                candle_time  = datetime.fromisoformat(p["candle_time"]) if isinstance(p["candle_time"], str) else p["candle_time"],
                description  = p["description"],
            )
            db.add(record)
            saved.append(record)
        await db.commit()
        return saved

    async def save_alerts(self, db: AsyncSession, alerts: list):
        for a in alerts:
            record = PatternAlert(
                symbol       = a["symbol"],
                pattern_name = a["pattern_name"],
                pattern_type = a["pattern_type"],
                timeframe    = a["timeframe"],
                message      = a["message"],
                confidence   = a["confidence"],
                price        = a["price"],
            )
            db.add(record)
        await db.commit()

    async def get_recent(self, db: AsyncSession, symbol: str, timeframe: str = None, limit: int = 50):
        q = select(CandlestickPattern).where(CandlestickPattern.symbol == symbol)
        if timeframe:
            q = q.where(CandlestickPattern.timeframe == timeframe)
        q = q.order_by(desc(CandlestickPattern.detected_at)).limit(limit)
        result = await db.execute(q)
        return result.scalars().all()

    async def get_unread_alerts(self, db: AsyncSession, limit: int = 20):
        q = select(PatternAlert).where(PatternAlert.is_read == False).order_by(desc(PatternAlert.created_at)).limit(limit)
        result = await db.execute(q)
        return result.scalars().all()

pattern_store = PatternStore()
