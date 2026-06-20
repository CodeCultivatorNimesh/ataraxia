from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings
from loguru import logger

class Base(DeclarativeBase):
    pass

_is_sqlite = settings.database_url.startswith("sqlite")
_engine_kwargs = {} if _is_sqlite else {"pool_size": 10, "max_overflow": 20}
engine = create_async_engine(settings.database_url, echo=False, **_engine_kwargs)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    # Import all models so their tables are registered with Base.metadata
    import app.models.trade        # noqa: F401
    import app.models.pattern      # noqa: F401
    import app.models.behavioral   # noqa: F401
    import app.models.journal      # noqa: F401
    import app.models.user         # noqa: F401
    import app.models.alert        # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")

async def close_db():
    await engine.dispose()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
