from datetime import datetime
from app.psychology.behavioral_engine import behavioral_engine
from app.psychology.bias_detector import bias_detector

class JournalEngine:

    def generate_entry(self, trade: dict, recent_trades: list, stress: int = 5, sleep: float = 7.0) -> dict:
        insights = behavioral_engine.analyze(recent_trades, stress, sleep)
        biases = bias_detector.detect(recent_trades)
        auto_notes = self._build_notes(trade, insights, biases)
        return {
            "timestamp":        datetime.utcnow().isoformat(),
            "symbol":           trade.get("symbol"),
            "direction":        trade.get("direction"),
            "entry":            trade.get("entry_price"),
            "exit":             trade.get("exit_price"),
            "pnl":              trade.get("pnl"),
            "emotion_score":    insights["emotional_score"],
            "warnings":         insights["warnings"],
            "biases_detected":  [b["bias"] for b in biases],
            "auto_notes":       auto_notes,
        }

    def _build_notes(self, trade, insights, biases) -> str:
        notes = []
        if trade.get("pnl", 0) > 0:
            notes.append("✅ Winning trade.")
        else:
            notes.append("❌ Losing trade.")
        if insights["revenge_trading"]:
            notes.append("⚠ Possible revenge trade — entered after consecutive losses.")
        if insights["overtrading"]:
            notes.append("⚠ Overtrading pattern detected today.")
        if insights["loss_aversion"]:
            notes.append("⚠ Loss aversion bias active — review exit discipline.")
        for b in biases:
            notes.append(f"🔍 Bias detected: {b['bias']} ({b['severity']}) — {b['detail']}")
        score = insights["emotional_score"]
        if score < 40:
            notes.append("🔴 Psychological state was poor during this trade.")
        elif score < 60:
            notes.append("🟡 Moderate psychological risk during this trade.")
        else:
            notes.append("🟢 Psychological state was acceptable.")
        return " | ".join(notes)

journal_engine = JournalEngine()
