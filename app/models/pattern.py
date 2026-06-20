from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database.connection import Base

class CandlestickPattern(Base):
    __tablename__ = "candlestick_patterns"

    id           = Column(Integer, primary_key=True, index=True)
    symbol       = Column(String(20), nullable=False, index=True)
    timeframe    = Column(String(10), nullable=False)   # 1m, 5m, 15m, 1h, 4h, 1d
    pattern_name = Column(String(50), nullable=False, index=True)
    pattern_type = Column(String(20))                   # bullish / bearish / neutral
    category     = Column(String(20))                   # single / double / triple / continuation
    confidence   = Column(Float)                        # 0.0 to 1.0
    open         = Column(Float)
    high         = Column(Float)
    low          = Column(Float)
    close        = Column(Float)
    volume       = Column(Float)
    candle_time  = Column(DateTime(timezone=True), nullable=False, index=True)
    detected_at  = Column(DateTime(timezone=True), server_default=func.now())
    alert_sent   = Column(Boolean, default=False)
    description  = Column(Text)

class PatternAlert(Base):
    __tablename__ = "pattern_alerts"

    id           = Column(Integer, primary_key=True, index=True)
    symbol       = Column(String(20), nullable=False)
    pattern_name = Column(String(50), nullable=False)
    pattern_type = Column(String(20))
    timeframe    = Column(String(10))
    message      = Column(Text)
    confidence   = Column(Float)
    price        = Column(Float)
    is_read      = Column(Boolean, default=False)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
