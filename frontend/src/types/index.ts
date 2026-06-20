// ── Shared types ─────────────────────────────────────────────

export interface Trade {
  id:            number;
  symbol:        string;
  direction:     "LONG" | "SHORT";
  asset_class:   string;
  entry_price:   number;
  exit_price?:   number;
  quantity:      number;
  pnl?:          number;
  pnl_pct?:      number;
  is_open:       boolean;
  emotion_score?: number;
  opened_at:     string;
  closed_at?:    string;
}

export interface Pattern {
  pattern_name:  string;
  pattern_type:  "bullish" | "bearish" | "neutral";
  category:      string;
  confidence:    number;
  description:   string;
  candle_time:   string;
}

export interface PatternSummary {
  total_detected: number;
  bullish_count:  number;
  bearish_count:  number;
  neutral_count:  number;
  bias:           "bullish" | "bearish" | "neutral";
  strongest?:     Pattern;
  patterns:       Pattern[];
}

export interface RiskValidation {
  approved:    boolean;
  reason:      string;
  risk_level:  "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  checks:      { rule: string; detail: string; passed: boolean; fail_reason?: string }[];
  timestamp:   string;
}

export interface PositionResult {
  risk_amount:        number;
  atr_stop_distance:  number;
  stop_loss_price:    number;
  position_size:      number;
  unit:               string;
  atr_multiplier:     number;
  volatility:         string;
  direction:          string;
}

export interface BehavioralInsights {
  behavioral_score:  number;
  revenge_trading:   boolean;
  overtrading:       boolean;
  loss_aversion:     boolean;
  overconfidence:    boolean;
  warnings:          string[];
  biases:            { bias: string; severity: string; detail: string }[];
}

export interface DashboardData {
  account: {
    balance:          number;
    starting_balance: number;
    total_pnl:        number;
    today_pnl:        number;
    today_loss_pct:   number;
  };
  performance: {
    total_trades:      number;
    win_rate:          number;
    profit_factor:     number;
    sharpe_ratio:      number;
    expectancy:        number;
    avg_win:           number;
    avg_loss:          number;
    reward_risk_ratio: number;
    max_drawdown_pct:  number;
  };
  behavioral: {
    score:            number;
    state:            "healthy" | "moderate" | "critical";
    trading_allowed:  boolean;
  };
  open_trades:   Trade[];
  top_patterns:  { pattern: string; count: number }[];
  equity_curve:  { date: string; daily_pnl: number; cumulative: number; balance: number }[];
}

export type Volatility = "low" | "medium" | "high" | "extreme";
export type AssetClass = "STOCK" | "CRYPTO_SPOT" | "CRYPTO_FUTURES" | "FUTURES" | "FOREX";
export type Broker = "alpaca" | "binance" | "binance_futures";
