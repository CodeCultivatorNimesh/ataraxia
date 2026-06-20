"""
Unit tests for behavioral analytics engine.
"""
import pytest
from app.psychology.behavioral_engine import BehavioralEngine
from app.psychology.bias_detector import BiasDetector
from app.psychology.decision_engine import DecisionEngine
from app.psychology.emotion_tracker import EmotionTracker


@pytest.fixture
def engine():
    return BehavioralEngine()


@pytest.fixture
def detector():
    return BiasDetector()


@pytest.fixture
def decision():
    return DecisionEngine()


@pytest.fixture
def tracker():
    return EmotionTracker()


# ── Behavioral Engine ──────────────────────────────────────────
class TestBehavioralEngine:

    def test_clean_state_scores_100(self, engine):
        r = engine.analyze([], stress=3, sleep=8.0, daily_loss_pct=0)
        assert r["emotional_score"] == 100
        assert r["warnings"] == []

    def test_three_consecutive_losses_flags_revenge(self, engine):
        trades = [{"pnl": -100}, {"pnl": -200}, {"pnl": -150}]
        r = engine.analyze(trades)
        assert r["revenge_trading"] is True
        assert any("revenge" in w.lower() for w in r["warnings"])

    def test_two_losses_does_not_flag_revenge(self, engine):
        trades = [{"pnl": -100}, {"pnl": -200}]
        r = engine.analyze(trades)
        assert r["revenge_trading"] is False

    def test_high_stress_reduces_score(self, engine):
        r = engine.analyze([], stress=9, sleep=7)
        assert r["emotional_score"] < 100
        assert any("stress" in w.lower() for w in r["warnings"])

    def test_poor_sleep_reduces_score(self, engine):
        r = engine.analyze([], stress=3, sleep=3.5)
        assert r["emotional_score"] < 100
        assert any("sleep" in w.lower() for w in r["warnings"])

    def test_score_never_below_zero(self, engine):
        trades = [{"pnl": -100}] * 5
        r = engine.analyze(trades, stress=10, sleep=2, daily_loss_pct=6)
        assert r["emotional_score"] >= 0

    def test_daily_loss_reduces_score(self, engine):
        r_clean = engine.analyze([], daily_loss_pct=0)
        r_loss  = engine.analyze([], daily_loss_pct=2.5)
        assert r_loss["emotional_score"] < r_clean["emotional_score"]

    def test_deductions_list_present(self, engine):
        r = engine.analyze([], stress=9, sleep=3)
        assert isinstance(r["deductions"], list)
        assert len(r["deductions"]) > 0


# ── Bias Detector ──────────────────────────────────────────────
class TestBiasDetector:

    def test_loss_aversion_detected(self, detector):
        trades = [
            {"pnl": -100, "hold_time": 7200},
            {"pnl": -200, "hold_time": 9000},
            {"pnl":  100, "hold_time": 600},
            {"pnl":  150, "hold_time": 500},
        ]
        biases = detector.detect(trades)
        names = [b["bias"] for b in biases]
        assert "loss_aversion" in names

    def test_no_bias_clean_trading(self, detector):
        trades = [
            {"pnl": 100, "hold_time": 1800, "quantity": 10},
            {"pnl": 150, "hold_time": 1200, "quantity": 10},
            {"pnl": -80, "hold_time": 900,  "quantity": 10},
        ]
        biases = detector.detect(trades)
        # No strong biases expected
        high = [b for b in biases if b.get("severity") == "high"]
        assert len(high) == 0

    def test_revenge_trading_detected(self, detector):
        trades = [{"pnl": -100, "hold_time": 600}] * 4
        biases = detector.detect(trades)
        names = [b["bias"] for b in biases]
        assert "revenge_trading" in names

    def test_empty_trades_returns_empty(self, detector):
        assert detector.detect([]) == []

    def test_bias_has_required_fields(self, detector):
        trades = [{"pnl": -100, "hold_time": 7200}] * 4
        biases = detector.detect(trades)
        for b in biases:
            assert "bias" in b
            assert "severity" in b
            assert "detail" in b


# ── Decision Engine ────────────────────────────────────────────
class TestDecisionEngine:

    def test_allows_healthy_state(self, decision):
        r = decision.evaluate(
            behavioral_score=80, daily_loss_pct=1.0,
            consecutive_losses=1, stress_level=4, sleep_hours=7.5
        )
        assert r["allowed"] is True
        assert r["reasons"] == []

    def test_blocks_low_behavioral_score(self, decision):
        r = decision.evaluate(behavioral_score=35, daily_loss_pct=0)
        assert r["allowed"] is False
        assert len(r["reasons"]) > 0

    def test_blocks_daily_loss_limit(self, decision):
        r = decision.evaluate(behavioral_score=80, daily_loss_pct=5.5)
        assert r["allowed"] is False

    def test_blocks_consecutive_losses(self, decision):
        r = decision.evaluate(behavioral_score=80, daily_loss_pct=1, consecutive_losses=4)
        assert r["allowed"] is False

    def test_blocks_extreme_stress(self, decision):
        r = decision.evaluate(behavioral_score=80, daily_loss_pct=1, stress_level=9)
        assert r["allowed"] is False

    def test_blocks_sleep_deprivation(self, decision):
        r = decision.evaluate(behavioral_score=80, daily_loss_pct=1, sleep_hours=3.5)
        assert r["allowed"] is False

    def test_result_has_suggestion(self, decision):
        r = decision.evaluate(behavioral_score=35, daily_loss_pct=0)
        assert "suggestion" in r
        assert len(r["suggestion"]) > 0

    def test_result_has_message(self, decision):
        r = decision.evaluate(behavioral_score=80, daily_loss_pct=1)
        assert "message" in r
        assert len(r["message"]) > 0


# ── Emotion Tracker ────────────────────────────────────────────
class TestEmotionTracker:

    def test_perfect_conditions_score_100(self, tracker):
        r = tracker.score_from_inputs(stress=1, sleep=9, consecutive_losses=0,
                                       daily_loss_pct=0, revenge_trading=False)
        assert r["score"] == 100
        assert r["state"] == "healthy"

    def test_revenge_reduces_score_30(self, tracker):
        r = tracker.score_from_inputs(stress=3, sleep=8, consecutive_losses=0,
                                       daily_loss_pct=0, revenge_trading=True)
        assert r["score"] == 70

    def test_state_critical_below_40(self, tracker):
        r = tracker.score_from_inputs(stress=10, sleep=2, consecutive_losses=5,
                                       daily_loss_pct=6, revenge_trading=True)
        assert r["score"] == 0
        assert r["state"] == "critical"

    def test_deductions_listed(self, tracker):
        r = tracker.score_from_inputs(stress=9, sleep=4, consecutive_losses=0,
                                       daily_loss_pct=0, revenge_trading=False)
        assert len(r["deductions"]) >= 2
        labels = [d["reason"] for d in r["deductions"]]
        assert any("stress" in l.lower() for l in labels)
        assert any("sleep" in l.lower() for l in labels)
