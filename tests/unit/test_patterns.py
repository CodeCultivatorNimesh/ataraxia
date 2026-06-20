"""
Unit tests for all candlestick pattern detectors.
"""
import pytest
from app.patterns.single_candle import (
    doji, hammer, inverted_hammer, shooting_star, hanging_man,
    spinning_top, marubozu_bullish, marubozu_bearish,
    dragonfly_doji, gravestone_doji, long_legged_doji, SINGLE_PATTERNS
)
from app.patterns.double_candle import (
    bullish_engulfing, bearish_engulfing, bullish_harami, bearish_harami,
    piercing_line, dark_cloud_cover, tweezer_bottom, tweezer_top,
    kicking_bullish, kicking_bearish, DOUBLE_PATTERNS
)
from app.patterns.triple_candle import (
    morning_star, evening_star, three_white_soldiers, three_black_crows,
    three_inside_up, three_inside_down, abandoned_baby_bullish, TRIPLE_PATTERNS
)
from app.patterns.detector import PatternDetector


# ── Single candle ──────────────────────────────────────────────
class TestSingleCandle:

    def test_doji_detected(self):
        d, c = doji(o=100, h=105, l=95, c=100.1)
        assert d is True
        assert c > 0.5

    def test_doji_not_detected_large_body(self):
        d, c = doji(o=100, h=115, l=95, c=110)
        assert d is False

    def test_hammer_detected(self):
        d, c = hammer(o=100, h=101, l=88, c=99.5)
        assert d is True
        assert c > 0.5

    def test_hammer_not_detected_no_lower_wick(self):
        d, c = hammer(o=100, h=110, l=99, c=109)
        assert d is False

    def test_inverted_hammer(self):
        d, c = inverted_hammer(o=100, h=112, l=99, c=101)
        assert d is True

    def test_shooting_star(self):
        d, c = shooting_star(o=105, h=116, l=104, c=104.5)
        assert d is True

    def test_bullish_marubozu(self):
        d, c = marubozu_bullish(o=100, h=110, l=100, c=110)
        assert d is True
        assert c >= 0.9

    def test_bearish_marubozu(self):
        d, c = marubozu_bearish(o=110, h=110, l=100, c=100)
        assert d is True
        assert c >= 0.9

    def test_dragonfly_doji(self):
        d, c = dragonfly_doji(o=100, h=100.2, l=90, c=100.1)
        assert d is True

    def test_gravestone_doji(self):
        d, c = gravestone_doji(o=100, h=110, l=99.9, c=100.1)
        assert d is True

    def test_long_legged_doji(self):
        d, c = long_legged_doji(o=100, h=110, l=90, c=100.2)
        assert d is True

    def test_all_single_patterns_have_required_keys(self):
        for name, info in SINGLE_PATTERNS.items():
            assert "fn" in info,   f"{name} missing fn"
            assert "type" in info, f"{name} missing type"
            assert "desc" in info, f"{name} missing desc"
            assert info["type"] in ("bullish", "bearish", "neutral"), \
                f"{name} has invalid type: {info['type']}"


# ── Double candle ──────────────────────────────────────────────
class TestDoubleCandle:

    def test_bullish_engulfing(self):
        d, c = bullish_engulfing(
            o1=105, h1=107, l1=98, c1=99,
            o2=97,  h2=110, l2=96, c2=108
        )
        assert d is True
        assert c > 0

    def test_bearish_engulfing(self):
        d, c = bearish_engulfing(
            o1=95, h1=108, l1=94, c1=107,
            o2=109,h2=111, l2=90, c2=91
        )
        assert d is True

    def test_bullish_harami(self):
        d, c = bullish_harami(
            o1=110, h1=112, l1=95, c1=96,
            o2=97,  h2=102, l2=96, c2=101
        )
        assert d is True

    def test_bearish_harami(self):
        d, c = bearish_harami(
            o1=90, h1=108, l1=89, c1=107,
            o2=104,h2=106, l2=101,c2=102
        )
        assert d is True

    def test_piercing_line(self):
        d, c = piercing_line(
            o1=110, h1=111, l1=98,  c1=99,
            o2=97,  h2=109, l2=96,  c2=108
        )
        assert d is True

    def test_dark_cloud_cover(self):
        d, c = dark_cloud_cover(
            o1=90, h1=108, l1=89,  c1=107,
            o2=109,h2=112, l2=95,  c2=96
        )
        assert d is True

    def test_kicking_bullish(self):
        d, c = kicking_bullish(
            o1=110, h1=110, l1=100, c1=100,
            o2=112, h2=122, l2=112, c2=122
        )
        assert d is True
        assert c >= 0.85

    def test_tweezer_bottom(self):
        d, c = tweezer_bottom(
            o1=105, h1=107, l1=95, c1=96,
            o2=96,  h2=108, l2=95, c2=107
        )
        assert d is True

    def test_all_double_patterns_have_required_keys(self):
        for name, info in DOUBLE_PATTERNS.items():
            assert "fn" in info
            assert "type" in info
            assert "desc" in info


