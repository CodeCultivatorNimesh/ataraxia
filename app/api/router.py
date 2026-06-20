from fastapi import APIRouter
from app.api.routes import position, risk, patterns, journal, behavioral, broker, analytics, websocket

api_router = APIRouter()

api_router.include_router(position.router,   prefix="/position",   tags=["Position Sizing"])
api_router.include_router(risk.router,        prefix="/risk",        tags=["Risk Engine"])
api_router.include_router(patterns.router,    prefix="/patterns",    tags=["Candlestick Patterns"])
api_router.include_router(journal.router,     prefix="/journal",     tags=["Trade Journal"])
api_router.include_router(behavioral.router,  prefix="/behavioral",  tags=["Behavioral Analytics"])
api_router.include_router(broker.router,      prefix="/broker",      tags=["Broker Bridge"])
api_router.include_router(analytics.router,   prefix="/analytics",   tags=["Analytics"])
api_router.include_router(websocket.router,   prefix="/ws",          tags=["WebSocket"])
