# Candlestick Patterns — Reference Guide

45 patterns supported across 4 categories.

## Single Candle (11)
| Pattern | Type | Reliability |
|---------|------|-------------|
| Doji | Neutral | Medium |
| Hammer | Bullish | High |
| Inverted Hammer | Bullish | Medium |
| Shooting Star | Bearish | High |
| Hanging Man | Bearish | Medium |
| Spinning Top | Neutral | Low |
| Bullish Marubozu | Bullish | High |
| Bearish Marubozu | Bearish | High |
| Dragonfly Doji | Bullish | High |
| Gravestone Doji | Bearish | High |
| Long-Legged Doji | Neutral | Medium |

## Double Candle (11)
| Pattern | Type | Reliability |
|---------|------|-------------|
| Bullish Engulfing | Bullish | High |
| Bearish Engulfing | Bearish | High |
| Bullish Harami | Bullish | Medium |
| Bearish Harami | Bearish | Medium |
| Piercing Line | Bullish | High |
| Dark Cloud Cover | Bearish | High |
| Tweezer Bottom | Bullish | Medium |
| Tweezer Top | Bearish | Medium |
| On Neck | Bearish | Medium |
| Kicking Bullish | Bullish | Very High |
| Kicking Bearish | Bearish | Very High |

## Triple Candle (12)
| Pattern | Type | Reliability |
|---------|------|-------------|
| Morning Star | Bullish | High |
| Evening Star | Bearish | High |
| Morning Doji Star | Bullish | Very High |
| Evening Doji Star | Bearish | Very High |
| Three White Soldiers | Bullish | High |
| Three Black Crows | Bearish | High |
| Three Inside Up | Bullish | High |
| Three Inside Down | Bearish | High |
| Three Outside Up | Bullish | High |
| Three Outside Down | Bearish | High |
| Abandoned Baby Bullish | Bullish | Very High |
| Abandoned Baby Bearish | Bearish | Very High |

## Continuation (11)
| Pattern | Type | Reliability |
|---------|------|-------------|
| Rising Three Methods | Bullish | High |
| Falling Three Methods | Bearish | High |
| Upside Tasuki Gap | Bullish | Medium |
| Downside Tasuki Gap | Bearish | Medium |
| Three Line Strike Bullish | Bullish | Medium |
| Three Line Strike Bearish | Bearish | Medium |
| Mat Hold | Bullish | High |
| Separating Lines Bullish | Bullish | Medium |
| Separating Lines Bearish | Bearish | Medium |
| In Neck | Bearish | Medium |
| Thrusting | Neutral | Low |

## How Detection Works

1. Candle data is sent to POST /api/v1/patterns/detect
2. All 45 patterns are checked against the last 1-5 candles
3. Patterns above the confidence threshold (default 0.7) are returned
4. Detections are saved to the candlestick_patterns table in PostgreSQL
5. Real-time alerts are broadcast via WebSocket to subscribed clients
6. Alerts are saved to the pattern_alerts table
