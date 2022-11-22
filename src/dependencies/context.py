from fastapi import Depends
from strawberry.fastapi import BaseContext

from src.dependencies.config import Config
from src.dependencies.config import get_config
from src.dependencies.database import Database
from src.dependencies.database import get_database
from src.models import WeatherStation
from typing import Optional
from src.dependencies.auth import get_auth_weather_station


class AppContext(BaseContext):
    """Custom typed context class

    https://strawberry.rocks/docs/integrations/fastapi#context_getter
    """

    def __init__(
        self,
        config: Config = Depends(get_config),
        db: Database = Depends(get_database),
        auth_weather_station: Optional[WeatherStation] = Depends(get_auth_weather_station),
    ):
        super().__init__()
        self.config = config
        self.db = db
        self.auth_weather_station = auth_weather_station
