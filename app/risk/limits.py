from app.config import settings

RISK_LIMITS = {
    "max_daily_loss_pct":          settings.max_daily_loss_pct,
    "max_risk_per_trade_pct":      settings.max_risk_per_trade_pct,
    "max_open_trades":             settings.max_open_trades,
    "max_crypto_isolated_positions": settings.max_crypto_positions_isolated,
    "min_behavioral_score":        40,
    "max_leverage_cross":          8,
    "max_leverage_isolated":       5,
    "atr_multipliers": {
        "low":     1.5,
        "medium":  2.0,
        "high":    2.5,
        "extreme": 3.0,
    },
    "risk_adjustments": {
        "low":     1.0,
        "medium":  1.0,
        "high":    0.8,
        "extreme": 0.6,
    }
}
