from typing import Any, Optional, List

import strawberry
from sqlalchemy import select, exists, and_
from strawberry.types import Info

from src import models
from src.dependencies.context import AppContext


@strawberry.type
class Location:
    long: float
    lat: float


@strawberry.type
class WeatherStation:
    resource_id: int
    battery_percentage: int
    location: Location

    @staticmethod
    def from_model(model: models.WeatherStation) -> "WeatherStation":
        return WeatherStation(
            resource_id=model.station_id,
            battery_percentage=model.battery_percentage,
            location=Location(lat=model.latitude, long=model.longitude),
        )


@strawberry.type
class Query:
    @strawberry.field(description="Gets data for all weather stations.")
    async def weather_stations(self, info: Info[AppContext, Any]) -> Optional[List[WeatherStation]]:
        """Load information for all weather stations present in database."""
        async with info.context.db.session() as session:
            query = select(models.WeatherStation)

            result = await session.execute(query)
            weather_stations = result.scalars()

        if not weather_stations:
            return None

        return [WeatherStation.from_model(station) for station in weather_stations]


@strawberry.type
class WeatherStationAlreadyExists:
    message: str = "Weather station already stored in database."


NewWeatherStationOutput = strawberry.union("NewWeatherStationOutput", (WeatherStation, WeatherStationAlreadyExists))


@strawberry.type
class RemoveWeatherStationOutput:
    resource_id: int
    message: str
    resource_removed: bool


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Store new weather station.")
    async def add_weather_station(
        self, info: Info[AppContext, Any], longitude: float, latitude: float, battery_status: int = 100
    ) -> NewWeatherStationOutput:
        """Store new weather station into DB"""
        async with info.context.db.session() as session:
            # Weather station already exists in db validation
            query = select(
                exists(
                    select(1)
                    .select_from(models.WeatherStation)
                    .where(
                        and_(models.WeatherStation.longitude == longitude, models.WeatherStation.latitude == latitude)
                    )
                )
            )
            result = await session.execute(query)
            weather_station = result.scalar()
            if weather_station:
                return WeatherStationAlreadyExists

            weather_station = models.WeatherStation(
                battery_percentage=battery_status, longitude=longitude, latitude=latitude
            )
            session.add(weather_station)

        return WeatherStation.from_model(weather_station)

    @strawberry.mutation(description="Remove weather station.")
    async def remove_weather_station(self, info: Info[AppContext, Any], resource_id: int) -> RemoveWeatherStationOutput:
        """Delete weather station from DB"""
        async with info.context.db.session() as session:
            query = select(
                exists(
                    select(1).select_from(models.WeatherStation).where(models.WeatherStation.station_id == resource_id)
                )
            )
            result = await session.execute(query)
            weather_station_exists = result.scalar()
            if weather_station_exists:
                query = select(models.WeatherStation).where(models.WeatherStation.station_id == resource_id)

                result = await session.execute(query)
                weather_station = result.scalar()

                await session.delete(weather_station)
                return RemoveWeatherStationOutput(
                    resource_id=resource_id, resource_removed=True, message="Weather station successfully removed."
                )
            return RemoveWeatherStationOutput(
                resource_id=resource_id, resource_removed=False, message="Weather station not found."
            )


schema = strawberry.Schema(query=Query, mutation=Mutation)
