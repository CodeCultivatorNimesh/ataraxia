"""
Pytest configuration and shared fixtures.
"""
import pytest
import asyncio
from httpx import AsyncClient
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest.fixture
def sample_candles():
    """Realistic OHLCV candle data for pattern testing."""
    return [
        {"o": 180.00, "h": 182.50, "l": 179.50, "c": 182.00, "v": 12000, "t": "2024-01-01"},
        {"o": 182.00, "h": 184.00, "l": 181.00, "c": 183.50, "v": 11000, "t": "2024-01-02"},
        {"o": 183.50, "h": 185.00, "l": 183.00, "c": 184.75, "v": 13000, "t": "2024-01-03"},
        {"o": 184.75, "h": 186.00, "l": 181.00, "c": 181.50, "v": 15000, "t": "2024-01-04"},
        {"o": 181.50, "h": 182.00, "l": 175.00, "c": 176.00, "v": 20000, "t": "2024-01-05"},
    ]


@pytest.fixture
def sample_trades():
    """Sample closed trade list for analytics testing."""
    return [
        {"pnl": 250.0,  "pnl_pct": 2.5,  "hold_time": 3600,  "quantity": 10,
         "asset_class": "STOCK",  "closed_at": "2024-01-02", "created_at": "2024-01-01"},
        {"pnl": -150.0, "pnl_pct": -1.5, "hold_time": 7200,  "quantity": 10,
         "asset_class": "STOCK",  "closed_at": "2024-01-03", "created_at": "2024-01-02"},
        {"pnl": 400.0,  "pnl_pct": 4.0,  "hold_time": 1800,  "quantity": 5,
         "asset_class": "CRYPTO_SPOT", "closed_at": "2024-01-04", "created_at": "2024-01-03"},
        {"pnl": -200.0, "pnl_pct": -2.0, "hold_time": 9000,  "quantity": 5,
         "asset_class": "CRYPTO_SPOT", "closed_at": "2024-01-05", "created_at": "2024-01-04"},
        {"pnl": 180.0,  "pnl_pct": 1.8,  "hold_time": 2700,  "quantity": 8,
         "asset_class": "STOCK",  "closed_at": "2024-01-06", "created_at": "2024-01-05"},
    ]


@pytest.fixture
def bearish_candles():
    """Three consecutive bearish candles for pattern testing."""
    return [
        {"o": 200.0, "h": 202.0, "l": 185.0, "c": 186.0, "v": 20000, "t": "2024-01-01"},
        {"o": 185.0, "h": 187.0, "l": 172.0, "c": 173.0, "v": 22000, "t": "2024-01-02"},
        {"o": 173.0, "h": 174.0, "l": 160.0, "c": 161.0, "v": 25000, "t": "2024-01-03"},
    ]


@pytest.fixture
def bullish_reversal_candles():
    """Morning star setup candles."""
    return [
        {"o": 200.0, "h": 202.0, "l": 178.0, "c": 179.0, "v": 20000, "t": "2024-01-01"},
        {"o": 178.0, "h": 181.0, "l": 176.0, "c": 179.5, "v": 8000,  "t": "2024-01-02"},
        {"o": 180.0, "h": 198.0, "l": 179.0, "c": 196.0, "v": 22000, "t": "2024-01-03"},
    ]
