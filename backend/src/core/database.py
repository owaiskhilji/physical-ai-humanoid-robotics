from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from src.core.config import settings


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Create async session maker
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for declarative models
Base = declarative_base()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logging.error(f"Database error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize the database by creating all tables.
    """
    try:
        logging.info("Starting database initialization...")
        # Import chat models to ensure they're registered with SQLAlchemy
        # This must be done inside the function to avoid circular imports
        import src.models.chat
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Error during database initialization: {e}")
        raise


async def close_db():
    """
    Close the database engine.
    """
    await engine.dispose()
    logging.info("Database engine disposed")