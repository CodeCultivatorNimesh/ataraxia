"""
Unit tests for position sizing — all asset classes.
"""
import pytest
from app.risk.position_size import PositionSizeCalculator
from app.services.atr_calculator import calculate_atr, atr_stop_loss


# ── Spot Position Sizing ───────────────────────────────────────
class TestSpotPositionSizing:

    def test_basic_stock_long(self):
        r = PositionSizeCalculator.calculate_spot(
            account_balance=10000, risk_pct=1.0,
            entry_price=150, atr_value=3.5,
            direction="long", volatility="medium", asset_type="stock"
        )
        assert r.risk_amount == pytest.approx(100.0)
        assert r.atr_stop_distance == pytest.approx(7.0)   # 3.5 * 2.0
        assert r.stop_loss_price == pytest.approx(143.0)
        assert r.position_size == pytest.approx(14.28, abs=0.1)
        assert r.unit == "shares"
        assert r.direction == "long"

    def test_basic_stock_short(self):
        r = PositionSizeCalculator.calculate_spot(
            account_balance=10000, risk_pct=1.0,
            entry_price=150, atr_value=3.5,
            direction="short", volatility="medium"
        )
        assert r.stop_loss_price == pytest.approx(157.0)  # entry + stop_dist

    def test_crypto_spot_unit_is_coins(self):
        r = PositionSizeCalculator.calculate_spot(
            account_balance=10000, risk_pct=1.0,
            entry_price=42000, atr_value=1200,
            direction="long", volatility="medium", asset_type="crypto"
        )
        assert r.unit == "coins"

    def test_low_volatility_multiplier_15(self):
        r = PositionSizeCalculator.calculate_spot(
            10000, 1.0, 150, 4.0, volatility="low"
        )
        assert r.atr_stop_distance == pytest.approx(6.0)   # 4.0 * 1.5

    def test_high_volatility_multiplier_25(self):
        r = PositionSizeCalculator.calculate_spot(
            10000, 1.0, 150, 4.0, volatility="high"
        )
        assert r.atr_stop_distance == pytest.approx(10.0)  # 4.0 * 2.5

    def test_extreme_volatility_multiplier_3(self):
        r = PositionSizeCalculator.calculate_spot(
            10000, 1.0, 150, 4.0, volatility="extreme"
        )
        assert r.atr_stop_distance == pytest.approx(12.0)  # 4.0 * 3.0

    def test_extreme_reduces_risk_by_40pct(self):
        r_med = PositionSizeCalculator.calculate_spot(10000, 1.0, 150, 3.5, volatility="medium")
        r_ext = PositionSizeCalculator.calculate_spot(10000, 1.0, 150, 3.5, volatility="extreme")
        assert r_ext.risk_amount == pytest.approx(r_med.risk_amount * 0.6, rel=0.01)

    def test_zero_atr_raises_value_error(self):
        with pytest.raises(ValueError, match="zero"):
            PositionSizeCalculator.calculate_spot(10000, 1.0, 150, 0)

    def test_higher_risk_pct_larger_position(self):
        r1 = PositionSizeCalculator.calculate_spot(10000, 1.0, 150, 3.5)
        r2 = PositionSizeCalculator.calculate_spot(10000, 2.0, 150, 3.5)
        assert r2.position_size > r1.position_size

    def test_higher_balance_larger_position(self):
        r1 = PositionSizeCalculator.calculate_spot(10000, 1.0, 150, 3.5)
        r2 = PositionSizeCalculator.calculate_spot(50000, 1.0, 150, 3.5)
        assert r2.position_size == pytest.approx(r1.position_size * 5, rel=0.01)


