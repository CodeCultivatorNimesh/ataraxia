from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket.manager import ws_manager
from app.patterns.alert_engine import alert_engine
from loguru import logger

router = APIRouter()

@router.websocket("/alerts")
async def ws_alerts(ws: WebSocket, symbol: str = Query(None)):
    channel = f"alerts_{symbol}" if symbol else "alerts_global"
    await ws_manager.connect(ws, channel)
    if symbol:
        alert_engine.subscribe(symbol.upper(), ws)
    try:
        await ws.send_json({"type": "connected", "channel": channel, "message": "WebSocket connected"})
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_json({"type": "pong"})
    except WebSocketDisconnect:
        await ws_manager.disconnect(ws, channel)
        if symbol:
            alert_engine.unsubscribe(symbol.upper(), ws)
        logger.info(f"WS disconnected: {channel}")

@router.websocket("/dashboard")
async def ws_dashboard(ws: WebSocket):
    await ws_manager.connect(ws, "dashboard")
    try:
        await ws.send_json({"type": "connected", "channel": "dashboard"})
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_json({"type": "pong"})
    except WebSocketDisconnect:
        await ws_manager.disconnect(ws, "dashboard")
