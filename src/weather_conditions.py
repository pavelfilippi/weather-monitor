import datetime
from typing import Optional

from fastapi import Depends, Header, HTTPException, APIRouter
from pydantic import BaseModel

from dependencies.auth import get_auth_weather_station
from dependencies.database import get_database, Database
from models import WeatherStation
from src import models

router = APIRouter()


class StationCondition(BaseModel):
    time: datetime.datetime
    battery_percentage: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None


@router.post(path="/conditions")
async def insert_weather_conditions_data(
    station_condition: StationCondition,
    db: Database = Depends(get_database),
    auth_station: Optional[WeatherStation] = Depends(get_auth_weather_station),
) -> None:
    if not auth_station:
        raise HTTPException(status_code=401, detail="Unauthorized access - request denied.")

    async with db.session() as session:
        new_condition = models.StationCondition(
            time=station_condition.time,
            station_id=auth_station.station_id,
            battery_percentage=station_condition.battery_percentage,
            temperature=station_condition.temperature,
            humidity=station_condition.humidity,
            pressure=station_condition.pressure,
        )
        session.add(new_condition)
