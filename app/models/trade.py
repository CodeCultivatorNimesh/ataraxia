from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
from app.database.connection import Base
import enum

class TradeDirection(str, enum.Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class AssetClass(str, enum.Enum):
    STOCK = "STOCK"
    CRYPTO_SPOT = "CRYPTO_SPOT"
    CRYPTO_FUTURES = "CRYPTO_FUTURES"
    FUTURES = "FUTURES"
    FOREX = "FOREX"

class MarginMode(str, enum.Enum):
    CROSS = "CROSS"
    ISOLATED = "ISOLATED"
    NONE = "NONE"

class Trade(Base):
    __tablename__ = "trades"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, index=True, default=1)
    symbol          = Column(String(20), nullable=False)
    asset_class     = Column(String(20), nullable=False)
    direction       = Column(String(10), nullable=False)
    broker          = Column(String(20))              # alpaca / binance
    margin_mode     = Column(String(10), default="NONE")
    leverage        = Column(Float, default=1.0)
    entry_price     = Column(Float, nullable=False)
    exit_price      = Column(Float)
    stop_loss       = Column(Float)
    take_profit     = Column(Float)
    quantity        = Column(Float, nullable=False)
    notional_value  = Column(Float)
    pnl             = Column(Float)
    pnl_pct         = Column(Float)
    risk_amount     = Column(Float)
    risk_pct        = Column(Float)
    atr_value       = Column(Float)
    emotion_score   = Column(Integer)
    is_open         = Column(Boolean, default=True)
    opened_at       = Column(DateTime(timezone=True), server_default=func.now())
    closed_at       = Column(DateTime(timezone=True))
    notes           = Column(Text)
    patterns_at_entry = Column(Text)  # JSON list of detected patterns
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())
