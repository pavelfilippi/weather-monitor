import datetime
from typing import Any, Optional, List

import strawberry
from sqlalchemy import select, exists, and_, update
from strawberry.types import Info

from src import models
from src.dependencies.context import AppContext
from src.permissions import IsAuthenticated


@strawberry.type
class Location:
    long: float
    lat: float


@strawberry.type
class WeatherStation:
    resource_id: int
    location: Location

    @staticmethod
    def from_model(model: models.WeatherStation) -> "WeatherStation":
        return WeatherStation(
            resource_id=model.station_id,
            location=Location(lat=model.latitude, long=model.longitude),
        )

    @strawberry.field
    async def weather_station_conditions(
        self,
        info: Info[AppContext, Any],
    ) -> List["StationCondition"]:
        async with info.context.db.session() as session:
            query = select(models.StationCondition).where(models.StationCondition.station_id == self.resource_id)
            result = await session.execute(query)
            station_conditions = result.scalars()

        return [StationCondition.from_model(condition) for condition in station_conditions]


@strawberry.type
class StationCondition:
    time: datetime.datetime
    resource_id: int
    battery_percentage: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None

    @staticmethod
    def from_model(station_condition: models.StationCondition) -> "StationCondition":
        return StationCondition(
            time=station_condition.time,
            resource_id=station_condition.station_id,
            battery_percentage=station_condition.battery_percentage,
            temperature=station_condition.temperature,
            humidity=station_condition.humidity,
            pressure=station_condition.pressure,
        )


@strawberry.input(description="Lets users filter based on time (from/to included)")
class TimeFilter:
    """Filtering time from/to (included)"""
    time_from: Optional[datetime.datetime] = None
    time_to: Optional[datetime.datetime] = None


@strawberry.type
class WeatherStationAlreadyExists:
    message: str = "Weather station already stored in database."


NewWeatherStationOutput = strawberry.union("NewWeatherStationOutput", (WeatherStation, WeatherStationAlreadyExists))


@strawberry.type
class RemoveWeatherStationOutput:
    resource_id: int
    message: str
    resource_removed: bool


@strawberry.input
class WeeatherStationInput:
    longitude: float
    latitude: float
    api_key: str


@strawberry.input
class StationUpdate:
    station_id: int
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    api_key: Optional[str] = None

    def as_dict(self):
        original = dict(longitude=self.longitude, latitude=self.latitude, api_key=self.api_key)
        return {k: v for k, v in original.items() if v is not None}


@strawberry.type
class UpdateStationOutput:
    resource_id: int
    message: str
    resource_updated: bool


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

    @strawberry.field(description="Get weather data.")
    async def weather_data(
        self, info: Info[AppContext, Any], time_filter: Optional[TimeFilter] = None
    ) -> Optional[List[StationCondition]]:
        """Load all weather data"""
        async with info.context.db.session() as session:
            query = select(models.StationCondition)

            # Filter based on time from/to
            # Check time_filter to avoid  "'NoneType' object has no attribute 'time_to'", error
            if time_filter and time_filter.time_to:
                query = query.filter(models.StationCondition.time <= time_filter.time_to)
            if time_filter and time_filter.time_from:
                query = query.filter(models.StationCondition.time >= time_filter.time_from)

            result = await session.execute(query)
            weather_conditions = result.scalars()

        if not weather_conditions:
            return None

        return [StationCondition.from_model(condition) for condition in weather_conditions]


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Store new weather station.", permission_classes=[IsAuthenticated])
    async def add_weather_station(
        self, info: Info[AppContext, Any], weather_station: WeeatherStationInput
    ) -> NewWeatherStationOutput:
        """Store new weather station into DB"""
        async with info.context.db.session() as session:
            # Weather station already exists in db validation
            query = select(
                exists(
                    select(1)
                    .select_from(models.WeatherStation)
                    .where(
                        and_(
                            models.WeatherStation.longitude == weather_station.longitude,
                            models.WeatherStation.latitude == weather_station.latitude,
                        )
                    )
                )
            )


            result = await session.execute(query)
            existing_weather_station = result.scalar()
            if existing_weather_station:
                return WeatherStationAlreadyExists

            auth_user = info.context.request.auth_user  # Set in permission

            new_weather_station = models.WeatherStation(
                longitude=weather_station.longitude, latitude=weather_station.latitude, api_key=weather_station.api_key, user_id=auth_user.id
            )
            session.add(new_weather_station)

        return WeatherStation.from_model(new_weather_station)

    @strawberry.mutation(description="Remove weather station.", permission_classes=[IsAuthenticated])
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
                auth_user = info.context.request.auth_user
                query = select(models.WeatherStation).where(models.WeatherStation.station_id == resource_id)

                result = await session.execute(query)
                weather_station = result.scalar()

                # Check if deleting own station
                if weather_station.user_id != auth_user.id:
                    return RemoveWeatherStationOutput(
                        resource_id=weather_station.station_id,
                        message="Cannot remove foreign weather station!",
                        resource_removed=False,
                    )

                await session.delete(weather_station)
                return RemoveWeatherStationOutput(
                    resource_id=resource_id, resource_removed=True, message="Weather station successfully removed."
                )
            return RemoveWeatherStationOutput(
                resource_id=resource_id, resource_removed=False, message="Weather station not found."
            )

    @strawberry.mutation(description="Update weather station", permission_classes=[IsAuthenticated])
    async def update_weather_station(
        self, info: Info[AppContext, Any], weather_station_update: StationUpdate
    ) -> UpdateStationOutput:
        """Update weather station"""
        async with info.context.db.session() as session:
            query = select(
                exists(
                    select(1)
                    .select_from(models.WeatherStation)
                    .where(models.WeatherStation.station_id == weather_station_update.station_id)
                )
            )
            result = await session.execute(query)
            weather_station_exists = result.scalar()
            if weather_station_exists:
                query = select(models.WeatherStation).where(models.WeatherStation.station_id == weather_station_update.station_id)
                result = await session.execute(query)
                weather_station = result.scalar()

                auth_user = info.context.request.auth_user
                if weather_station.user_id != auth_user.id:
                    return UpdateStationOutput(
                        resource_id=weather_station.station_id,
                        message="Cannot update foreign weather station!",
                        resource_updated=False,
                    )
                if not weather_station_update.as_dict():
                    return UpdateStationOutput(
                        resource_id=weather_station.station_id,
                        message="Nothing to update",
                        resource_updated=False,
                    )
                query = (
                    update(models.WeatherStation)
                    .where(models.WeatherStation.station_id == weather_station.station_id)
                    .values(**weather_station_update.as_dict())
                )
                await session.execute(query)
                return UpdateStationOutput(
                    resource_id=weather_station.station_id,
                    message="Station successfully udpated.",
                    resource_updated=True,
                )
            return UpdateStationOutput(
                resource_id=weather_station_update.station_id,
                message="Station not found.",
                resource_updated=False,
            )


schema = strawberry.Schema(query=Query, mutation=Mutation)
