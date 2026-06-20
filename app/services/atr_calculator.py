def calculate_atr(candles: list, period: int = 14) -> float:
    """Calculate ATR from list of {o,h,l,c} candle dicts."""
    if len(candles) < period + 1:
        return 0.0
    trs = []
    for i in range(1, len(candles)):
        h, l, pc = candles[i]["h"], candles[i]["l"], candles[i-1]["c"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    return round(sum(trs[-period:]) / period, 4)

def atr_stop_loss(entry: float, atr: float, direction: str, volatility: str = "medium") -> dict:
    multipliers = {"low": 1.5, "medium": 2.0, "high": 2.5, "extreme": 3.0}
    mult = multipliers.get(volatility, 2.0)
    dist = atr * mult
    stop = entry - dist if direction == "long" else entry + dist
    return {
        "atr_value":    round(atr, 4),
        "multiplier":   mult,
        "stop_distance":round(dist, 4),
        "stop_price":   round(stop, 4),
        "volatility":   volatility,
    }
