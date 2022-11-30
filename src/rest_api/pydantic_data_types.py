import datetime
from typing import Optional

from pydantic import BaseModel


class UserInDB(BaseModel):
    username: str
    password: str


class StationCondition(BaseModel):
    time: datetime.datetime
    battery_percentage: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
