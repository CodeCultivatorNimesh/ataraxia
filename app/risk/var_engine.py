import statistics
from typing import List

def historical_var(returns: List[float], confidence: float = 0.95) -> dict:
    if not returns:
        return {"var_95": 0.0, "var_99": 0.0, "cvar_95": 0.0}
    s = sorted(returns)
    idx_95 = max(0, int(len(s) * (1 - confidence)))
    idx_99 = max(0, int(len(s) * 0.01))
    var_95 = abs(s[idx_95])
    var_99 = abs(s[idx_99])
    tail = [r for r in s if r <= s[idx_95]]
    cvar_95 = abs(statistics.mean(tail)) if tail else var_95
    return {
        "var_95":    round(var_95, 4),
        "var_99":    round(var_99, 4),
        "cvar_95":   round(cvar_95, 4),
        "method":    "historical",
        "samples":   len(returns),
    }

def parametric_var(mean: float, std: float, confidence: float = 0.95) -> dict:
    # z-score for 95% = 1.645, 99% = 2.326
    z95, z99 = 1.645, 2.326
    return {
        "var_95":  round(abs(mean - z95 * std), 4),
        "var_99":  round(abs(mean - z99 * std), 4),
        "method":  "parametric",
    }
