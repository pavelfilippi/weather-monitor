from typing import Any, Optional, List

import strawberry
from sqlalchemy import select
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


schema = strawberry.Schema(query=Query)
