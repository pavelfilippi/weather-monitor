from typing import Optional

from fastapi import Depends
from fastapi import Request
from fastapi import Header
from sqlalchemy import select

from src.models import WeatherStation
from src.dependencies.database import Database
from src.dependencies.database import get_database


async def get_auth_weather_station(
        request: Request,
        db: Database = Depends(get_database),
        Authorization: str | None = Header(default="Bearer <api_key>"),
) -> Optional[WeatherStation]:
    """ Get weather station based on request header API key """

    authorization = request.headers.get("Authorization", "")
    authorization_split = authorization.split(" ", 1)

    if len(authorization_split) != 2:
        return None  # unauthorized or invalid format

    auth_type, api_key = authorization_split
    if auth_type != "Bearer" or not api_key:
        return None  # invalid type or empty api_key

    async with db.session() as session:
        query = select(WeatherStation).where(WeatherStation.api_key == api_key)
        result = await session.execute(query)
        weather_station = result.scalar()

    return weather_station
