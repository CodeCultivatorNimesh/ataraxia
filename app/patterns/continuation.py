"""
Continuation candlestick patterns.
These signal the existing trend is likely to continue.
"""

def rising_three_methods(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3, o4,h4,l4,c4, o5,h5,l5,c5):
    first_bull  = c1 > o1 and abs(c1-o1)/(h1-l1+1e-9) > 0.5
    three_small = all(abs(c-o) < abs(c1-o1)*0.5 for o,c in [(o2,c2),(o3,c3),(o4,c4)])
    stay_inside = all(l >= l1 and h <= h1 for h,l in [(h2,l2),(h3,l3),(h4,l4)])
    last_bull   = c5 > c1 and o5 > o4
    detected = first_bull and three_small and stay_inside and last_bull
    return detected, 0.82 if detected else 0.0

def falling_three_methods(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3, o4,h4,l4,c4, o5,h5,l5,c5):
    first_bear  = c1 < o1 and abs(o1-c1)/(h1-l1+1e-9) > 0.5
    three_small = all(abs(c-o) < abs(o1-c1)*0.5 for o,c in [(o2,c2),(o3,c3),(o4,c4)])
    stay_inside = all(l >= l1 and h <= h1 for h,l in [(h2,l2),(h3,l3),(h4,l4)])
    last_bear   = c5 < c1 and o5 < o4
    detected = first_bear and three_small and stay_inside and last_bear
    return detected, 0.82 if detected else 0.0

def upside_tasuki_gap(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3):
    bull1    = c1 > o1
    gap_up   = o2 > h1
    bull2    = c2 > o2
    bear3    = c3 < o3
    fills_gap = o3 >= c2 and c3 >= o2 and c3 <= c2
    detected = bull1 and gap_up and bull2 and bear3 and fills_gap
    return detected, 0.78 if detected else 0.0

def downside_tasuki_gap(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3):
    bear1    = c1 < o1
    gap_down = o2 < l1
    bear2    = c2 < o2
    bull3    = c3 > o3
    fills_gap = o3 <= c2 and c3 <= o2 and c3 >= c2
    detected = bear1 and gap_down and bear2 and bull3 and fills_gap
    return detected, 0.78 if detected else 0.0

def three_line_strike_bullish(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3, o4,h4,l4,c4):
    three_bear = all(c<o for o,c in [(o1,c1),(o2,c2),(o3,c3)])
    descending = c2 < c1 and c3 < c2
    strike     = c4 > o1 and o4 <= c3
    detected = three_bear and descending and strike
    return detected, 0.75 if detected else 0.0

def three_line_strike_bearish(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3, o4,h4,l4,c4):
    three_bull = all(c>o for o,c in [(o1,c1),(o2,c2),(o3,c3)])
    ascending  = c2 > c1 and c3 > c2
    strike     = c4 < o1 and o4 >= c3
    detected = three_bull and ascending and strike
    return detected, 0.75 if detected else 0.0

def mat_hold(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3, o4,h4,l4,c4, o5,h5,l5,c5):
    first_bull  = c1 > o1 and abs(c1-o1)/(h1-l1+1e-9) > 0.5
    gap_up      = o2 > c1
    middle_weak = all(abs(c-o) < abs(c1-o1)*0.4 for o,c in [(o2,c2),(o3,c3),(o4,c4)])
    hold_above  = all(l >= o2*0.99 for l in [l2,l3,l4])
    final_bull  = c5 > h1
    detected = first_bull and gap_up and middle_weak and hold_above and final_bull
    return detected, 0.84 if detected else 0.0

def separating_lines_bullish(o1,h1,l1,c1, o2,h2,l2,c2):
    bear1 = c1 < o1
    bull2 = c2 > o2
    same_open = abs(o1 - o2) / (max(o1, o2) + 1e-9) < 0.002
    detected = bear1 and bull2 and same_open
    return detected, 0.72 if detected else 0.0

def separating_lines_bearish(o1,h1,l1,c1, o2,h2,l2,c2):
    bull1 = c1 > o1
    bear2 = c2 < o2
    same_open = abs(o1 - o2) / (max(o1, o2) + 1e-9) < 0.002
    detected = bull1 and bear2 and same_open
    return detected, 0.72 if detected else 0.0

