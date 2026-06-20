"""
Single candlestick pattern detection.
Each function receives OHLCV values and returns (detected: bool, confidence: float).
"""

def _body(o, c): return abs(c - o)
def _upper_wick(o, h, c): return h - max(o, c)
def _lower_wick(o, l, c): return min(o, c) - l
def _range(h, l): return h - l

def doji(o, h, l, c):
    rng = _range(h, l)
    if rng == 0: return False, 0.0
    body_ratio = _body(o, c) / rng
    detected = body_ratio <= 0.05
    return detected, round(1 - body_ratio, 2) if detected else 0.0

def hammer(o, h, l, c):
    rng = _range(h, l)
    if rng == 0: return False, 0.0
    body = _body(o, c)
    lower = _lower_wick(o, l, c)
    upper = _upper_wick(o, h, c)
    detected = lower >= body * 2 and upper <= body * 0.5 and body / rng >= 0.1
    conf = round(lower / rng, 2) if detected else 0.0
    return detected, conf

def inverted_hammer(o, h, l, c):
    rng = _range(h, l)
    if rng == 0: return False, 0.0
    body = _body(o, c)
    upper = _upper_wick(o, h, c)
    lower = _lower_wick(o, l, c)
    detected = upper >= body * 2 and lower <= body * 0.5 and body / rng >= 0.1
    conf = round(upper / rng, 2) if detected else 0.0
    return detected, conf

def shooting_star(o, h, l, c):
    rng = _range(h, l)
    if rng == 0: return False, 0.0
    body = _body(o, c)
    upper = _upper_wick(o, h, c)
    lower = _lower_wick(o, l, c)
    is_bearish = c < o
    detected = upper >= body * 2 and lower <= body * 0.3 and is_bearish
    conf = round(upper / rng, 2) if detected else 0.0
    return detected, conf

def hanging_man(o, h, l, c):
    detected, conf = hammer(o, h, l, c)
    return detected and c < o, conf

def spinning_top(o, h, l, c):
    rng = _range(h, l)
    if rng == 0: return False, 0.0
    body = _body(o, c)
    body_ratio = body / rng
    detected = 0.05 < body_ratio < 0.35
    return detected, round(1 - body_ratio, 2) if detected else 0.0

def marubozu_bullish(o, h, l, c):
    rng = _range(h, l)
    if rng == 0: return False, 0.0
    body = _body(o, c)
    detected = c > o and body / rng >= 0.95
    return detected, round(body / rng, 2) if detected else 0.0

def marubozu_bearish(o, h, l, c):
    rng = _range(h, l)
    if rng == 0: return False, 0.0
    body = _body(o, c)
    detected = c < o and body / rng >= 0.95
    return detected, round(body / rng, 2) if detected else 0.0

def dragonfly_doji(o, h, l, c):
    rng = _range(h, l)
    if rng == 0: return False, 0.0
    body = _body(o, c)
    lower = _lower_wick(o, l, c)
    upper = _upper_wick(o, h, c)
    detected = body / rng <= 0.05 and lower / rng >= 0.6 and upper / rng <= 0.1
    return detected, 0.85 if detected else 0.0

def gravestone_doji(o, h, l, c):
    rng = _range(h, l)
    if rng == 0: return False, 0.0
    body = _body(o, c)
    upper = _upper_wick(o, h, c)
    lower = _lower_wick(o, l, c)
    detected = body / rng <= 0.05 and upper / rng >= 0.6 and lower / rng <= 0.1
    return detected, 0.85 if detected else 0.0

def long_legged_doji(o, h, l, c):
    rng = _range(h, l)
    if rng == 0: return False, 0.0
    body = _body(o, c)
    upper = _upper_wick(o, h, c)
    lower = _lower_wick(o, l, c)
    detected = body / rng <= 0.05 and upper / rng >= 0.3 and lower / rng >= 0.3
    return detected, 0.8 if detected else 0.0

SINGLE_PATTERNS = {
    "Doji":              {"fn": doji,              "type": "neutral",  "desc": "Indecision — open and close nearly equal"},
    "Hammer":            {"fn": hammer,            "type": "bullish",  "desc": "Bullish reversal — long lower wick"},
    "Inverted Hammer":   {"fn": inverted_hammer,   "type": "bullish",  "desc": "Potential bullish reversal — long upper wick"},
    "Shooting Star":     {"fn": shooting_star,     "type": "bearish",  "desc": "Bearish reversal — long upper wick"},
    "Hanging Man":       {"fn": hanging_man,       "type": "bearish",  "desc": "Bearish reversal after uptrend"},
    "Spinning Top":      {"fn": spinning_top,      "type": "neutral",  "desc": "Indecision — small body, equal wicks"},
    "Bullish Marubozu":  {"fn": marubozu_bullish,  "type": "bullish",  "desc": "Strong bullish momentum — no wicks"},
    "Bearish Marubozu":  {"fn": marubozu_bearish,  "type": "bearish",  "desc": "Strong bearish momentum — no wicks"},
    "Dragonfly Doji":    {"fn": dragonfly_doji,    "type": "bullish",  "desc": "Bullish reversal — buyers rejected lows"},
    "Gravestone Doji":   {"fn": gravestone_doji,   "type": "bearish",  "desc": "Bearish reversal — sellers rejected highs"},
    "Long-Legged Doji":  {"fn": long_legged_doji,  "type": "neutral",  "desc": "High uncertainty — equal buying and selling"},
}
