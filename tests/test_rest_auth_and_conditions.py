import datetime as dt

import pytest
from sqlalchemy import select

from src import models
from src.dependencies.auth import get_auth_weather_station


@pytest.mark.asyncio
async def test_token_unknown_user_returns_400(client):
    resp = await client.post("/token", data={"username": "missing", "password": "pw"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_token_wrong_password_returns_400(client, seed_user):
    await seed_user(username="alice", password="secret")
    resp = await client.post("/token", data={"username": "alice", "password": "wrong"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_token_success_returns_bearer_token(client, seed_user):
    await seed_user(username="alice", password="secret")
    resp = await client.post("/token", data={"username": "alice", "password": "secret"})
    assert resp.status_code == 200
    assert resp.json() == {"access_token": "alice", "token_type": "bearer"}


@pytest.mark.asyncio
async def test_conditions_missing_auth_returns_401(client):
    payload = {
        "time": dt.datetime(2026, 1, 1, 12, 0, 0).isoformat(),
        "battery_percentage": 50.0,
        "temperature": 20.0,
        "humidity": 70.0,
        "pressure": 1000.0,
    }
    resp = await client.post("/conditions", json=payload)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_conditions_valid_station_inserts_row(client, test_db, seed_station):
    station = await seed_station(api_key="station-key")
    payload = {
        "time": dt.datetime(2026, 1, 1, 12, 0, 0).isoformat(),
        "battery_percentage": 51.0,
        "temperature": 19.5,
        "humidity": 65.0,
        "pressure": 1005.0,
    }
    resp = await client.post("/conditions", json=payload, headers={"Authorization": f"Bearer {station.api_key}"})
    assert resp.status_code == 200

    async with test_db.session() as session:
        result = await session.execute(select(models.StationCondition))
        rows = result.scalars().all()
        assert len(rows) == 1
        assert rows[0].station_id == station.station_id


@pytest.mark.asyncio
async def test_get_auth_weather_station_missing_header_returns_none(test_db, make_request):
    req = make_request({})
    station = await get_auth_weather_station(request=req, db=test_db)  # type: ignore[arg-type]
    assert station is None


@pytest.mark.asyncio
async def test_get_auth_weather_station_invalid_format_returns_none(test_db, make_request):
    req = make_request({"Authorization": "Bearer"})
    station = await get_auth_weather_station(request=req, db=test_db)  # type: ignore[arg-type]
    assert station is None


@pytest.mark.asyncio
async def test_get_auth_weather_station_wrong_type_returns_none(test_db, make_request):
    req = make_request({"Authorization": "Token abc"})
    station = await get_auth_weather_station(request=req, db=test_db)  # type: ignore[arg-type]
    assert station is None


@pytest.mark.asyncio
async def test_get_auth_weather_station_valid_bearer_returns_station(test_db, make_request, seed_station):
    st = await seed_station(api_key="station-key")
    req = make_request({"Authorization": f"Bearer {st.api_key}"})
    station = await get_auth_weather_station(request=req, db=test_db)  # type: ignore[arg-type]
    assert station is not None
    assert station.station_id == st.station_id

