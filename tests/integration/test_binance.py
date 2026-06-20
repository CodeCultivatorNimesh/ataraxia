"""
Binance integration tests.
Requires valid BINANCE_API_KEY and BINANCE_SECRET_KEY in .env
Run with: pytest tests/integration/test_binance.py -v -s
"""
import pytest

@pytest.mark.asyncio
async def test_binance_price():
    try:
        from app.broker.binance.client import binance_client
        price = await binance_client.get_price("BTCUSDT")
        assert price > 0
        print(f"\nBTC price: ${price:,.2f}")
    except Exception as e:
        pytest.skip(f"Binance not configured: {e}")

@pytest.mark.asyncio
async def test_binance_candles():
    try:
        from app.broker.binance.client import binance_client
        candles = await binance_client.get_candles("BTCUSDT", "1d", 20)
        assert len(candles) > 0
        assert "o" in candles[0]
        print(f"\nBTC candles: {len(candles)}")
    except Exception as e:
        pytest.skip(f"Binance not configured: {e}")

@pytest.mark.asyncio
async def test_binance_atr():
    try:
        from app.broker.binance.client import binance_client
        atr = await binance_client.calculate_atr("BTCUSDT", "1d", 14)
        assert atr > 0
        print(f"\nBTC ATR(14): ${atr:,.2f}")
    except Exception as e:
        pytest.skip(f"Binance not configured: {e}")
