from fastapi import Depends, HTTPException, status
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session
from src.core.vector_db import vector_db
from src.core.config import settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session dependency
    """
    async with get_db_session() as session:
        yield session


def get_vector_db():
    """
    Get vector database dependency
    """
    return vector_db


def get_settings():
    """
    Get application settings dependency
    """
    return settings