from pydantic import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()


class Config(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("POSTGRES_PASSWORD")
    DB_NAME: str = os.getenv("POSTGRES_DB")


@lru_cache()
def get_config():
    """Cached configuration factory

    https://fastapi.tiangolo.com/advanced/settings/#lru_cache-technical-details
    """
    return Config()
