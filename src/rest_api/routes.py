from typing import Optional

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from dependencies.database import get_database, Database
from src import models
from src.dependencies.auth import get_auth_weather_station
from src.models import MonitorUser
from src.models import WeatherStation
from src.rest_api.pydantic_data_types import UserInDB, StationCondition

router = APIRouter()


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Database = Depends(get_database),
):
    async with db.session() as session:
        query = select(MonitorUser).where(MonitorUser.username == form_data.username)
        result = await session.execute(query)
        user = result.scalar()

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(username=user.username, password=user.password)
    if not form_data.password == user.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


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