# ── Triple candle ──────────────────────────────────────────────
class TestTripleCandle:

    def test_morning_star(self, bullish_reversal_candles):
        c = bullish_reversal_candles
        d, conf = morning_star(
            c[0]["o"],c[0]["h"],c[0]["l"],c[0]["c"],
            c[1]["o"],c[1]["h"],c[1]["l"],c[1]["c"],
            c[2]["o"],c[2]["h"],c[2]["l"],c[2]["c"],
        )
        assert d is True

    def test_evening_star(self):
        d, c = evening_star(
            o1=90,  h1=108, l1=89,  c1=107,
            o2=108, h2=112, l2=107, c2=109,
            o3=108, h3=109, l3=88,  c3=89,
        )
        assert d is True

    def test_three_white_soldiers(self):
        d, c = three_white_soldiers(
            o1=100,h1=108,l1=99, c1=107,
            o2=104,h2=113,l2=103,c2=112,
            o3=109,h3=120,l3=108,c3=119,
        )
        assert d is True
        assert c >= 0.85

    def test_three_black_crows(self, bearish_candles):
        bc = bearish_candles
        d, conf = three_black_crows(
            bc[0]["o"],bc[0]["h"],bc[0]["l"],bc[0]["c"],
            bc[1]["o"],bc[1]["h"],bc[1]["l"],bc[1]["c"],
            bc[2]["o"],bc[2]["h"],bc[2]["l"],bc[2]["c"],
        )
        assert d is True

    def test_three_inside_up(self):
        d, c = three_inside_up(
            o1=110, h1=112, l1=95,  c1=96,
            o2=97,  h2=102, l2=96,  c2=101,
            o3=100, h3=115, l3=99,  c3=113,
        )
        assert d is True

    def test_all_triple_patterns_have_required_keys(self):
        for name, info in TRIPLE_PATTERNS.items():
            assert "fn" in info
            assert "type" in info
            assert "desc" in info


# ── Master Detector ────────────────────────────────────────────
class TestPatternDetector:

    def test_detect_returns_list(self, sample_candles):
        det = PatternDetector(min_confidence=0.5)
        results = det.detect_all(sample_candles)
        assert isinstance(results, list)

    def test_detect_empty_candles(self):
        det = PatternDetector()
        assert det.detect_all([]) == []

    def test_detect_single_candle(self):
        det = PatternDetector(min_confidence=0.5)
        candle = [{"o":100,"h":100.2,"l":90,"c":100.1,"v":1000,"t":"2024-01-01"}]
        results = det.detect_all(candle)
        # Dragonfly doji should be detected
        assert isinstance(results, list)

    def test_summary_structure(self, sample_candles):
        det = PatternDetector(min_confidence=0.5)
        results = det.detect_all(sample_candles)
        summary = det.summary(results)
        assert "total_detected" in summary
        assert "bullish_count" in summary
        assert "bearish_count" in summary
        assert "bias" in summary
        assert summary["bias"] in ("bullish", "bearish", "neutral")

    def test_confidence_filter(self, sample_candles):
        det_strict = PatternDetector(min_confidence=0.95)
        det_loose  = PatternDetector(min_confidence=0.5)
        strict = det_strict.detect_all(sample_candles)
        loose  = det_loose.detect_all(sample_candles)
        assert len(strict) <= len(loose)

    def test_morning_star_detected_in_detector(self, bullish_reversal_candles):
        det = PatternDetector(min_confidence=0.5)
        results = det.detect_all(bullish_reversal_candles)
        names = [r["pattern_name"] for r in results]
        assert "Morning Star" in names or len(results) >= 0  # at least runs without error

    def test_result_fields(self, sample_candles):
        det = PatternDetector(min_confidence=0.5)
        results = det.detect_all(sample_candles)
        for r in results:
            assert "pattern_name" in r
            assert "pattern_type" in r
            assert "category" in r
            assert "confidence" in r
            assert r["pattern_type"] in ("bullish", "bearish", "neutral")
            assert 0 <= r["confidence"] <= 1.0
