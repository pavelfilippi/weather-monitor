from sqlalchemy import UniqueConstraint, Column, Integer, Float, TIMESTAMP
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

Base = declarative_base()


class WeatherStation(Base):
    __tablename__ = "weather_stations"
    __table_args__ = (UniqueConstraint("longitude", "latitude", name="location"),)

    station_id = Column(Integer, nullable=False, primary_key=True)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)

    weather_real_time = relationship("StationCondition", back_populates="weather_station_rel")


class StationCondition(Base):
    __tablename__ = "weather_real_time"

    time = Column(TIMESTAMP, primary_key=True, nullable=False)
    # Should have public. ?
    station_id = Column(Integer, ForeignKey("weather_stations.station_id"), nullable=False)

    weather_station_rel = relationship("WeatherStation", back_populates="weather_real_time")

    battery_percentage = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