def in_neck(o1,h1,l1,c1, o2,h2,l2,c2):
    prior_bear = c1 < o1
    gap_down   = o2 < c1
    bull2      = c2 > o2
    closes_near_low = abs(c2 - l1) / (l1 + 1e-9) < 0.003
    detected = prior_bear and gap_down and bull2 and closes_near_low
    return detected, 0.65 if detected else 0.0

def thrusting(o1,h1,l1,c1, o2,h2,l2,c2):
    prior_bear = c1 < o1
    gap_down   = o2 < c1
    bull2      = c2 > o2
    mid        = (o1 + c1) / 2
    below_mid  = c2 < mid and c2 > l1
    detected = prior_bear and gap_down and bull2 and below_mid
    return detected, 0.60 if detected else 0.0

# 5-candle wrapper helpers
def _c5(fn, candles):
    if len(candles) < 5: return False, 0.0
    c = candles
    return fn(c[0]['o'],c[0]['h'],c[0]['l'],c[0]['c'],
              c[1]['o'],c[1]['h'],c[1]['l'],c[1]['c'],
              c[2]['o'],c[2]['h'],c[2]['l'],c[2]['c'],
              c[3]['o'],c[3]['h'],c[3]['l'],c[3]['c'],
              c[4]['o'],c[4]['h'],c[4]['l'],c[4]['c'])

def _c4(fn, candles):
    if len(candles) < 4: return False, 0.0
    c = candles
    return fn(c[0]['o'],c[0]['h'],c[0]['l'],c[0]['c'],
              c[1]['o'],c[1]['h'],c[1]['l'],c[1]['c'],
              c[2]['o'],c[2]['h'],c[2]['l'],c[2]['c'],
              c[3]['o'],c[3]['h'],c[3]['l'],c[3]['c'])

def _c3(fn, candles):
    if len(candles) < 3: return False, 0.0
    c = candles
    return fn(c[0]['o'],c[0]['h'],c[0]['l'],c[0]['c'],
              c[1]['o'],c[1]['h'],c[1]['l'],c[1]['c'],
              c[2]['o'],c[2]['h'],c[2]['l'],c[2]['c'])

def _c2(fn, candles):
    if len(candles) < 2: return False, 0.0
    c = candles
    return fn(c[0]['o'],c[0]['h'],c[0]['l'],c[0]['c'],
              c[1]['o'],c[1]['h'],c[1]['l'],c[1]['c'])

CONTINUATION_PATTERNS = {
    "Rising Three Methods":         {"candles": 5, "fn": rising_three_methods,       "type": "bullish",    "desc": "Bullish continuation — brief pause in uptrend"},
    "Falling Three Methods":        {"candles": 5, "fn": falling_three_methods,      "type": "bearish",    "desc": "Bearish continuation — brief pause in downtrend"},
    "Upside Tasuki Gap":            {"candles": 3, "fn": upside_tasuki_gap,          "type": "bullish",    "desc": "Bullish continuation — gap not fully filled"},
    "Downside Tasuki Gap":          {"candles": 3, "fn": downside_tasuki_gap,        "type": "bearish",    "desc": "Bearish continuation — gap not fully filled"},
    "Three Line Strike Bullish":    {"candles": 4, "fn": three_line_strike_bullish,  "type": "bullish",    "desc": "Bullish reversal after 3 bearish candles"},
    "Three Line Strike Bearish":    {"candles": 4, "fn": three_line_strike_bearish,  "type": "bearish",    "desc": "Bearish reversal after 3 bullish candles"},
    "Mat Hold":                     {"candles": 5, "fn": mat_hold,                   "type": "bullish",    "desc": "Strong bullish continuation after consolidation"},
    "Separating Lines Bullish":     {"candles": 2, "fn": separating_lines_bullish,   "type": "bullish",    "desc": "Bullish continuation — same open, direction reverses"},
    "Separating Lines Bearish":     {"candles": 2, "fn": separating_lines_bearish,   "type": "bearish",    "desc": "Bearish continuation — same open, direction reverses"},
    "In Neck":                      {"candles": 2, "fn": in_neck,                    "type": "bearish",    "desc": "Bearish continuation — weak recovery near prior low"},
    "Thrusting":                    {"candles": 2, "fn": thrusting,                  "type": "neutral",    "desc": "Weak recovery — closes below midpoint, trend may continue"},
}