# ── Crypto Futures Cross Mode ──────────────────────────────────
class TestCryptoFuturesCross:

    def test_medium_volatility_6x(self):
        r = PositionSizeCalculator.calculate_crypto_futures_cross(
            account_balance=10000, entry_price=42000,
            atr_value=1200, volatility="medium"
        )
        assert r["leverage"] == 6
        assert r["notional_power"] == 60000
        assert r["position_opened"] == 3600
        assert r["notional_remaining"] == 56400

    def test_low_volatility_8x(self):
        r = PositionSizeCalculator.calculate_crypto_futures_cross(
            10000, 42000, 1200, volatility="low"
        )
        assert r["leverage"] == 8
        assert r["notional_power"] == 80000

    def test_high_volatility_5x(self):
        r = PositionSizeCalculator.calculate_crypto_futures_cross(
            10000, 42000, 1200, volatility="high"
        )
        assert r["leverage"] == 5

    def test_stop_before_liquidation_long(self):
        r = PositionSizeCalculator.calculate_crypto_futures_cross(
            10000, 42000, 1200, volatility="medium", direction="long"
        )
        assert r["stop_before_liquidation"] is True

    def test_liquidation_price_below_entry_for_long(self):
        r = PositionSizeCalculator.calculate_crypto_futures_cross(
            10000, 42000, 1200, direction="long"
        )
        assert r["liquidation_price"] < 42000

    def test_liquidation_price_above_entry_for_short(self):
        r = PositionSizeCalculator.calculate_crypto_futures_cross(
            10000, 42000, 1200, direction="short"
        )
        assert r["liquidation_price"] > 42000

    def test_averaging_entries_positive(self):
        r = PositionSizeCalculator.calculate_crypto_futures_cross(
            10000, 42000, 1200, volatility="medium"
        )
        assert r["averaging_entries_possible"] >= 10

    def test_higher_maintenance_margin_shifts_liquidation(self):
        r1 = PositionSizeCalculator.calculate_crypto_futures_cross(
            10000, 42000, 1200, maintenance_margin_pct=0.5
        )
        r2 = PositionSizeCalculator.calculate_crypto_futures_cross(
            10000, 42000, 1200, maintenance_margin_pct=1.0
        )
        # Higher mm → liquidation price is farther from entry
        assert r2["liquidation_distance_pct"] != r1["liquidation_distance_pct"]


# ── Crypto Futures Isolated Mode ──────────────────────────────
class TestCryptoFuturesIsolated:

    @pytest.mark.parametrize("vol,expected_lev", [
        ("low", 5), ("medium", 4), ("high", 3), ("extreme", 3)
    ])
    def test_leverage_by_volatility(self, vol, expected_lev):
        r = PositionSizeCalculator.calculate_crypto_futures_isolated(
            10000, 42000, 1200, volatility=vol
        )
        assert r["leverage"] == expected_lev

    def test_blocks_at_3_positions(self):
        r = PositionSizeCalculator.calculate_crypto_futures_isolated(
            10000, 42000, 1200, open_positions=3
        )
        assert r["new_trade_allowed"] is False
        assert r["slots_remaining"] == 0

    def test_allows_at_0_positions(self):
        r = PositionSizeCalculator.calculate_crypto_futures_isolated(
            10000, 42000, 1200, open_positions=0
        )
        assert r["new_trade_allowed"] is True
        assert r["slots_remaining"] == 3

    def test_allows_at_2_positions(self):
        r = PositionSizeCalculator.calculate_crypto_futures_isolated(
            10000, 42000, 1200, open_positions=2
        )
        assert r["new_trade_allowed"] is True
        assert r["slots_remaining"] == 1

    def test_margin_less_than_notional(self):
        r = PositionSizeCalculator.calculate_crypto_futures_isolated(
            10000, 42000, 1200
        )
        assert r["margin_used"] < r["notional_value"]

    def test_stop_before_liquidation(self):
        r = PositionSizeCalculator.calculate_crypto_futures_isolated(
            10000, 42000, 1200, direction="long"
        )
        assert r["stop_before_liquidation"] is True


# ── ATR Calculator ────────────────────────────────────────────
class TestATRCalculator:

    def test_basic_atr_calculation(self):
        candles = [
            {"o":100,"h":105,"l":98, "c":103},
            {"o":103,"h":108,"l":101,"c":106},
            {"o":106,"h":110,"l":104,"c":108},
            {"o":108,"h":112,"l":106,"c":109},
            {"o":109,"h":113,"l":107,"c":111},
        ]
        atr = calculate_atr(candles, period=3)
        assert atr > 0

    def test_insufficient_candles_returns_zero(self):
        candles = [{"o":100,"h":105,"l":98,"c":103}]
        atr = calculate_atr(candles, period=14)
        assert atr == 0.0

    def test_atr_stop_loss_long(self):
        r = atr_stop_loss(entry=150, atr=5.0, direction="long", volatility="medium")
        assert r["stop_price"] == pytest.approx(140.0)   # 150 - (5 * 2.0)
        assert r["atr_multiplier"] == 2.0

    def test_atr_stop_loss_short(self):
        r = atr_stop_loss(entry=150, atr=5.0, direction="short", volatility="medium")
        assert r["stop_price"] == pytest.approx(160.0)   # 150 + (5 * 2.0)

    def test_atr_stop_distance_increases_with_volatility(self):
        r_low = atr_stop_loss(entry=150, atr=5.0, direction="long", volatility="low")
        r_ext = atr_stop_loss(entry=150, atr=5.0, direction="long", volatility="extreme")
        assert r_ext["stop_distance"] > r_low["stop_distance"]
