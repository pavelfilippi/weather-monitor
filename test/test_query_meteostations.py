import pytest
from src.main import schema
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from fastapi.testclient import TestClient
from src.dependencies.context import get_database
from src.main import app


SQLALCHEMY_DATABASE_URL = "sqlite://"
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
Base.metadata.create_all(bind=engine)


# app.dependency_overrides[get_database] = override_get_db



client = TestClient(app)


# @pytest.mark.asyncio
def test_query_zero_stations():
    """ Query returns empty result for empty db """
    query = """
        query TestQuery {
            meteostations {
                batteryPercentage
                location {
                    lat
                    long
                }
            }
        }
    """

    response = client.post(
        "/graphql/",
        json={"query": query},
    )

    # result = await schema.execute(query)
    assert response.json() == []



    # assert result.data["meteostations"] == []
