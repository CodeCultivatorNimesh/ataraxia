"""
Notification service — broadcasts alerts via WebSocket.
"""
from app.websocket.manager import ws_manager
from loguru import logger

async def send_pattern_alert(symbol: str, pattern_name: str, pattern_type: str, message: str):
    payload = {
        "type":         "pattern_alert",
        "symbol":       symbol,
        "pattern_name": pattern_name,
        "pattern_type": pattern_type,
        "message":      message,
    }
    await ws_manager.broadcast(f"alerts_{symbol}", payload)
    await ws_manager.broadcast("alerts_global", payload)
    logger.info(f"Alert sent: {symbol} — {pattern_name}")

async def send_risk_alert(message: str, risk_level: str = "HIGH"):
    payload = {"type": "risk_alert", "risk_level": risk_level, "message": message}
    await ws_manager.broadcast_all(payload)

async def send_dashboard_update(data: dict):
    await ws_manager.broadcast("dashboard", {"type": "dashboard_update", "data": data})
