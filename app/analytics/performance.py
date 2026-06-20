"""
Performance analytics — equity curve, daily PnL, drawdown tracking.
"""
from collections import defaultdict
from datetime import datetime
from app.analytics.statistics import (
    win_rate, profit_factor, sharpe_ratio,
    max_drawdown, avg_win_loss, consecutive_streaks, expectancy
)

def build_equity_curve(trades: list, starting_balance: float = 10000.0) -> list:
    """
    Takes a list of closed trade dicts with pnl and closed_at fields.
    Returns list of {date, daily_pnl, cumulative_pnl, balance} dicts.
    """
    daily = defaultdict(float)
    for t in trades:
        if t.get("pnl") is None:
            continue
        closed = t.get("closed_at") or t.get("created_at")
        if isinstance(closed, str):
            try:
                day = closed[:10]
            except Exception:
                day = str(datetime.utcnow().date())
        elif isinstance(closed, datetime):
            day = str(closed.date())
        else:
            day = str(datetime.utcnow().date())
        daily[day] += t["pnl"]

    curve = []
    cumulative = 0.0
    balance = starting_balance
    for day in sorted(daily.keys()):
        pnl = daily[day]
        cumulative += pnl
        balance += pnl
        curve.append({
            "date":           day,
            "daily_pnl":      round(pnl, 2),
            "cumulative_pnl": round(cumulative, 2),
            "balance":        round(balance, 2),
        })
    return curve

def full_performance_report(trades: list, starting_balance: float = 10000.0) -> dict:
    """Full performance summary for a list of trade dicts."""
    closed = [t for t in trades if t.get("pnl") is not None]
    returns_pct = [t["pnl_pct"] for t in closed if t.get("pnl_pct") is not None]
    curve = build_equity_curve(closed, starting_balance)
    balances = [c["balance"] for c in curve]
    dd = max_drawdown(balances) if balances else {"max_drawdown": 0, "max_drawdown_pct": 0}

    return {
        "total_trades":      len(closed),
        "win_rate":          win_rate(closed),
        "profit_factor":     profit_factor(closed),
        "sharpe_ratio":      sharpe_ratio(returns_pct),
        "expectancy":        expectancy(closed),
        "total_pnl":         round(sum(t["pnl"] for t in closed), 2),
        "max_drawdown":      dd["max_drawdown"],
        "max_drawdown_pct":  dd["max_drawdown_pct"],
        **avg_win_loss(closed),
        **consecutive_streaks(closed),
        "equity_curve":      curve,
    }

def asset_breakdown(trades: list) -> dict:
    """PnL breakdown by asset class."""
    breakdown = defaultdict(lambda: {"trades": 0, "pnl": 0.0, "wins": 0})
    for t in trades:
        if t.get("pnl") is None:
            continue
        ac = t.get("asset_class", "UNKNOWN")
        breakdown[ac]["trades"] += 1
        breakdown[ac]["pnl"]    += t["pnl"]
        if t["pnl"] > 0:
            breakdown[ac]["wins"] += 1
    result = {}
    for ac, data in breakdown.items():
        data["pnl"]      = round(data["pnl"], 2)
        data["win_rate"] = round(data["wins"] / data["trades"] * 100, 1) if data["trades"] > 0 else 0
        result[ac] = data
    return result
