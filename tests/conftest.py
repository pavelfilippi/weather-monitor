import datetime as dt
from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable, AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.requests import Request

from src.main import app as fastapi_app
from src import models
from src.dependencies.database import get_database


class TestDatabase:
    def __init__(self, engine: AsyncEngine):
        self.engine = engine
        self.session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[TestDatabase, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    db = TestDatabase(engine)
    try:
        yield db
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def app(test_db: TestDatabase) -> AsyncGenerator[Callable, None]:
    fastapi_app.dependency_overrides[get_database] = lambda: test_db
    try:
        yield fastapi_app
    finally:
        fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def seed_user(test_db: TestDatabase) -> Callable[[str, str], AsyncGenerator[models.MonitorUser, None]]:
    async def _seed(username: str = "alice", password: str = "secret") -> models.MonitorUser:
        async with test_db.session() as session:
            user = models.MonitorUser(username=username, password=password)
            session.add(user)
            await session.flush()
            return user

    return _seed


@pytest_asyncio.fixture
async def seed_station(
    test_db: TestDatabase, seed_user
) -> Callable[[models.MonitorUser | None, str, float, float], AsyncGenerator[models.WeatherStation, None]]:
    async def _seed(
        user: models.MonitorUser | None = None,
        api_key: str = "station-key",
        longitude: float = 10.0,
        latitude: float = 20.0,
    ) -> models.WeatherStation:
        if user is None:
            user = await seed_user()
        async with test_db.session() as session:
            station = models.WeatherStation(
                longitude=longitude,
                latitude=latitude,
                api_key=api_key,
                user_id=user.id,
            )
            session.add(station)
            await session.flush()
            return station

    return _seed


@pytest_asyncio.fixture
async def seed_condition(test_db: TestDatabase, seed_station) -> Callable[..., AsyncGenerator[models.StationCondition, None]]:
    async def _seed(
        station: models.WeatherStation | None = None,
        time: dt.datetime | None = None,
        battery_percentage: float | None = 50.0,
        temperature: float | None = 21.5,
        humidity: float | None = 60.0,
        pressure: float | None = 1012.0,
    ) -> models.StationCondition:
        if station is None:
            station = await seed_station()
        if time is None:
            time = dt.datetime(2026, 1, 1, 12, 0, 0)
        async with test_db.session() as session:
            cond = models.StationCondition(
                time=time,
                station_id=station.station_id,
                battery_percentage=battery_percentage,
                temperature=temperature,
                humidity=humidity,
                pressure=pressure,
            )
            session.add(cond)
            return cond

    return _seed


@pytest.fixture
def make_request() -> Callable[[dict[str, str]], Request]:
    def _make(headers: dict[str, str]) -> Request:
        raw_headers = [(k.lower().encode(), v.encode()) for k, v in headers.items()]
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": raw_headers,
            "query_string": b"",
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
            "scheme": "http",
        }
        return Request(scope)

    return _make

