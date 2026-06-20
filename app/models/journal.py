"""
Journal and trade note models.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database.connection import Base


class TradeNote(Base):
    """
    Rich trade notes — pre-trade plan, post-trade review, screenshots.
    Separate from JournalEntry which is auto-generated.
    """
    __tablename__ = "trade_notes"

    id              = Column(Integer, primary_key=True, index=True)
    trade_id        = Column(Integer, ForeignKey("trades.id"), index=True)
    user_id         = Column(Integer, default=1)
    note_type       = Column(String(20), default="general")  # pre / post / general
    content         = Column(Text, nullable=False)
    emotion_score   = Column(Integer)
    strategy_followed = Column(Boolean)
    lesson_learned  = Column(Text)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())


class DailyReview(Base):
    """
    End-of-day review summarising behavioral and performance metrics.
    """
    __tablename__ = "daily_reviews"

    id                  = Column(Integer, primary_key=True, index=True)
    user_id             = Column(Integer, default=1)
    review_date         = Column(DateTime(timezone=True), nullable=False, index=True)
    total_trades        = Column(Integer, default=0)
    winning_trades      = Column(Integer, default=0)
    losing_trades       = Column(Integer, default=0)
    daily_pnl           = Column(Float, default=0.0)
    daily_pnl_pct       = Column(Float, default=0.0)
    behavioral_score    = Column(Integer)
    revenge_trading     = Column(Boolean, default=False)
    overtrading         = Column(Boolean, default=False)
    followed_plan       = Column(Boolean)
    key_mistakes        = Column(Text)
    key_wins            = Column(Text)
    tomorrow_plan       = Column(Text)
    overall_rating      = Column(Integer)   # 1-10 self-rating
    created_at          = Column(DateTime(timezone=True), server_default=func.now())


# Re-export JournalEntry so callers can import from here
from app.models.behavioral import JournalEntry

__all__ = ["TradeNote", "DailyReview", "JournalEntry"]
