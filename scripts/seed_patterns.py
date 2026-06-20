"""
Seed the pattern_catalog table with all supported candlestick patterns.
Usage: python scripts/seed_patterns.py
"""
import asyncio
import sys
sys.path.append(".")

from app.database.connection import AsyncSessionLocal, init_db
from sqlalchemy import text
from loguru import logger

PATTERNS = [
    # (name, category, type, description, reliability)
    ("Doji", "single", "neutral", "Open and close nearly equal — market indecision", "medium"),
    ("Hammer", "single", "bullish", "Long lower wick — buyers rejected lows strongly", "high"),
    ("Inverted Hammer", "single", "bullish", "Long upper wick after downtrend — potential reversal", "medium"),
    ("Shooting Star", "single", "bearish", "Long upper wick after uptrend — sellers taking control", "high"),
    ("Hanging Man", "single", "bearish", "Hammer shape after uptrend — bearish reversal warning", "medium"),
    ("Spinning Top", "single", "neutral", "Small body with equal wicks — indecision", "low"),
    ("Bullish Marubozu", "single", "bullish", "Full body candle, no wicks — strong bullish momentum", "high"),
    ("Bearish Marubozu", "single", "bearish", "Full body candle, no wicks — strong bearish momentum", "high"),
    ("Dragonfly Doji", "single", "bullish", "Long lower wick, no upper wick — buyers rejected lows", "high"),
    ("Gravestone Doji", "single", "bearish", "Long upper wick, no lower wick — sellers rejected highs", "high"),
    ("Long-Legged Doji", "single", "neutral", "Long upper and lower wicks — extreme uncertainty", "medium"),
    ("Bullish Engulfing", "double", "bullish", "Bullish candle completely engulfs prior bearish candle", "high"),
    ("Bearish Engulfing", "double", "bearish", "Bearish candle completely engulfs prior bullish candle", "high"),
    ("Bullish Harami", "double", "bullish", "Small bullish candle inside prior large bearish candle", "medium"),
    ("Bearish Harami", "double", "bearish", "Small bearish candle inside prior large bullish candle", "medium"),
    ("Piercing Line", "double", "bullish", "Bullish candle closes above midpoint of prior bearish", "high"),
    ("Dark Cloud Cover", "double", "bearish", "Bearish candle closes below midpoint of prior bullish", "high"),
    ("Tweezer Bottom", "double", "bullish", "Two candles with equal lows — strong support signal", "medium"),
    ("Tweezer Top", "double", "bearish", "Two candles with equal highs — strong resistance signal", "medium"),
    ("On Neck", "double", "bearish", "Bullish candle closes near prior bearish low — continuation", "medium"),
    ("Kicking Bullish", "double", "bullish", "Gap up marubozu after bearish marubozu — very strong reversal", "very high"),
    ("Kicking Bearish", "double", "bearish", "Gap down marubozu after bullish marubozu — very strong reversal", "very high"),
    ("Morning Star", "triple", "bullish", "Three-candle bottom reversal: bearish, small, bullish", "high"),
    ("Evening Star", "triple", "bearish", "Three-candle top reversal: bullish, small, bearish", "high"),
    ("Morning Doji Star", "triple", "bullish", "Morning star with doji middle candle — extra strength", "very high"),
    ("Evening Doji Star", "triple", "bearish", "Evening star with doji middle candle — extra strength", "very high"),
    ("Three White Soldiers", "triple", "bullish", "Three consecutive large bullish candles — strong uptrend", "high"),
    ("Three Black Crows", "triple", "bearish", "Three consecutive large bearish candles — strong downtrend", "high"),
    ("Three Inside Up", "triple", "bullish", "Bullish harami confirmed by third bullish candle", "high"),
    ("Three Inside Down", "triple", "bearish", "Bearish harami confirmed by third bearish candle", "high"),
    ("Three Outside Up", "triple", "bullish", "Bullish engulfing confirmed by third bullish candle", "high"),
    ("Three Outside Down", "triple", "bearish", "Bearish engulfing confirmed by third bearish candle", "high"),
    ("Abandoned Baby Bullish", "triple", "bullish", "Extremely rare — doji gaps below then above — very strong reversal", "very high"),
    ("Abandoned Baby Bearish", "triple", "bearish", "Extremely rare — doji gaps above then below — very strong reversal", "very high"),
    ("Rising Three Methods", "continuation", "bullish", "Three small candles pause within uptrend — continuation signal", "high"),
    ("Falling Three Methods", "continuation", "bearish", "Three small candles pause within downtrend — continuation signal", "high"),
    ("Upside Tasuki Gap", "continuation", "bullish", "Gap up not fully filled — bullish trend continues", "medium"),
    ("Downside Tasuki Gap", "continuation", "bearish", "Gap down not fully filled — bearish trend continues", "medium"),
    ("Three Line Strike Bullish", "continuation", "bullish", "Bullish candle strikes back after three bearish candles", "medium"),
    ("Three Line Strike Bearish", "continuation", "bearish", "Bearish candle strikes back after three bullish candles", "medium"),
    ("Mat Hold", "continuation", "bullish", "Strong uptrend continues after brief consolidation", "high"),
    ("Separating Lines Bullish", "continuation", "bullish", "Same open price, trend resumes bullish", "medium"),
    ("Separating Lines Bearish", "continuation", "bearish", "Same open price, trend resumes bearish", "medium"),
    ("In Neck", "continuation", "bearish", "Weak bullish recovery closes near prior low — bearish continues", "medium"),
    ("Thrusting", "continuation", "neutral", "Recovery closes below midpoint — original trend may continue", "low"),
]

async def seed_patterns():
    await init_db()
    async with AsyncSessionLocal() as db:
        for name, cat, ptype, desc, rel in PATTERNS:
            await db.execute(text("""
                INSERT INTO pattern_catalog (name, category, pattern_type, description, reliability)
                VALUES (:name, :cat, :ptype, :desc, :rel)
                ON CONFLICT (name) DO UPDATE SET
                    description = EXCLUDED.description,
                    reliability = EXCLUDED.reliability
            """), {"name": name, "cat": cat, "ptype": ptype, "desc": desc, "rel": rel})
        await db.commit()
        logger.info(f"Seeded {len(PATTERNS)} candlestick patterns into pattern_catalog")

if __name__ == "__main__":
    asyncio.run(seed_patterns())
