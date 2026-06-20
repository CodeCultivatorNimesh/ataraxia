from dataclasses import dataclass
from enum import Enum

class Volatility(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

ATR_MULTIPLIERS = {Volatility.LOW: 1.5, Volatility.MEDIUM: 2.0, Volatility.HIGH: 2.5, Volatility.EXTREME: 3.0}
RISK_ADJUSTMENTS = {Volatility.LOW: 1.0, Volatility.MEDIUM: 1.0, Volatility.HIGH: 0.8, Volatility.EXTREME: 0.6}

@dataclass
class PositionSizeResult:
    risk_amount: float
    atr_stop_distance: float
    stop_loss_price: float
    position_size: float
    unit: str
    atr_multiplier: float
    risk_adjustment: float
    volatility: str
    direction: str

class PositionSizeCalculator:

    @staticmethod
    def calculate_spot(
        account_balance: float,
        risk_pct: float,
        entry_price: float,
        atr_value: float,
        direction: str = "long",
        volatility: str = "medium",
        asset_type: str = "stock"
    ) -> PositionSizeResult:
        vol = Volatility(volatility)
        mult = ATR_MULTIPLIERS[vol]
        adj = RISK_ADJUSTMENTS[vol]
        stop_dist = atr_value * mult
        stop_price = entry_price - stop_dist if direction == "long" else entry_price + stop_dist
        risk_amount = account_balance * (risk_pct / 100) * adj
        if stop_dist == 0:
            raise ValueError("ATR stop distance cannot be zero")
        qty = risk_amount / stop_dist
        unit = "coins" if asset_type == "crypto" else "shares"
        return PositionSizeResult(
            risk_amount=round(risk_amount, 2),
            atr_stop_distance=round(stop_dist, 4),
            stop_loss_price=round(stop_price, 4),
            position_size=round(qty, 4),
            unit=unit,
            atr_multiplier=mult,
            risk_adjustment=adj,
            volatility=volatility,
            direction=direction
        )

    @staticmethod
    def calculate_crypto_futures_cross(
        account_balance: float,
        entry_price: float,
        atr_value: float,
        volatility: str = "medium",
        direction: str = "long",
        maintenance_margin_pct: float = 0.5
    ) -> dict:
        vol_config = {
            "low": {"leverage": 8, "position_pct": 8},
            "medium": {"leverage": 6, "position_pct": 6},
            "high": {"leverage": 5, "position_pct": 5},
            "extreme": {"leverage": 5, "position_pct": 5},
        }
        cfg = vol_config[volatility]
        leverage = cfg["leverage"]
        notional_power = account_balance * leverage
        position_opened = notional_power * (cfg["position_pct"] / 100)
        notional_remaining = notional_power - position_opened
        mm = maintenance_margin_pct / 100
        if direction == "long":
            liquidation_price = entry_price * (1 - (1 / leverage) + mm)
        else:
            liquidation_price = entry_price * (1 + (1 / leverage) - mm)
        liq_distance_pct = abs(entry_price - liquidation_price) / entry_price * 100
        atr_mult = ATR_MULTIPLIERS[Volatility(volatility)]
        stop_dist = atr_value * atr_mult
        stop_price = entry_price - stop_dist if direction == "long" else entry_price + stop_dist
        stop_pct = stop_dist / entry_price * 100
        return {
            "leverage": leverage,
            "notional_power": round(notional_power, 2),
            "position_opened": round(position_opened, 2),
            "notional_remaining": round(notional_remaining, 2),
            "averaging_entries_possible": int(notional_remaining / position_opened),
            "liquidation_price": round(liquidation_price, 2),
            "liquidation_distance_pct": round(liq_distance_pct, 2),
            "atr_stop_price": round(stop_price, 2),
            "atr_stop_distance_pct": round(stop_pct, 2),
            "stop_before_liquidation": stop_pct < liq_distance_pct,
        }

    @staticmethod
    def calculate_crypto_futures_isolated(
        account_balance: float,
        entry_price: float,
        atr_value: float,
        volatility: str = "medium",
        direction: str = "long",
        open_positions: int = 0
    ) -> dict:
        vol_config = {
            "low": {"leverage": 5, "position_pct": 8},
            "medium": {"leverage": 4, "position_pct": 6},
            "high": {"leverage": 3, "position_pct": 5},
            "extreme": {"leverage": 3, "position_pct": 5},
        }
        cfg = vol_config[volatility]
        leverage = cfg["leverage"]
        notional = account_balance * leverage
        position = notional * (cfg["position_pct"] / 100)
        margin_used = position / leverage
        liq_price = entry_price * (1 - (1/leverage) + 0.005) if direction == "long" else entry_price * (1 + (1/leverage) - 0.005)
        liq_pct = abs(entry_price - liq_price) / entry_price * 100
        stop_dist = atr_value * ATR_MULTIPLIERS[Volatility(volatility)]
        stop_price = entry_price - stop_dist if direction == "long" else entry_price + stop_dist
        stop_pct = stop_dist / entry_price * 100
        slots_remaining = 3 - open_positions
        return {
            "leverage": leverage,
            "margin_used": round(margin_used, 2),
            "notional_value": round(notional, 2),
            "position_size": round(position, 2),
            "slots_used": open_positions,
            "slots_remaining": max(0, slots_remaining),
            "new_trade_allowed": slots_remaining > 0,
            "liquidation_price": round(liq_price, 2),
            "liquidation_distance_pct": round(liq_pct, 2),
            "atr_stop_price": round(stop_price, 2),
            "stop_before_liquidation": stop_pct < liq_pct,
        }
