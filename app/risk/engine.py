from enum import Enum
from datetime import datetime
from app.config import settings

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RiskEngine:

    def __init__(self):
        self.max_daily_loss_pct   = settings.max_daily_loss_pct
        self.max_open_trades      = settings.max_open_trades
        self.max_risk_per_trade   = settings.max_risk_per_trade_pct

    def validate_trade(
        self,
        account_balance: float,
        current_daily_loss_pct: float,
        risk_pct: float,
        open_positions: int,
        behavioral_score: int = 100,
    ) -> dict:
        checks = []
        blocked = False
        block_reason = None

        # Check 1: daily loss limit
        c1_pass = current_daily_loss_pct < self.max_daily_loss_pct
        checks.append({
            "rule": "Daily loss limit",
            "detail": f"{current_daily_loss_pct:.1f}% lost today — limit is {self.max_daily_loss_pct}%",
            "passed": c1_pass,
            "fail_reason": f"Daily loss {current_daily_loss_pct:.1f}% exceeds {self.max_daily_loss_pct}% limit"
        })
        if not c1_pass: blocked = True; block_reason = checks[-1]["fail_reason"]

        # Check 2: open trade limit
        c2_pass = open_positions < self.max_open_trades
        checks.append({
            "rule": "Open trade limit",
            "detail": f"{open_positions} open — limit is {self.max_open_trades}",
            "passed": c2_pass,
            "fail_reason": f"{open_positions} trades open — maximum is {self.max_open_trades}"
        })
        if not c2_pass and not blocked: blocked = True; block_reason = checks[-1]["fail_reason"]

        # Check 3: risk per trade
        c3_pass = risk_pct <= self.max_risk_per_trade
        checks.append({
            "rule": "Risk per trade",
            "detail": f"{risk_pct:.1f}% risk — limit is {self.max_risk_per_trade}%",
            "passed": c3_pass,
            "fail_reason": f"Trade risk {risk_pct:.1f}% exceeds {self.max_risk_per_trade}% limit"
        })
        if not c3_pass and not blocked: blocked = True; block_reason = checks[-1]["fail_reason"]

        # Check 4: behavioral score
        c4_pass = behavioral_score >= 40
        checks.append({
            "rule": "Behavioral score",
            "detail": f"Score {behavioral_score}/100 — minimum is 40",
            "passed": c4_pass,
            "fail_reason": f"Behavioral score {behavioral_score} too low — psychological risk detected"
        })
        if not c4_pass and not blocked: blocked = True; block_reason = checks[-1]["fail_reason"]

        risk_level = RiskLevel.LOW
        if current_daily_loss_pct >= self.max_daily_loss_pct: risk_level = RiskLevel.CRITICAL
        elif behavioral_score < 40: risk_level = RiskLevel.CRITICAL
        elif behavioral_score < 60 or current_daily_loss_pct > 3: risk_level = RiskLevel.HIGH
        elif risk_pct > 1.5: risk_level = RiskLevel.MEDIUM

        return {
            "approved": not blocked,
            "reason": block_reason if blocked else "All checks passed",
            "risk_level": risk_level.value,
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }

    def calculate_var(self, returns: list, confidence: float = 0.95) -> dict:
        if not returns: return {"var_95": 0, "var_99": 0}
        sorted_returns = sorted(returns)
        idx_95 = int(len(sorted_returns) * (1 - confidence))
        idx_99 = int(len(sorted_returns) * 0.01)
        return {
            "var_95": abs(sorted_returns[max(0, idx_95)]),
            "var_99": abs(sorted_returns[max(0, idx_99)]),
            "method": "historical",
            "sample_size": len(returns),
            "confidence_95": confidence,
        }
