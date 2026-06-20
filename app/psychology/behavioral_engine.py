from datetime import datetime, timedelta
from app.config import settings

class BehavioralEngine:

    def analyze(self, trades: list, stress: int = 5, sleep: float = 7.0, daily_loss_pct: float = 0.0) -> dict:
        insights = {
            "revenge_trading":    False,
            "overtrading":        False,
            "loss_aversion":      False,
            "fomo_detected":      False,
            "overconfidence":     False,
            "recency_bias":       False,
            "emotional_score":    100,
            "warnings":           [],
            "deductions":         [],
        }

        if not trades:
            return insights

        # Overtrading: more than 10 trades today
        today = datetime.utcnow().date()
        today_trades = [t for t in trades if self._trade_date(t) == today]
        if len(today_trades) > 10:
            insights["overtrading"] = True
            insights["warnings"].append("Overtrading detected — more than 10 trades today")
            insights["deductions"].append({"label": "Overtrading", "pts": 20})

        # Consecutive losses → revenge trading
        consecutive_losses = 0
        for t in reversed(trades):
            if t.get("pnl", 0) < 0:
                consecutive_losses += 1
            else:
                break

        if consecutive_losses >= 3:
            insights["revenge_trading"] = True
            insights["warnings"].append(f"Revenge trading risk — {consecutive_losses} consecutive losses")
            insights["deductions"].append({"label": "Revenge trading", "pts": 30})

        # Loss aversion: holding losers longer than winners
        losing_hold = [t.get("hold_time", 0) for t in trades if t.get("pnl", 0) < 0]
        winning_hold = [t.get("hold_time", 0) for t in trades if t.get("pnl", 0) > 0]
        if losing_hold and winning_hold:
            avg_lose = sum(losing_hold) / len(losing_hold)
            avg_win  = sum(winning_hold) / len(winning_hold)
            if avg_lose > avg_win * 1.5:
                insights["loss_aversion"] = True
                ratio = round(avg_lose / max(avg_win, 1), 1)
                insights["warnings"].append(f"Loss aversion — holding losers {ratio}× longer than winners")
                insights["deductions"].append({"label": "Loss aversion", "pts": 15})

        # Overconfidence: increasing size after wins
        recent_wins = [t for t in trades[-5:] if t.get("pnl", 0) > 0]
        if len(recent_wins) >= 4:
            sizes = [t.get("quantity", 0) for t in trades[-5:]]
            if sizes and sizes[-1] > sizes[0] * 1.5:
                insights["overconfidence"] = True
                insights["warnings"].append("Overconfidence — position sizes increasing after win streak")
                insights["deductions"].append({"label": "Overconfidence", "pts": 15})

        # Daily loss check
        if daily_loss_pct >= settings.max_daily_loss_pct:
            insights["deductions"].append({"label": f"Daily loss >{settings.max_daily_loss_pct}%", "pts": 25})
        elif daily_loss_pct >= 2:
            insights["deductions"].append({"label": "Daily loss >2%", "pts": 8})

        # Stress and sleep
        if stress > 7:
            insights["deductions"].append({"label": "High stress level", "pts": 15})
            insights["warnings"].append("High stress detected — consider waiting before trading")
        if sleep < 5:
            insights["deductions"].append({"label": "Sleep deprivation", "pts": 10})
            insights["warnings"].append("Poor sleep — cognitive performance may be impaired")

        # Calculate score
        score = 100
        for d in insights["deductions"]:
            score -= d["pts"]
        insights["emotional_score"] = max(0, score)

        return insights

    def _trade_date(self, trade):
        ts = trade.get("created_at") or trade.get("opened_at")
        if isinstance(ts, datetime):
            return ts.date()
        return datetime.utcnow().date()

behavioral_engine = BehavioralEngine()
