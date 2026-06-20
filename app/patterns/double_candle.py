"""
Double candlestick pattern detection.
Functions receive two candles: (o1,h1,l1,c1) = prior, (o2,h2,l2,c2) = current.
"""

def bullish_engulfing(o1, h1, l1, c1, o2, h2, l2, c2):
    prior_bearish = c1 < o1
    current_bullish = c2 > o2
    engulfs = o2 <= c1 and c2 >= o1
    detected = prior_bearish and current_bullish and engulfs
    conf = round(abs(c2 - o2) / abs(o1 - c1), 2) if detected and abs(o1 - c1) > 0 else 0.0
    return detected, min(conf, 1.0)

def bearish_engulfing(o1, h1, l1, c1, o2, h2, l2, c2):
    prior_bullish = c1 > o1
    current_bearish = c2 < o2
    engulfs = o2 >= c1 and c2 <= o1
    detected = prior_bullish and current_bearish and engulfs
    conf = round(abs(o2 - c2) / abs(c1 - o1), 2) if detected and abs(c1 - o1) > 0 else 0.0
    return detected, min(conf, 1.0)

def bullish_harami(o1, h1, l1, c1, o2, h2, l2, c2):
    prior_bearish = c1 < o1
    current_bullish = c2 > o2
    inside = o2 >= c1 and c2 <= o1
    detected = prior_bearish and current_bullish and inside
    return detected, 0.70 if detected else 0.0

def bearish_harami(o1, h1, l1, c1, o2, h2, l2, c2):
    prior_bullish = c1 > o1
    current_bearish = c2 < o2
    inside = o2 <= c1 and c2 >= o1
    detected = prior_bullish and current_bearish and inside
    return detected, 0.70 if detected else 0.0

def piercing_line(o1, h1, l1, c1, o2, h2, l2, c2):
    prior_bearish = c1 < o1
    current_bullish = c2 > o2
    gap_down = o2 < c1
    closes_above_midpoint = c2 > (o1 + c1) / 2
    detected = prior_bearish and current_bullish and gap_down and closes_above_midpoint
    return detected, 0.80 if detected else 0.0

def dark_cloud_cover(o1, h1, l1, c1, o2, h2, l2, c2):
    prior_bullish = c1 > o1
    current_bearish = c2 < o2
    gap_up = o2 > c1
    closes_below_midpoint = c2 < (o1 + c1) / 2
    detected = prior_bullish and current_bearish and gap_up and closes_below_midpoint
    return detected, 0.80 if detected else 0.0

def tweezer_bottom(o1, h1, l1, c1, o2, h2, l2, c2):
    tolerance = (h1 - l1) * 0.02
    same_lows = abs(l1 - l2) <= tolerance
    prior_bearish = c1 < o1
    current_bullish = c2 > o2
    detected = same_lows and prior_bearish and current_bullish
    return detected, 0.75 if detected else 0.0

def tweezer_top(o1, h1, l1, c1, o2, h2, l2, c2):
    tolerance = (h1 - l1) * 0.02
    same_highs = abs(h1 - h2) <= tolerance
    prior_bullish = c1 > o1
    current_bearish = c2 < o2
    detected = same_highs and prior_bullish and current_bearish
    return detected, 0.75 if detected else 0.0

def on_neck(o1, h1, l1, c1, o2, h2, l2, c2):
    prior_bearish = c1 < o1
    gap_down = o2 < l1
    closes_near_prior_low = abs(c2 - l1) / l1 < 0.003
    detected = prior_bearish and gap_down and closes_near_prior_low
    return detected, 0.65 if detected else 0.0

def kicking_bullish(o1, h1, l1, c1, o2, h2, l2, c2):
    prior_bearish_marubouzu = c1 < o1 and (h1 - l1) > 0 and abs(c1 - o1) / (h1 - l1) >= 0.9
    current_bullish_marubozu = c2 > o2 and (h2 - l2) > 0 and abs(c2 - o2) / (h2 - l2) >= 0.9
    gap_up = o2 > o1
    detected = prior_bearish_marubouzu and current_bullish_marubozu and gap_up
    return detected, 0.90 if detected else 0.0

def kicking_bearish(o1, h1, l1, c1, o2, h2, l2, c2):
    prior_bullish_marubozu = c1 > o1 and (h1 - l1) > 0 and abs(c1 - o1) / (h1 - l1) >= 0.9
    current_bearish_marubozu = c2 < o2 and (h2 - l2) > 0 and abs(o2 - c2) / (h2 - l2) >= 0.9
    gap_down = o2 < o1
    detected = prior_bullish_marubozu and current_bearish_marubozu and gap_down
    return detected, 0.90 if detected else 0.0

DOUBLE_PATTERNS = {
    "Bullish Engulfing":  {"fn": bullish_engulfing, "type": "bullish", "desc": "Strong bullish reversal — second candle engulfs first"},
    "Bearish Engulfing":  {"fn": bearish_engulfing, "type": "bearish", "desc": "Strong bearish reversal — second candle engulfs first"},
    "Bullish Harami":     {"fn": bullish_harami,    "type": "bullish", "desc": "Bullish reversal — small candle inside prior large bearish"},
    "Bearish Harami":     {"fn": bearish_harami,    "type": "bearish", "desc": "Bearish reversal — small candle inside prior large bullish"},
    "Piercing Line":      {"fn": piercing_line,     "type": "bullish", "desc": "Bullish reversal — closes above midpoint of prior bearish"},
    "Dark Cloud Cover":   {"fn": dark_cloud_cover,  "type": "bearish", "desc": "Bearish reversal — closes below midpoint of prior bullish"},
    "Tweezer Bottom":     {"fn": tweezer_bottom,    "type": "bullish", "desc": "Bullish reversal — equal lows signal support"},
    "Tweezer Top":        {"fn": tweezer_top,       "type": "bearish", "desc": "Bearish reversal — equal highs signal resistance"},
    "On Neck":            {"fn": on_neck,           "type": "bearish", "desc": "Bearish continuation — closes near prior low"},
    "Kicking Bullish":    {"fn": kicking_bullish,   "type": "bullish", "desc": "Very strong bullish reversal — gap up marubozu"},
    "Kicking Bearish":    {"fn": kicking_bearish,   "type": "bearish", "desc": "Very strong bearish reversal — gap down marubozu"},
}
