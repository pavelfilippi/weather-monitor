import pytest
from sqlalchemy import select

from src import models
from src.dependencies.database import Database


@pytest.mark.asyncio
async def test_database_session_rolls_back_on_exception(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(f"sqlite+aiosqlite:///{db_path}")

    async with db.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    with pytest.raises(RuntimeError):
        async with db.session() as session:
            session.add(models.MonitorUser(username="alice", password="secret"))
            raise RuntimeError("boom")

    async with db.session() as session:
        result = await session.execute(select(models.MonitorUser))
        assert result.scalars().all() == []

