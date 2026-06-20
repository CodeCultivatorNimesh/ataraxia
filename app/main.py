from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.config import settings
from app.database.connection import init_db, close_db
from app.api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Trading Middleware...")
    await init_db()
    logger.info("Database connected")
    yield
    # Shutdown
    await close_db()
    logger.info("Trading Middleware stopped")

app = FastAPI(
    title="Trading Middleware API",
    description="Behavioral-risk-aware trading middleware bridge",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "active", "app": settings.app_name, "env": settings.app_env}

@app.get("/health")
async def health():
    return {"status": "healthy"}
