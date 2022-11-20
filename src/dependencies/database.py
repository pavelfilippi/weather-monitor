from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from src.dependencies.config import Config
from src.dependencies.config import get_config


class Database:
    """Asynchronous database adapter"""

    def __init__(self, connection_url: str):
        self.engine = create_async_engine(connection_url)
        self.session_factory = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Obtains a new asynchronous session with managed transaction"""

        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


def get_database(config: Config = Depends(get_config)):
    """Database dependency factory"""
    return Database(
        f"mysql+aiomysql://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    )
