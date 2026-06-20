class BiasDetector:

    BIAS_DESCRIPTIONS = {
        "loss_aversion":      "Holding losing trades too long hoping they recover",
        "confirmation_bias":  "Seeking information that confirms existing view",
        "recency_bias":       "Overweighting recent trades in decision making",
        "overconfidence":     "Increasing position size after a winning streak",
        "gambler_fallacy":    "Expecting a reversal simply because of a recent streak",
        "anchoring":          "Fixating on entry price rather than current market reality",
        "fomo":               "Entering trades due to fear of missing a move",
        "revenge_trading":    "Trading to recover losses rather than following strategy",
    }

    def detect(self, trades: list) -> list:
        detected = []
        if not trades: return detected

        wins = [t for t in trades if t.get("pnl", 0) > 0]
        losses = [t for t in trades if t.get("pnl", 0) < 0]

        losing_hold = [t.get("hold_time", 0) for t in losses]
        winning_hold = [t.get("hold_time", 0) for t in wins]
        if losing_hold and winning_hold:
            avg_l = sum(losing_hold) / len(losing_hold)
            avg_w = sum(winning_hold) / len(winning_hold)
            if avg_l > avg_w * 1.5:
                detected.append({"bias": "loss_aversion", "severity": "high",
                    "detail": f"Holding losers {round(avg_l/max(avg_w,1),1)}× longer than winners"})

        if len(wins) >= 5:
            sizes = [t.get("quantity", 0) for t in trades[-6:] if t.get("pnl", 0) > 0]
            if len(sizes) >= 2 and sizes[-1] > sizes[0] * 1.3:
                detected.append({"bias": "overconfidence", "severity": "medium",
                    "detail": "Position sizes increasing after win streak"})

        consec_losses = 0
        for t in reversed(trades):
            if t.get("pnl", 0) < 0: consec_losses += 1
            else: break
        if consec_losses >= 3:
            detected.append({"bias": "revenge_trading", "severity": "medium",
                "detail": f"{consec_losses} consecutive losses — high risk of emotional trade"})

        recent = trades[-3:] if len(trades) >= 3 else trades
        recent_loss_rate = sum(1 for t in recent if t.get("pnl", 0) < 0) / len(recent)
        if recent_loss_rate > 0.6 and len(trades) > 10:
            detected.append({"bias": "recency_bias", "severity": "watch",
                "detail": "Recent losses may be skewing current confidence"})

        return detected

bias_detector = BiasDetector()
