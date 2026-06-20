from sqlalchemy import Column, Integer, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database.connection import Base

class BehavioralMetric(Base):
    __tablename__ = "behavioral_metrics"

    id                  = Column(Integer, primary_key=True, index=True)
    user_id             = Column(Integer, index=True, default=1)
    behavioral_score    = Column(Integer)
    revenge_trading     = Column(Boolean, default=False)
    overtrading         = Column(Boolean, default=False)
    loss_aversion       = Column(Boolean, default=False)
    fomo_detected       = Column(Boolean, default=False)
    overconfidence      = Column(Boolean, default=False)
    recency_bias        = Column(Boolean, default=False)
    consecutive_losses  = Column(Integer, default=0)
    stress_level        = Column(Integer)
    sleep_hours         = Column(Float)
    daily_loss_pct      = Column(Float)
    notes               = Column(Text)
    recorded_at         = Column(DateTime(timezone=True), server_default=func.now())

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id              = Column(Integer, primary_key=True, index=True)
    trade_id        = Column(Integer, index=True)
    user_id         = Column(Integer, default=1)
    emotion_score   = Column(Integer)
    pre_trade_notes = Column(Text)
    post_trade_notes= Column(Text)
    auto_notes      = Column(Text)    # system-generated behavioral notes
    warnings        = Column(Text)    # JSON list of warnings
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
