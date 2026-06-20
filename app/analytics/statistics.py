"""
Statistical helpers for trade analytics.
"""
import statistics
from typing import List, Optional

def win_rate(trades: list) -> float:
    closed = [t for t in trades if t.get("pnl") is not None]
    if not closed: return 0.0
    wins = [t for t in closed if t["pnl"] > 0]
    return round(len(wins) / len(closed) * 100, 2)

def profit_factor(trades: list) -> float:
    gross_profit = sum(t["pnl"] for t in trades if t.get("pnl", 0) > 0)
    gross_loss   = abs(sum(t["pnl"] for t in trades if t.get("pnl", 0) < 0))
    return round(gross_profit / gross_loss, 2) if gross_loss > 0 else 0.0

def sharpe_ratio(returns: List[float], periods_per_year: int = 252) -> float:
    if len(returns) < 2: return 0.0
    mean_r = statistics.mean(returns)
    std_r  = statistics.stdev(returns)
    if std_r == 0: return 0.0
    return round((mean_r / std_r) * (periods_per_year ** 0.5), 2)

def max_drawdown(equity_curve: List[float]) -> dict:
    if not equity_curve: return {"max_drawdown": 0.0, "max_drawdown_pct": 0.0}
    peak = equity_curve[0]
    max_dd = 0.0
    for val in equity_curve:
        if val > peak: peak = val
        dd = peak - val
        if dd > max_dd: max_dd = dd
    max_dd_pct = (max_dd / peak * 100) if peak > 0 else 0.0
    return {
        "max_drawdown":     round(max_dd, 2),
        "max_drawdown_pct": round(max_dd_pct, 2),
    }

def avg_win_loss(trades: list) -> dict:
    wins   = [t["pnl"] for t in trades if t.get("pnl", 0) > 0]
    losses = [t["pnl"] for t in trades if t.get("pnl", 0) < 0]
    return {
        "avg_win":          round(statistics.mean(wins),   2) if wins   else 0.0,
        "avg_loss":         round(statistics.mean(losses), 2) if losses else 0.0,
        "largest_win":      round(max(wins),    2) if wins   else 0.0,
        "largest_loss":     round(min(losses),  2) if losses else 0.0,
        "win_count":        len(wins),
        "loss_count":       len(losses),
        "reward_risk_ratio": round(abs(statistics.mean(wins) / statistics.mean(losses)), 2)
                             if wins and losses and statistics.mean(losses) != 0 else 0.0,
    }

def consecutive_streaks(trades: list) -> dict:
    if not trades: return {"max_win_streak": 0, "max_loss_streak": 0, "current_streak": 0}
    max_wins = max_losses = cur = 0
    streak_type = None
    for t in trades:
        is_win = t.get("pnl", 0) > 0
        if streak_type is None or streak_type == is_win:
            cur += 1
            streak_type = is_win
        else:
            cur = 1
            streak_type = is_win
        if is_win:  max_wins   = max(max_wins,   cur)
        else:       max_losses = max(max_losses, cur)
    current = cur if streak_type is False else -cur
    return {
        "max_win_streak":  max_wins,
        "max_loss_streak": max_losses,
        "current_streak":  current,
    }

def expectancy(trades: list) -> float:
    """Average expected PnL per trade."""
    closed = [t for t in trades if t.get("pnl") is not None]
    if not closed: return 0.0
    return round(statistics.mean([t["pnl"] for t in closed]), 2)
