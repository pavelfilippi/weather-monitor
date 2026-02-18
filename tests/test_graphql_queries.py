import datetime as dt

import pytest


@pytest.mark.asyncio
async def test_graphql_weather_stations_empty_returns_null_or_empty_list(client):
    query = """
        query {
            weatherStations {
                resourceId
            }
        }
    """
    resp = await client.post("/graphql", json={"query": query})
    assert resp.status_code == 200
    payload = resp.json()
    assert "errors" not in payload
    assert payload["data"]["weatherStations"] in (None, [])


@pytest.mark.asyncio
async def test_graphql_weather_stations_returns_stations(client, seed_station):
    st = await seed_station(longitude=10.5, latitude=20.5, api_key="k1")

    query = """
        query {
            weatherStations {
                resourceId
                location { lat long }
            }
        }
    """
    resp = await client.post("/graphql", json={"query": query})
    assert resp.status_code == 200
    payload = resp.json()
    assert "errors" not in payload
    stations = payload["data"]["weatherStations"]
    assert isinstance(stations, list)
    assert len(stations) == 1
    assert stations[0]["resourceId"] == st.station_id
    assert stations[0]["location"] == {"lat": 20.5, "long": 10.5}


@pytest.mark.asyncio
async def test_graphql_nested_weather_station_conditions(client, seed_station, seed_condition):
    st = await seed_station(api_key="k1")
    await seed_condition(station=st, time=dt.datetime(2026, 1, 1, 12, 0, 0), temperature=18.0)

    query = """
        query {
            weatherStations {
                resourceId
                weatherStationConditions {
                    time
                    temperature
                }
            }
        }
    """
    resp = await client.post("/graphql", json={"query": query})
    assert resp.status_code == 200
    payload = resp.json()
    assert "errors" not in payload
    stations = payload["data"]["weatherStations"]
    assert len(stations) == 1
    assert stations[0]["resourceId"] == st.station_id
    conditions = stations[0]["weatherStationConditions"]
    assert isinstance(conditions, list)
    assert len(conditions) == 1
    assert conditions[0]["temperature"] == 18.0


@pytest.mark.asyncio
async def test_graphql_weather_data_time_filter(client, seed_station, seed_condition):
    st = await seed_station(api_key="k1")
    t1 = dt.datetime(2026, 1, 1, 12, 0, 0)
    t2 = dt.datetime(2026, 1, 1, 13, 0, 0)
    await seed_condition(station=st, time=t1, temperature=10.0)
    await seed_condition(station=st, time=t2, temperature=11.0)

    query = """
        query($f: TimeFilter) {
            weatherData(timeFilter: $f) {
                time
                temperature
            }
        }
    """
    variables = {"f": {"timeFrom": t2.isoformat(), "timeTo": t2.isoformat()}}
    resp = await client.post("/graphql", json={"query": query, "variables": variables})
    assert resp.status_code == 200
    payload = resp.json()
    assert "errors" not in payload

    data = payload["data"]["weatherData"]
    assert data is not None
    assert len(data) == 1
    assert data[0]["temperature"] == 11.0


@pytest.mark.asyncio
async def test_graphql_permission_required_for_mutation(client):
    mutation = """
        mutation {
            addWeatherStation(weatherStation: {longitude: 1.0, latitude: 2.0, apiKey: "k"}) {
                __typename
            }
        }
    """
    resp = await client.post("/graphql", json={"query": mutation})
    assert resp.status_code == 200
    payload = resp.json()
    assert "errors" in payload
    assert any("not authenticated" in err.get("message", "").lower() for err in payload["errors"])

