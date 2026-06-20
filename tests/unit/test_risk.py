"""
Unit tests for risk engine and position sizing.
"""
import pytest
from app.risk.engine import RiskEngine, RiskLevel
from app.risk.position_size import PositionSizeCalculator
from app.risk.var_engine import historical_var, parametric_var
from app.risk.limits import RISK_LIMITS


@pytest.fixture
def engine():
    return RiskEngine()


# ── Risk Engine ────────────────────────────────────────────────
class TestRiskEngine:

    def test_all_checks_pass(self, engine):
        r = engine.validate_trade(10000, 2.0, 1.0, 2, 80)
        assert r["approved"] is True
        assert all(c["passed"] for c in r["checks"])
        assert r["risk_level"] == RiskLevel.LOW.value

    def test_daily_loss_blocks_at_5pct(self, engine):
        r = engine.validate_trade(10000, 5.1, 1.0, 2, 80)
        assert r["approved"] is False
        assert "daily" in r["reason"].lower()

    def test_daily_loss_allows_at_4pct(self, engine):
        r = engine.validate_trade(10000, 4.9, 1.0, 2, 80)
        assert r["approved"] is True

    def test_open_trades_blocks_at_5(self, engine):
        r = engine.validate_trade(10000, 1.0, 1.0, 5, 80)
        assert r["approved"] is False

    def test_open_trades_allows_at_4(self, engine):
        r = engine.validate_trade(10000, 1.0, 1.0, 4, 80)
        assert r["approved"] is True

    def test_risk_pct_blocks_above_2(self, engine):
        r = engine.validate_trade(10000, 1.0, 2.1, 2, 80)
        assert r["approved"] is False

    def test_risk_pct_allows_at_2(self, engine):
        r = engine.validate_trade(10000, 1.0, 2.0, 2, 80)
        assert r["approved"] is True

    def test_behavioral_score_blocks_below_40(self, engine):
        r = engine.validate_trade(10000, 1.0, 1.0, 2, 39)
        assert r["approved"] is False

    def test_behavioral_score_allows_at_40(self, engine):
        r = engine.validate_trade(10000, 1.0, 1.0, 2, 40)
        assert r["approved"] is True

    def test_result_has_four_checks(self, engine):
        r = engine.validate_trade(10000, 1.0, 1.0, 2, 80)
        assert len(r["checks"]) == 4

    def test_result_has_timestamp(self, engine):
        r = engine.validate_trade(10000, 1.0, 1.0, 2, 80)
        assert "timestamp" in r

    def test_risk_level_critical_on_daily_loss(self, engine):
        r = engine.validate_trade(10000, 5.5, 1.0, 2, 80)
        assert r["risk_level"] == RiskLevel.CRITICAL.value

    def test_var_basic(self, engine):
        returns = [-0.8,-1.2,0.5,1.1,-0.3,0.9,-1.5,0.7,-0.6,1.3,
                   -2.1,0.4,1.8,-0.9,0.6,-1.1,0.8,-0.4,1.6,-0.7]
        r = engine.calculate_var(returns)
        assert r["var_95"] > 0
        assert r["var_99"] >= r["var_95"]
        assert r["sample_size"] == 20


