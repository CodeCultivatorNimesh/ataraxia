"""
Dashboard data assembler — combines all analytics into one payload
for the frontend dashboard.
"""
from app.analytics.performance import full_performance_report, asset_breakdown
from app.analytics.statistics import consecutive_streaks

def build_dashboard_payload(
    trades: list,
    behavioral_score: int,
    open_trades: list,
    top_patterns: list,
    starting_balance: float = 10000.0,
) -> dict:
    """
    Assembles the full dashboard payload used by the frontend.
    All inputs are plain dicts so this is framework-agnostic.
    """
    perf = full_performance_report(trades, starting_balance)
    asset_bk = asset_breakdown(trades)
    streaks = consecutive_streaks(trades)

    # Daily loss today
    from datetime import datetime
    today = str(datetime.utcnow().date())
    today_pnl = sum(
        t.get("pnl", 0) for t in trades
        if t.get("pnl") is not None and (
            str(t.get("closed_at", ""))[:10] == today or
            str(t.get("created_at", ""))[:10] == today
        )
    )
    today_loss_pct = abs(today_pnl) / starting_balance * 100 if today_pnl < 0 else 0

    return {
        "account": {
            "balance":          starting_balance + perf["total_pnl"],
            "starting_balance": starting_balance,
            "total_pnl":        perf["total_pnl"],
            "today_pnl":        round(today_pnl, 2),
            "today_loss_pct":   round(today_loss_pct, 2),
        },
        "performance": {
            "total_trades":     perf["total_trades"],
            "win_rate":         perf["win_rate"],
            "profit_factor":    perf["profit_factor"],
            "sharpe_ratio":     perf["sharpe_ratio"],
            "expectancy":       perf["expectancy"],
            "avg_win":          perf["avg_win"],
            "avg_loss":         perf["avg_loss"],
            "reward_risk_ratio":perf["reward_risk_ratio"],
            "max_drawdown_pct": perf["max_drawdown_pct"],
            "largest_win":      perf["largest_win"],
            "largest_loss":     perf["largest_loss"],
        },
        "streaks": streaks,
        "behavioral": {
            "score":         behavioral_score,
            "state":         "critical" if behavioral_score < 40 else
                             "moderate" if behavioral_score < 60 else "healthy",
            "trading_allowed": behavioral_score >= 40,
        },
        "open_trades":      open_trades,
        "top_patterns":     top_patterns,
        "asset_breakdown":  asset_bk,
        "equity_curve":     perf["equity_curve"],
    }
