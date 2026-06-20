"""
Database migration helper.
Run this to create or update all tables.
Usage: python -m app.database.migrations
"""
import asyncio
from app.database.connection import init_db
from loguru import logger

async def run_migrations():
    logger.info("Running database migrations...")
    await init_db()
    logger.info("Migrations complete.")

if __name__ == "__main__":
    asyncio.run(run_migrations())
