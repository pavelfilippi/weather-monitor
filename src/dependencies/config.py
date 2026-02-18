from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DB_HOST: str = ""
    DB_PORT: str = ""
    DB_USER: str = ""
    DB_PASS: str = Field(default="", alias="POSTGRES_PASSWORD")
    DB_NAME: str = Field(default="", alias="POSTGRES_DB")


@lru_cache()
def get_config() -> Config:
    """Cached configuration factory

    https://fastapi.tiangolo.com/advanced/settings/#lru_cache-technical-details
    """
    return Config()
