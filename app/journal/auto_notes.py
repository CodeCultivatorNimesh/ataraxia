"""
Auto-notes generator — produces human-readable notes for trade journal entries.
"""
from app.journal.journal_engine import journal_engine

def generate(trade: dict, recent_trades: list, stress: int = 5, sleep: float = 7.0) -> dict:
    return journal_engine.generate_entry(trade, recent_trades, stress, sleep)
