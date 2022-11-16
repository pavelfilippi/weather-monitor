from pydantic import BaseSettings
from functools import lru_cache
import os


class Config(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")
    DB_NAME: str = os.getenv("DB_NAME")


@lru_cache()
def get_config():
    """Cached configuration factory

    https://fastapi.tiangolo.com/advanced/settings/#lru_cache-technical-details
    """
    return Config()
