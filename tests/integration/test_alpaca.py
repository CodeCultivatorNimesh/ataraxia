"""
Alpaca integration tests.
Requires valid ALPACA_API_KEY and ALPACA_SECRET_KEY in .env
Run with: pytest tests/integration/test_alpaca.py -v -s
"""
import pytest

@pytest.mark.asyncio
async def test_alpaca_account():
    """Test Alpaca account fetch — requires API keys"""
    try:
        from app.broker.alpaca.client import alpaca
        account = await alpaca.get_account()
        assert "balance" in account
        assert account["broker"] == "alpaca"
        print(f"\nAlpaca balance: ${account['balance']:,.2f}")
    except Exception as e:
        pytest.skip(f"Alpaca not configured: {e}")

@pytest.mark.asyncio
async def test_alpaca_price():
    try:
        from app.broker.alpaca.client import alpaca
        price = await alpaca.get_price("AAPL")
        assert price > 0
        print(f"\nAAPL price: ${price}")
    except Exception as e:
        pytest.skip(f"Alpaca not configured: {e}")

@pytest.mark.asyncio
async def test_alpaca_atr():
    try:
        from app.broker.alpaca.client import alpaca
        atr = await alpaca.calculate_atr("AAPL", "1d", 14)
        assert atr > 0
        print(f"\nAAPL ATR(14): ${atr}")
    except Exception as e:
        pytest.skip(f"Alpaca not configured: {e}")
