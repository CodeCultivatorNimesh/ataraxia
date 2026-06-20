class DecisionEngine:

    def evaluate(
        self,
        behavioral_score: int,
        daily_loss_pct: float,
        consecutive_losses: int = 0,
        stress_level: int = 5,
        sleep_hours: float = 7.0,
    ) -> dict:
        score = behavioral_score
        reasons = []

        if score < 40:
            reasons.append(f"Behavioral score {score}/100 is critically low")
        if daily_loss_pct >= 5:
            reasons.append(f"Daily loss {daily_loss_pct:.1f}% has hit the 5% limit")
        if consecutive_losses >= 3:
            reasons.append(f"{consecutive_losses} consecutive losses — revenge trading risk")
        if stress_level > 8:
            reasons.append(f"Stress level {stress_level}/10 is dangerously high")
        if sleep_hours < 4:
            reasons.append(f"Only {sleep_hours}h sleep — cognitive performance severely impaired")

        allowed = len(reasons) == 0

        if not allowed:
            message = "Trading blocked — " + reasons[0]
            suggestion = self._suggest(score, daily_loss_pct, consecutive_losses)
        else:
            message = "Trading permitted — psychological state is acceptable"
            suggestion = "Proceed with your normal risk management rules"

        return {
            "allowed":    allowed,
            "score":      score,
            "message":    message,
            "reasons":    reasons,
            "suggestion": suggestion,
        }

    def _suggest(self, score, daily_loss, consec_losses):
        if daily_loss >= 5:
            return "Daily loss limit reached. Stop trading for today. Review what went wrong."
        if consec_losses >= 3:
            return "Step away from the screen for at least 30 minutes before reconsidering."
        if score < 40:
            return "Take a break, reset your mindset. Trade only when score is above 40."
        return "Reduce position size significantly before continuing."

decision_engine = DecisionEngine()
