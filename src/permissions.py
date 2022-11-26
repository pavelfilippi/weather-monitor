
import typing

from sqlalchemy import select
from strawberry.permission import BasePermission
from strawberry.types import Info

from src.dependencies.context import AppContext
from src.models import MonitorUser


# TODO: How to get value from?
class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    async def has_permission(self, source: typing.Any, info: Info[AppContext, typing.Any], **kwargs) -> bool:

        authorization = info.context.request.headers.get("Authorize", "")
        authorization_split = authorization.split(" ", 1)

        if len(authorization_split) != 2:
            return False  # unauthorized or invalid format

        auth_type, token = authorization_split
        if auth_type != "Bearer" or not token:
            return False  # invalid type or empty api_key

        async with info.context.db.session() as session:
            query = select(MonitorUser).where(MonitorUser.username == token)
            result = await session.execute(query)
            user = result.scalar()

        if user:
            return user





# {
#   "Authorize": "Bearer <username>"
# }

