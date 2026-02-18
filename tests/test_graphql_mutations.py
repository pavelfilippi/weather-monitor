import pytest
from sqlalchemy import select

from src import models


@pytest.mark.asyncio
async def test_add_weather_station_success(client, test_db, seed_user):
    user = await seed_user(username="alice", password="secret")
    mutation = """
        mutation {
            addWeatherStation(weatherStation: {longitude: 1.0, latitude: 2.0, apiKey: "k"}) {
                __typename
                ... on WeatherStation {
                    resourceId
                    location { lat long }
                }
            }
        }
    """
    resp = await client.post("/graphql", json={"query": mutation}, headers={"Authorize": f"Bearer {user.username}"})
    payload = resp.json()
    assert "errors" not in payload
    data = payload["data"]["addWeatherStation"]
    assert data["__typename"] == "WeatherStation"
    assert data["location"] == {"lat": 2.0, "long": 1.0}

    async with test_db.session() as session:
        result = await session.execute(select(models.WeatherStation))
        rows = result.scalars().all()
        assert len(rows) == 1


@pytest.mark.asyncio
async def test_add_weather_station_already_exists(client, seed_user, seed_station):
    user = await seed_user(username="alice", password="secret")
    await seed_station(user=user, longitude=1.0, latitude=2.0, api_key="k1")

    mutation = """
        mutation {
            addWeatherStation(weatherStation: {longitude: 1.0, latitude: 2.0, apiKey: "k2"}) {
                __typename
                ... on WeatherStationAlreadyExists {
                    message
                }
            }
        }
    """
    resp = await client.post("/graphql", json={"query": mutation}, headers={"Authorize": f"Bearer {user.username}"})
    payload = resp.json()
    assert "errors" not in payload
    data = payload["data"]["addWeatherStation"]
    assert data["__typename"] == "WeatherStationAlreadyExists"
    assert "already" in data["message"].lower()


@pytest.mark.asyncio
async def test_update_weather_station_not_found(client, seed_user):
    user = await seed_user(username="alice", password="secret")

    mutation = """
        mutation {
            updateWeatherStation(weatherStationUpdate: {stationId: 999, longitude: 9.9}) {
                resourceId
                message
                resourceUpdated
            }
        }
    """
    resp = await client.post("/graphql", json={"query": mutation}, headers={"Authorize": f"Bearer {user.username}"})
    payload = resp.json()
    assert "errors" not in payload
    out = payload["data"]["updateWeatherStation"]
    assert out["resourceId"] == 999
    assert out["resourceUpdated"] is False
    assert "not found" in out["message"].lower()


@pytest.mark.asyncio
async def test_update_weather_station_foreign_station_denied(client, seed_user, seed_station):
    owner = await seed_user(username="owner", password="secret")
    other = await seed_user(username="other", password="secret")
    st = await seed_station(user=owner, longitude=1.0, latitude=2.0, api_key="k1")

    mutation = f"""
        mutation {{
            updateWeatherStation(weatherStationUpdate: {{stationId: {st.station_id}, longitude: 9.9}}) {{
                resourceId
                message
                resourceUpdated
            }}
        }}
    """
    resp = await client.post("/graphql", json={"query": mutation}, headers={"Authorize": f"Bearer {other.username}"})
    payload = resp.json()
    assert "errors" not in payload
    out = payload["data"]["updateWeatherStation"]
    assert out["resourceId"] == st.station_id
    assert out["resourceUpdated"] is False
    assert "foreign" in out["message"].lower()


@pytest.mark.asyncio
async def test_update_weather_station_nothing_to_update(client, seed_user, seed_station):
    user = await seed_user(username="alice", password="secret")
    st = await seed_station(user=user, longitude=1.0, latitude=2.0, api_key="k1")

    mutation = f"""
        mutation {{
            updateWeatherStation(weatherStationUpdate: {{stationId: {st.station_id}}}) {{
                resourceId
                message
                resourceUpdated
            }}
        }}
    """
    resp = await client.post("/graphql", json={"query": mutation}, headers={"Authorize": f"Bearer {user.username}"})
    payload = resp.json()
    assert "errors" not in payload
    out = payload["data"]["updateWeatherStation"]
    assert out["resourceUpdated"] is False
    assert "nothing" in out["message"].lower()


@pytest.mark.asyncio
async def test_update_weather_station_success_updates_row(client, test_db, seed_user, seed_station):
    user = await seed_user(username="alice", password="secret")
    st = await seed_station(user=user, longitude=1.0, latitude=2.0, api_key="k1")

    mutation = f"""
        mutation {{
            updateWeatherStation(weatherStationUpdate: {{stationId: {st.station_id}, longitude: 3.3}}) {{
                resourceId
                message
                resourceUpdated
            }}
        }}
    """
    resp = await client.post("/graphql", json={"query": mutation}, headers={"Authorize": f"Bearer {user.username}"})
    payload = resp.json()
    assert "errors" not in payload
    out = payload["data"]["updateWeatherStation"]
    assert out["resourceUpdated"] is True

    async with test_db.session() as session:
        result = await session.execute(
            select(models.WeatherStation).where(models.WeatherStation.station_id == st.station_id)
        )
        updated = result.scalar_one()
        assert updated.longitude == 3.3


@pytest.mark.asyncio
async def test_remove_weather_station_not_found(client, seed_user):
    user = await seed_user(username="alice", password="secret")
    mutation = """
        mutation {
            removeWeatherStation(resourceId: 999) {
                resourceId
                message
                resourceRemoved
            }
        }
    """
    resp = await client.post("/graphql", json={"query": mutation}, headers={"Authorize": f"Bearer {user.username}"})
    payload = resp.json()
    assert "errors" not in payload
    out = payload["data"]["removeWeatherStation"]
    assert out["resourceId"] == 999
    assert out["resourceRemoved"] is False
    assert "not found" in out["message"].lower()


@pytest.mark.asyncio
async def test_remove_weather_station_foreign_station_denied(client, seed_user, seed_station):
    owner = await seed_user(username="owner", password="secret")
    other = await seed_user(username="other", password="secret")
    st = await seed_station(user=owner, longitude=1.0, latitude=2.0, api_key="k1")

    mutation = f"""
        mutation {{
            removeWeatherStation(resourceId: {st.station_id}) {{
                resourceId
                message
                resourceRemoved
            }}
        }}
    """
    resp = await client.post("/graphql", json={"query": mutation}, headers={"Authorize": f"Bearer {other.username}"})
    payload = resp.json()
    assert "errors" not in payload
    out = payload["data"]["removeWeatherStation"]
    assert out["resourceId"] == st.station_id
    assert out["resourceRemoved"] is False
    assert "foreign" in out["message"].lower()


@pytest.mark.asyncio
async def test_remove_weather_station_success_deletes_row(client, test_db, seed_user, seed_station):
    user = await seed_user(username="alice", password="secret")
    st = await seed_station(user=user, longitude=1.0, latitude=2.0, api_key="k1")

    mutation = f"""
        mutation {{
            removeWeatherStation(resourceId: {st.station_id}) {{
                resourceId
                message
                resourceRemoved
            }}
        }}
    """
    resp = await client.post("/graphql", json={"query": mutation}, headers={"Authorize": f"Bearer {user.username}"})
    payload = resp.json()
    assert "errors" not in payload
    out = payload["data"]["removeWeatherStation"]
    assert out["resourceRemoved"] is True

    async with test_db.session() as session:
        result = await session.execute(select(models.WeatherStation))
        assert result.scalars().all() == []

