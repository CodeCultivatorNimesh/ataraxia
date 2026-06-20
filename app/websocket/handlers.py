"""
WebSocket message handlers — process incoming messages from clients.
"""
from app.websocket.manager import ws_manager
from loguru import logger

async def handle_message(channel: str, data: str):
    if data == "ping":
        await ws_manager.broadcast(channel, {"type": "pong"})
    elif data.startswith("subscribe:"):
        symbol = data.split(":")[1].upper()
        logger.info(f"Client subscribed to {symbol} alerts")
    else:
        logger.debug(f"WS message on {channel}: {data}")
