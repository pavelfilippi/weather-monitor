import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Config(BaseSettings):
    DB_HOST: Optional[str] = os.getenv("DB_HOST")
    DB_PORT: Optional[str] = os.getenv("DB_PORT")
    DB_USER: Optional[str] = os.getenv("DB_USER")
    DB_PASS: Optional[str] = os.getenv("POSTGRES_PASSWORD")
    DB_NAME: Optional[str] = os.getenv("POSTGRES_DB")


@lru_cache()
def get_config() -> Config:
    """Cached configuration factory

    https://fastapi.tiangolo.com/advanced/settings/#lru_cache-technical-details
    """
    return Config()
