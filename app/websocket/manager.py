from fastapi import WebSocket
from typing import Dict, List
from loguru import logger
import json

class WebSocketManager:

    def __init__(self):
        self.active: Dict[str, List[WebSocket]] = {}

    async def connect(self, ws: WebSocket, channel: str):
        await ws.accept()
        if channel not in self.active:
            self.active[channel] = []
        self.active[channel].append(ws)
        logger.info(f"WS connected: {channel} ({len(self.active[channel])} clients)")

    async def disconnect(self, ws: WebSocket, channel: str):
        if channel in self.active:
            self.active[channel] = [w for w in self.active[channel] if w != ws]

    async def broadcast(self, channel: str, data: dict):
        if channel not in self.active:
            return
        dead = []
        for ws in self.active[channel]:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(ws, channel)

    async def broadcast_all(self, data: dict):
        for channel in self.active:
            await self.broadcast(channel, data)

ws_manager = WebSocketManager()
