"""
Unit tests for analytics modules.
"""
import pytest
from app.analytics.statistics import (
    win_rate, profit_factor, sharpe_ratio,
    max_drawdown, avg_win_loss, consecutive_streaks, expectancy
)
from app.analytics.performance import full_performance_report, asset_breakdown
from app.analytics.dashboard import build_dashboard_payload


def test_win_rate(sample_trades):
    wr = win_rate(sample_trades)
    assert wr == 60.0   # 3 wins out of 5


def test_profit_factor(sample_trades):
    pf = profit_factor(sample_trades)
    assert pf > 0
    # gross profit = 250+400+180=830, gross loss = 150+200=350
    assert round(pf, 2) == round(830 / 350, 2)


def test_sharpe_ratio():
    returns = [1.0, 2.0, -1.0, 0.5, 1.5, -0.5, 2.0, 0.8, -0.3, 1.2]
    sr = sharpe_ratio(returns)
    assert isinstance(sr, float)


def test_max_drawdown():
    curve = [10000, 10500, 10200, 9800, 10300, 11000]
    dd = max_drawdown(curve)
    assert dd["max_drawdown"] == pytest.approx(700, abs=1)
    assert dd["max_drawdown_pct"] > 0


def test_avg_win_loss(sample_trades):
    result = avg_win_loss(sample_trades)
    assert result["avg_win"] > 0
    assert result["avg_loss"] < 0
    assert result["win_count"] == 3
    assert result["loss_count"] == 2


def test_consecutive_streaks(sample_trades):
    s = consecutive_streaks(sample_trades)
    assert "max_win_streak" in s
    assert "max_loss_streak" in s
    assert s["max_win_streak"] >= 1


def test_expectancy(sample_trades):
    e = expectancy(sample_trades)
    # (250 - 150 + 400 - 200 + 180) / 5 = 96
    assert e == pytest.approx(96.0, abs=0.1)


def test_full_performance_report(sample_trades):
    report = full_performance_report(sample_trades)
    assert "total_trades" in report
    assert "win_rate" in report
    assert "equity_curve" in report
    assert report["total_trades"] == 5
    assert report["win_rate"] == 60.0


def test_asset_breakdown(sample_trades):
    breakdown = asset_breakdown(sample_trades)
    assert "STOCK" in breakdown
    assert "CRYPTO_SPOT" in breakdown
    assert breakdown["STOCK"]["trades"] == 3


def test_dashboard_payload(sample_trades):
    payload = build_dashboard_payload(
        trades=sample_trades,
        behavioral_score=72,
        open_trades=[],
        top_patterns=[{"pattern": "Hammer", "count": 3}],
    )
    assert "account" in payload
    assert "performance" in payload
    assert "behavioral" in payload
    assert payload["behavioral"]["score"] == 72
    assert payload["behavioral"]["trading_allowed"] == True
