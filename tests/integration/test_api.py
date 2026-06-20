"""
Integration tests for FastAPI endpoints.
Run with: pytest tests/integration/test_api.py -v
Requires: running PostgreSQL and Redis (docker-compose up -d postgres redis)
"""
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/")
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_position_spot():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.post("/api/v1/position/spot", json={
            "account_balance": 10000,
            "risk_pct": 1.0,
            "entry_price": 150,
            "atr_value": 3.5,
            "direction": "long",
            "volatility": "medium",
            "asset_type": "stock"
        })
    assert r.status_code == 200
    data = r.json()
    assert data["position_size"] > 0
    assert data["stop_loss_price"] == 143.0

@pytest.mark.asyncio
async def test_risk_validate_approve():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.post("/api/v1/risk/validate", json={
            "account_balance": 10000,
            "current_daily_loss_pct": 1.0,
            "risk_pct": 1.0,
            "open_positions": 2,
            "behavioral_score": 80,
        })
    assert r.status_code == 200
    assert r.json()["approved"] == True

@pytest.mark.asyncio
async def test_risk_validate_block():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.post("/api/v1/risk/validate", json={
            "account_balance": 10000,
            "current_daily_loss_pct": 6.0,
            "risk_pct": 1.0,
            "open_positions": 2,
            "behavioral_score": 80,
        })
    assert r.status_code == 200
    assert r.json()["approved"] == False

@pytest.mark.asyncio
async def test_pattern_catalog():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/api/v1/patterns/catalog")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 45
    assert len(data["single"]) == 11
    assert len(data["double"]) == 11

@pytest.mark.asyncio
async def test_pattern_detect():
    candles = [
        {"o":110,"h":112,"l":100,"c":101,"v":1000,"t":"2024-01-01"},
        {"o":100,"h":102,"l":99, "c":101,"v":800, "t":"2024-01-02"},
        {"o":101,"h":115,"l":100,"c":112,"v":1200,"t":"2024-01-03"},
    ]
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.post("/api/v1/patterns/detect", json={
            "symbol": "AAPL", "timeframe": "1d",
            "candles": candles, "current_price": 112
        })
    assert r.status_code == 200
    assert "bias" in r.json()
