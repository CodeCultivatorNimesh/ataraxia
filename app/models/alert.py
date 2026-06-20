"""
Alert models for pattern and risk notifications.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database.connection import Base


class RiskAlert(Base):
    __tablename__ = "risk_alerts"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, default=1, index=True)
    alert_type   = Column(String(30), nullable=False)   # risk / behavioral / pattern
    severity     = Column(String(10), nullable=False)   # LOW / MEDIUM / HIGH / CRITICAL
    title        = Column(String(100), nullable=False)
    message      = Column(Text, nullable=False)
    symbol       = Column(String(20))
    value        = Column(Float)                        # the triggering value
    threshold    = Column(Float)                        # the limit that was breached
    is_read      = Column(Boolean, default=False)
    is_resolved  = Column(Boolean, default=False)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at  = Column(DateTime(timezone=True))


# Re-export PatternAlert so callers can import from here
from app.models.pattern import PatternAlert

__all__ = ["RiskAlert", "PatternAlert"]
