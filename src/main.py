from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from src.dependencies.context import AppContext
from src.schema import schema
from src import weather_conditions
from src import user_management

app = FastAPI()


graphql_app = GraphQLRouter(schema, context_getter=AppContext)
app.include_router(graphql_app, prefix="/graphql")
app.include_router(weather_conditions.router, prefix="")
app.include_router(user_management.router, prefix="")
