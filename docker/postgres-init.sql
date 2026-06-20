-- Trading Middleware Database Initialization

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER DEFAULT 1,
    symbol          VARCHAR(20) NOT NULL,
    asset_class     VARCHAR(20) NOT NULL DEFAULT 'STOCK',
    direction       VARCHAR(10) NOT NULL,
    broker          VARCHAR(20),
    margin_mode     VARCHAR(10) DEFAULT 'NONE',
    leverage        FLOAT DEFAULT 1.0,
    entry_price     FLOAT NOT NULL,
    exit_price      FLOAT,
    stop_loss       FLOAT,
    take_profit     FLOAT,
    quantity        FLOAT NOT NULL,
    notional_value  FLOAT,
    pnl             FLOAT,
    pnl_pct         FLOAT,
    risk_amount     FLOAT,
    risk_pct        FLOAT,
    atr_value       FLOAT,
    emotion_score   INTEGER,
    is_open         BOOLEAN DEFAULT TRUE,
    opened_at       TIMESTAMPTZ DEFAULT NOW(),
    closed_at       TIMESTAMPTZ,
    notes           TEXT,
    patterns_at_entry TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ
);

-- Candlestick patterns table
CREATE TABLE IF NOT EXISTS candlestick_patterns (
    id              SERIAL PRIMARY KEY,
    symbol          VARCHAR(20) NOT NULL,
    timeframe       VARCHAR(10) NOT NULL,
    pattern_name    VARCHAR(50) NOT NULL,
    pattern_type    VARCHAR(20),
    category        VARCHAR(20),
    confidence      FLOAT,
    open            FLOAT,
    high            FLOAT,
    low             FLOAT,
    close           FLOAT,
    volume          FLOAT,
    candle_time     TIMESTAMPTZ NOT NULL,
    detected_at     TIMESTAMPTZ DEFAULT NOW(),
    alert_sent      BOOLEAN DEFAULT FALSE,
    description     TEXT
);

