"""
Triple candlestick pattern detection.
Candles: 1=oldest, 2=middle, 3=newest.
"""

def morning_star(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3):
    prior_bearish = c1 < o1 and abs(c1-o1)/(h1-l1+0.0001) > 0.5
    middle_small  = abs(c2-o2) < abs(c1-o1)*0.3
    current_bull  = c3 > o3 and abs(c3-o3)/(h3-l3+0.0001) > 0.5
    recovers      = c3 > (o1+c1)/2
    detected = prior_bearish and middle_small and current_bull and recovers
    return detected, 0.85 if detected else 0.0

def evening_star(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3):
    prior_bull    = c1 > o1 and abs(c1-o1)/(h1-l1+0.0001) > 0.5
    middle_small  = abs(c2-o2) < abs(c1-o1)*0.3
    current_bear  = c3 < o3 and abs(o3-c3)/(h3-l3+0.0001) > 0.5
    recovers      = c3 < (o1+c1)/2
    detected = prior_bull and middle_small and current_bear and recovers
    return detected, 0.85 if detected else 0.0

def morning_doji_star(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3):
    prior_bearish = c1 < o1
    doji_middle   = abs(c2-o2)/(h2-l2+0.0001) <= 0.05
    current_bull  = c3 > o3 and c3 > (o1+c1)/2
    detected = prior_bearish and doji_middle and current_bull
    return detected, 0.88 if detected else 0.0

def evening_doji_star(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3):
    prior_bull    = c1 > o1
    doji_middle   = abs(c2-o2)/(h2-l2+0.0001) <= 0.05
    current_bear  = c3 < o3 and c3 < (o1+c1)/2
    detected = prior_bull and doji_middle and current_bear
    return detected, 0.88 if detected else 0.0

def three_white_soldiers(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3):
    all_bull = c1>o1 and c2>o2 and c3>o3
    ascending = c2>c1 and c3>c2
    opens_within = o2>o1 and o2<c1 and o3>o2 and o3<c2
    small_wicks  = (h1-c1)<abs(c1-o1)*0.3 and (h2-c2)<abs(c2-o2)*0.3 and (h3-c3)<abs(c3-o3)*0.3
    detected = all_bull and ascending and opens_within and small_wicks
    return detected, 0.90 if detected else 0.0

def three_black_crows(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3):
    all_bear = c1<o1 and c2<o2 and c3<o3
    descending = c2<c1 and c3<c2
    opens_within = o2<o1 and o2>c1 and o3<o2 and o3>c2
    small_wicks  = (c1-l1)<abs(o1-c1)*0.3 and (c2-l2)<abs(o2-c2)*0.3 and (c3-l3)<abs(o3-c3)*0.3
    detected = all_bear and descending and opens_within and small_wicks
    return detected, 0.90 if detected else 0.0

def three_inside_up(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3):
    prior_bearish = c1 < o1
    harami = o2 >= c1 and c2 <= o1 and c2 > o2
    confirmation = c3 > c1
    detected = prior_bearish and harami and confirmation
    return detected, 0.82 if detected else 0.0

def three_inside_down(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3):
    prior_bull = c1 > o1
    harami = o2 <= c1 and c2 >= o1 and c2 < o2
    confirmation = c3 < c1
    detected = prior_bull and harami and confirmation
    return detected, 0.82 if detected else 0.0

def three_outside_up(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3):
    engulf = c1<o1 and c2>o2 and o2<=c1 and c2>=o1
    confirmation = c3 > c2
    detected = engulf and confirmation
    return detected, 0.83 if detected else 0.0

def three_outside_down(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3):
    engulf = c1>o1 and c2<o2 and o2>=c1 and c2<=o1
    confirmation = c3 < c2
    detected = engulf and confirmation
    return detected, 0.83 if detected else 0.0

def abandoned_baby_bullish(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3):
    prior_bearish = c1 < o1
    doji = abs(c2-o2)/(h2-l2+0.0001) <= 0.05
    gap_down = h2 < l1
    gap_up   = l3 > h2
    bull_confirm = c3 > o3
    detected = prior_bearish and doji and gap_down and gap_up and bull_confirm
    return detected, 0.92 if detected else 0.0

def abandoned_baby_bearish(o1,h1,l1,c1, o2,h2,l2,c2, o3,h3,l3,c3):
    prior_bull = c1 > o1
    doji = abs(c2-o2)/(h2-l2+0.0001) <= 0.05
    gap_up   = l2 > h1
    gap_down = h3 < l2
    bear_confirm = c3 < o3
    detected = prior_bull and doji and gap_up and gap_down and bear_confirm
    return detected, 0.92 if detected else 0.0

TRIPLE_PATTERNS = {
    "Morning Star":             {"fn": morning_star,            "type": "bullish", "desc": "Strong bullish reversal — 3-candle bottom pattern"},
    "Evening Star":             {"fn": evening_star,            "type": "bearish", "desc": "Strong bearish reversal — 3-candle top pattern"},
    "Morning Doji Star":        {"fn": morning_doji_star,       "type": "bullish", "desc": "Powerful bullish reversal with doji indecision"},
    "Evening Doji Star":        {"fn": evening_doji_star,       "type": "bearish", "desc": "Powerful bearish reversal with doji indecision"},
    "Three White Soldiers":     {"fn": three_white_soldiers,    "type": "bullish", "desc": "Strong bullish trend — 3 consecutive large bullish candles"},
    "Three Black Crows":        {"fn": three_black_crows,       "type": "bearish", "desc": "Strong bearish trend — 3 consecutive large bearish candles"},
    "Three Inside Up":          {"fn": three_inside_up,         "type": "bullish", "desc": "Bullish reversal — harami confirmed by third candle"},
    "Three Inside Down":        {"fn": three_inside_down,       "type": "bearish", "desc": "Bearish reversal — harami confirmed by third candle"},
    "Three Outside Up":         {"fn": three_outside_up,        "type": "bullish", "desc": "Bullish reversal — engulfing confirmed"},
    "Three Outside Down":       {"fn": three_outside_down,      "type": "bearish", "desc": "Bearish reversal — engulfing confirmed"},
    "Abandoned Baby Bullish":   {"fn": abandoned_baby_bullish,  "type": "bullish", "desc": "Very rare, very powerful bullish reversal"},
    "Abandoned Baby Bearish":   {"fn": abandoned_baby_bearish,  "type": "bearish", "desc": "Very rare, very powerful bearish reversal"},
}
