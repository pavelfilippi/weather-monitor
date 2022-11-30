from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from src.rest_api.routes import router
from src.dependencies.context import AppContext
from src.schema import schema

app = FastAPI()

graphql_app = GraphQLRouter(schema, context_getter=AppContext)

app.include_router(graphql_app, prefix="/graphql")
app.include_router(router, prefix="")
