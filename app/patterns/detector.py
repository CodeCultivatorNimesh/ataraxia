"""
Master pattern detector.
Receives a list of candles (dicts with o,h,l,c,v,t keys) and runs all patterns.
"""
from app.patterns.single_candle import SINGLE_PATTERNS
from app.patterns.double_candle import DOUBLE_PATTERNS
from app.patterns.triple_candle import TRIPLE_PATTERNS
from app.patterns.continuation import CONTINUATION_PATTERNS, _c2, _c3, _c4, _c5
from app.config import settings
from datetime import datetime

def _candle(o, h, l, c): return {"o": o, "h": h, "l": l, "c": c}

class PatternDetector:

    def __init__(self, min_confidence: float = None):
        self.min_confidence = min_confidence or settings.pattern_min_confidence

    def detect_all(self, candles: list) -> list:
        """
        candles: list of dicts [{o, h, l, c, v, t}, ...]  oldest → newest
        Returns list of detected pattern dicts.
        """
        if not candles:
            return []

        results = []
        last = candles[-1]
        o, h, l, c = last["o"], last["h"], last["l"], last["c"]

        # ── Single candle (last candle only) ──
        for name, info in SINGLE_PATTERNS.items():
            detected, conf = info["fn"](o, h, l, c)
            if detected and conf >= self.min_confidence:
                results.append(self._build(name, info, conf, last, "single"))

        # ── Double candle (last 2) ──
        if len(candles) >= 2:
            p = candles[-2]
            for name, info in DOUBLE_PATTERNS.items():
                detected, conf = info["fn"](
                    p["o"],p["h"],p["l"],p["c"],
                    o, h, l, c
                )
                if detected and conf >= self.min_confidence:
                    results.append(self._build(name, info, conf, last, "double"))

        # ── Triple candle (last 3) ──
        if len(candles) >= 3:
            p1, p2 = candles[-3], candles[-2]
            for name, info in TRIPLE_PATTERNS.items():
                detected, conf = info["fn"](
                    p1["o"],p1["h"],p1["l"],p1["c"],
                    p2["o"],p2["h"],p2["l"],p2["c"],
                    o, h, l, c
                )
                if detected and conf >= self.min_confidence:
                    results.append(self._build(name, info, conf, last, "triple"))

        # ── Continuation (2–5 candles) ──
        for name, info in CONTINUATION_PATTERNS.items():
            n = info["candles"]
            if len(candles) < n:
                continue
            subset = [_candle(x["o"],x["h"],x["l"],x["c"]) for x in candles[-n:]]
            if n == 2:
                detected, conf = _c2(info["fn"], subset)
            elif n == 3:
                detected, conf = _c3(info["fn"], subset)
            elif n == 4:
                detected, conf = _c4(info["fn"], subset)
            else:
                detected, conf = _c5(info["fn"], subset)
            if detected and conf >= self.min_confidence:
                results.append(self._build(name, info, conf, last, "continuation"))

        return results

    def _build(self, name, info, confidence, candle, category):
        return {
            "pattern_name":  name,
            "pattern_type":  info["type"],
            "category":      category,
            "confidence":    round(confidence, 2),
            "description":   info["desc"],
            "candle_time":   candle.get("t", datetime.utcnow().isoformat()),
            "open":          candle["o"],
            "high":          candle["h"],
            "low":           candle["l"],
            "close":         candle["c"],
        }

    def summary(self, results: list) -> dict:
        bullish = [r for r in results if r["pattern_type"] == "bullish"]
        bearish = [r for r in results if r["pattern_type"] == "bearish"]
        return {
            "total_detected":  len(results),
            "bullish_count":   len(bullish),
            "bearish_count":   len(bearish),
            "neutral_count":   len(results) - len(bullish) - len(bearish),
            "bias":            "bullish" if len(bullish) > len(bearish) else "bearish" if len(bearish) > len(bullish) else "neutral",
            "strongest":       max(results, key=lambda x: x["confidence"]) if results else None,
            "patterns":        results,
        }

detector = PatternDetector()