# ── Position Size Calculator ───────────────────────────────────
class TestPositionSizeCalculator:

    def test_spot_long_medium(self):
        r = PositionSizeCalculator.calculate_spot(
            account_balance=10000, risk_pct=1.0,
            entry_price=150, atr_value=3.5,
            direction="long", volatility="medium", asset_type="stock"
        )
        assert r.risk_amount == 100.0
        assert r.atr_stop_distance == pytest.approx(7.0)
        assert r.stop_loss_price == pytest.approx(143.0)
        assert r.position_size > 0
        assert r.unit == "shares"

    def test_spot_short_places_stop_above(self):
        r = PositionSizeCalculator.calculate_spot(
            account_balance=10000, risk_pct=1.0,
            entry_price=150, atr_value=3.5,
            direction="short", volatility="medium"
        )
        assert r.stop_loss_price == pytest.approx(157.0)

    def test_extreme_volatility_reduces_risk(self):
        r_med = PositionSizeCalculator.calculate_spot(10000,1,150,3.5,volatility="medium")
        r_ext = PositionSizeCalculator.calculate_spot(10000,1,150,3.5,volatility="extreme")
        assert r_ext.risk_amount < r_med.risk_amount

    def test_extreme_volatility_wider_stop(self):
        r_low = PositionSizeCalculator.calculate_spot(10000,1,150,3.5,volatility="low")
        r_ext = PositionSizeCalculator.calculate_spot(10000,1,150,3.5,volatility="extreme")
        assert r_ext.atr_stop_distance > r_low.atr_stop_distance

    def test_zero_atr_raises(self):
        with pytest.raises(ValueError):
            PositionSizeCalculator.calculate_spot(10000, 1, 150, 0)

    def test_crypto_spot_returns_coins_unit(self):
        r = PositionSizeCalculator.calculate_spot(
            10000, 1, 42000, 1200, asset_type="crypto"
        )
        assert r.unit == "coins"

    def test_cross_mode_leverage(self):
        r = PositionSizeCalculator.calculate_crypto_futures_cross(
            account_balance=10000, entry_price=42000,
            atr_value=1200, volatility="medium"
        )
        assert r["leverage"] == 6
        assert r["notional_power"] == 60000
        assert r["position_opened"] == 3600

    def test_cross_mode_averaging_capacity(self):
        r = PositionSizeCalculator.calculate_crypto_futures_cross(
            10000, 42000, 1200, volatility="medium"
        )
        assert r["notional_remaining"] == 56400
        assert r["averaging_entries_possible"] >= 10

    def test_cross_mode_stop_before_liquidation(self):
        r = PositionSizeCalculator.calculate_crypto_futures_cross(
            10000, 42000, 1200, volatility="medium", direction="long"
        )
        assert r["stop_before_liquidation"] is True

    def test_isolated_mode_leverage_range(self):
        for vol, expected_lev in [("low",5),("medium",4),("high",3),("extreme",3)]:
            r = PositionSizeCalculator.calculate_crypto_futures_isolated(
                10000, 42000, 1200, volatility=vol
            )
            assert r["leverage"] == expected_lev, f"Failed for volatility={vol}"

    def test_isolated_mode_blocks_at_3_positions(self):
        r = PositionSizeCalculator.calculate_crypto_futures_isolated(
            10000, 42000, 1200, open_positions=3
        )
        assert r["new_trade_allowed"] is False
        assert r["slots_remaining"] == 0

    def test_isolated_mode_allows_below_3(self):
        r = PositionSizeCalculator.calculate_crypto_futures_isolated(
            10000, 42000, 1200, open_positions=2
        )
        assert r["new_trade_allowed"] is True
        assert r["slots_remaining"] == 1


# ── VaR Engine ─────────────────────────────────────────────────
class TestVaREngine:

    def test_historical_var_basic(self):
        returns = [1.0, -0.5, 2.0, -1.5, 0.8, -0.3, 1.2, -2.0, 0.5, 0.9,
                   -0.7, 1.1, -1.8, 0.6, -0.4, 1.3, -0.9, 0.7, -1.2, 0.4]
        r = historical_var(returns)
        assert r["var_95"] > 0
        assert r["var_99"] >= r["var_95"]
        assert r["method"] == "historical"

    def test_empty_returns(self):
        r = historical_var([])
        assert r["var_95"] == 0.0

    def test_parametric_var(self):
        r = parametric_var(mean=0.5, std=1.2)
        assert r["var_95"] > 0
        assert r["var_99"] > r["var_95"]
        assert r["method"] == "parametric"

    def test_cvar_greater_or_equal_var(self):
        returns = [-2.1,-1.5,-1.2,-0.8,-0.5,0.3,0.7,1.0,1.5,2.0]
        r = historical_var(returns)
        assert r["cvar_95"] >= r["var_95"]


# ── Risk Limits Config ─────────────────────────────────────────
class TestRiskLimits:

    def test_limits_have_required_keys(self):
        required = ["max_daily_loss_pct","max_risk_per_trade_pct",
                    "max_open_trades","atr_multipliers","risk_adjustments"]
        for key in required:
            assert key in RISK_LIMITS, f"Missing key: {key}"

    def test_atr_multipliers_ascending(self):
        m = RISK_LIMITS["atr_multipliers"]
        assert m["low"] < m["medium"] < m["high"] < m["extreme"]

    def test_risk_adjustments_descend_with_volatility(self):
        r = RISK_LIMITS["risk_adjustments"]
        assert r["low"] >= r["medium"] >= r["high"] >= r["extreme"]
