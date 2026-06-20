"""
Emotion tracker — records and trends emotional scores over time.
"""
from datetime import datetime

class EmotionTracker:

    def score_from_inputs(self, stress: int, sleep: float, consecutive_losses: int,
                           daily_loss_pct: float, revenge_trading: bool = False) -> dict:
        score = 100
        deductions = []

        if revenge_trading:
            score -= 30
            deductions.append({"reason": "Revenge trading", "pts": 30})
        if consecutive_losses >= 3:
            pts = min(consecutive_losses * 5, 25)
            score -= pts
            deductions.append({"reason": f"{consecutive_losses} consecutive losses", "pts": pts})
        if daily_loss_pct >= 5:
            score -= 25
            deductions.append({"reason": "Daily loss limit hit", "pts": 25})
        elif daily_loss_pct >= 2:
            score -= 8
            deductions.append({"reason": "Daily loss > 2%", "pts": 8})
        if stress > 7:
            score -= 15
            deductions.append({"reason": "High stress", "pts": 15})
        if sleep < 5:
            score -= 10
            deductions.append({"reason": "Poor sleep", "pts": 10})

        score = max(0, score)
        return {
            "score":      score,
            "deductions": deductions,
            "timestamp":  datetime.utcnow().isoformat(),
            "state":      "critical" if score < 40 else "moderate" if score < 60 else "healthy",
        }

emotion_tracker = EmotionTracker()
