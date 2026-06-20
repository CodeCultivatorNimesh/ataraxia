"""
Seed database with initial data.
Usage: python -m app.database.seeds
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import AsyncSessionLocal, init_db
from loguru import logger

async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        logger.info("Database seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed())
