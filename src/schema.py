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
class Meteostation:
    battery_percentage: int
    location: Location

    @staticmethod
    def from_model(model: models.Meteostation) -> "Meteostation":
        return Meteostation(
            battery_percentage=model.battery_percentage, location=Location(lat=model.latitude, long=model.longitude)
        )


@strawberry.type
class Query:
    @strawberry.field(description="Gets data for all meteostations.")
    async def meteostations(self, info: Info[AppContext, Any]) -> Optional[List[Meteostation]]:
        """Load information for all meteostations present in database."""
        async with info.context.db.session() as session:
            query = select(models.Meteostation)

            result = await session.execute(query)
            meteostations = result.scalars()

        if not meteostations:
            return None

        return [Meteostation.from_model(station) for station in meteostations]


@strawberry.type
class MeteostationAlreadyExists:
    message: str = "Meteostation already stored in database."


NewMeteostationOutput = strawberry.union("NewMeteostationOutput", (Meteostation, MeteostationAlreadyExists))


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Store new meteostation.")
    async def add_meteostation(
            self,
            info: Info[AppContext, Any],
            longitude: float,
            latitude: float,
            battery_status: int=100
    ) -> NewMeteostationOutput:
        """ Store new meteostation into DB """
        async with info.context.db.session() as session:
            # Meteostation already exists in db validation
            query = select(
                exists(
                    select(1)
                    .select_from(models.Meteostation)
                    .where(and_(models.Meteostation.longitude == longitude, models.Meteostation.latitude == latitude))
                )
            )
            result = await session.execute(query)
            meteostation_exists = result.scalar()
            if meteostation_exists:
                return MeteostationAlreadyExists

            meteostation = models.Meteostation(battery_percentage=battery_status, longitude=longitude, latitude=latitude)
            session.add(meteostation)

        return Meteostation.from_model(meteostation)


    @strawberry.mutation(description="Remove meteostation.")
    async def remove_meteostation(
            self, info: Info[AppContext, Any], longitude: float, latitude: float
    ) -> None:
        """Delete meteostation from DB"""
        async with info.context.db.session() as session:
            query = select(
                exists(
                    select(1)
                    .select_from(models.Meteostation)
                    .where(and_(models.Meteostation.longitude == longitude, models.Meteostation.latitude == latitude))
                )
            )
            result = await session.execute(query)
            meteostation_exists = result.scalar()
            if meteostation_exists:
                query = select(models.Meteostation).where(and_(models.Meteostation.longitude == longitude, models.Meteostation.latitude == latitude))

                result = await session.execute(query)
                meteostation = result.scalar()

                await session.delete(meteostation)


schema = strawberry.Schema(query=Query, mutation=Mutation)