-- Pattern alerts table
CREATE TABLE IF NOT EXISTS pattern_alerts (
    id              SERIAL PRIMARY KEY,
    symbol          VARCHAR(20) NOT NULL,
    pattern_name    VARCHAR(50) NOT NULL,
    pattern_type    VARCHAR(20),
    timeframe       VARCHAR(10),
    message         TEXT,
    confidence      FLOAT,
    price           FLOAT,
    is_read         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Behavioral metrics table
CREATE TABLE IF NOT EXISTS behavioral_metrics (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER DEFAULT 1,
    behavioral_score    INTEGER,
    revenge_trading     BOOLEAN DEFAULT FALSE,
    overtrading         BOOLEAN DEFAULT FALSE,
    loss_aversion       BOOLEAN DEFAULT FALSE,
    fomo_detected       BOOLEAN DEFAULT FALSE,
    overconfidence      BOOLEAN DEFAULT FALSE,
    recency_bias        BOOLEAN DEFAULT FALSE,
    consecutive_losses  INTEGER DEFAULT 0,
    stress_level        INTEGER,
    sleep_hours         FLOAT,
    daily_loss_pct      FLOAT,
    notes               TEXT,
    recorded_at         TIMESTAMPTZ DEFAULT NOW()
);

-- Journal entries table
CREATE TABLE IF NOT EXISTS journal_entries (
    id                  SERIAL PRIMARY KEY,
    trade_id            INTEGER,
    user_id             INTEGER DEFAULT 1,
    emotion_score       INTEGER,
    pre_trade_notes     TEXT,
    post_trade_notes    TEXT,
    auto_notes          TEXT,
    warnings            TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_opened_at ON trades(opened_at);
CREATE INDEX IF NOT EXISTS idx_patterns_symbol ON candlestick_patterns(symbol);
CREATE INDEX IF NOT EXISTS idx_patterns_candle_time ON candlestick_patterns(candle_time);
CREATE INDEX IF NOT EXISTS idx_alerts_unread ON pattern_alerts(is_read) WHERE is_read = FALSE;

-- Seed: all candlestick patterns reference data
CREATE TABLE IF NOT EXISTS pattern_catalog (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(50) UNIQUE NOT NULL,
    category     VARCHAR(20),
    pattern_type VARCHAR(20),
    description  TEXT,
    reliability  VARCHAR(10)
);

INSERT INTO pattern_catalog (name, category, pattern_type, description, reliability) VALUES
('Doji','single','neutral','Open and close nearly equal — indecision','medium'),
('Hammer','single','bullish','Long lower wick — buyers rejected lows','high'),
('Inverted Hammer','single','bullish','Long upper wick — potential reversal','medium'),
('Shooting Star','single','bearish','Long upper wick — sellers rejected highs','high'),
('Hanging Man','single','bearish','Bearish reversal after uptrend','medium'),
('Spinning Top','single','neutral','Small body, equal wicks — indecision','low'),
('Bullish Marubozu','single','bullish','No wicks — strong bullish momentum','high'),
('Bearish Marubozu','single','bearish','No wicks — strong bearish momentum','high'),
('Dragonfly Doji','single','bullish','Buyers rejected lows — reversal signal','high'),
('Gravestone Doji','single','bearish','Sellers rejected highs — reversal signal','high'),
('Long-Legged Doji','single','neutral','High uncertainty — equal buying and selling','medium'),
('Bullish Engulfing','double','bullish','Second candle engulfs first bearish candle','high'),
('Bearish Engulfing','double','bearish','Second candle engulfs first bullish candle','high'),
('Bullish Harami','double','bullish','Small bullish inside large bearish','medium'),
('Bearish Harami','double','bearish','Small bearish inside large bullish','medium'),
('Piercing Line','double','bullish','Closes above midpoint of prior bearish','high'),
('Dark Cloud Cover','double','bearish','Closes below midpoint of prior bullish','high'),
('Tweezer Bottom','double','bullish','Equal lows signal support','medium'),
('Tweezer Top','double','bearish','Equal highs signal resistance','medium'),
('On Neck','double','bearish','Closes near prior low — bearish continuation','medium'),
('Kicking Bullish','double','bullish','Gap up marubozu — very strong reversal','very high'),
('Kicking Bearish','double','bearish','Gap down marubozu — very strong reversal','very high'),
('Morning Star','triple','bullish','3-candle bottom reversal pattern','high'),
('Evening Star','triple','bearish','3-candle top reversal pattern','high'),
('Morning Doji Star','triple','bullish','Morning star with doji — powerful reversal','very high'),
('Evening Doji Star','triple','bearish','Evening star with doji — powerful reversal','very high'),
('Three White Soldiers','triple','bullish','3 consecutive large bullish candles','high'),
('Three Black Crows','triple','bearish','3 consecutive large bearish candles','high'),
('Three Inside Up','triple','bullish','Harami confirmed by third bullish candle','high'),
('Three Inside Down','triple','bearish','Harami confirmed by third bearish candle','high'),
('Three Outside Up','triple','bullish','Engulfing confirmed by third candle','high'),
('Three Outside Down','triple','bearish','Engulfing confirmed by third candle','high'),
('Abandoned Baby Bullish','triple','bullish','Very rare — gap doji gap pattern','very high'),
('Abandoned Baby Bearish','triple','bearish','Very rare — gap doji gap pattern','very high'),
('Rising Three Methods','continuation','bullish','Brief pause within uptrend','high'),
('Falling Three Methods','continuation','bearish','Brief pause within downtrend','high'),
('Upside Tasuki Gap','continuation','bullish','Gap not fully filled — trend continues','medium'),
('Downside Tasuki Gap','continuation','bearish','Gap not fully filled — trend continues','medium'),
('Three Line Strike Bullish','continuation','bullish','Strike after 3 bearish candles','medium'),
('Three Line Strike Bearish','continuation','bearish','Strike after 3 bullish candles','medium'),
('Mat Hold','continuation','bullish','Strong uptrend continues after pause','high'),
('Separating Lines Bullish','continuation','bullish','Same open, direction reverses bullish','medium'),
('Separating Lines Bearish','continuation','bearish','Same open, direction reverses bearish','medium'),
('In Neck','continuation','bearish','Weak recovery — bearish continuation','medium'),
('Thrusting','continuation','neutral','Closes below midpoint — trend may continue','low')
ON CONFLICT (name) DO NOTHING;

COMMIT;
