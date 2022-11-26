from sqlalchemy import UniqueConstraint, Column, Integer, Float, TIMESTAMP, Text, event, DDL, Index, String
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
    api_key = Column(Text, nullable=False)

    weather_real_time = relationship("StationCondition", back_populates="weather_station_rel", cascade="all, delete")
    monitor_user_rel = relationship("MonitorUser", back_populates="weather_station")
    user_id = Column(Integer, ForeignKey("monitor_user.id"), nullable=False)

class StationCondition(Base):
    __tablename__ = "weather_real_time"

    time = Column(TIMESTAMP, primary_key=True, nullable=False)
    station_id = Column(Integer, ForeignKey("weather_stations.station_id"), nullable=False)

    weather_station_rel = relationship("WeatherStation", back_populates="weather_real_time")

    battery_percentage = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)


class MonitorUser(Base):
    __tablename__ = "monitor_user"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(128), nullable=False)

    weather_station = relationship("WeatherStation", back_populates="monitor_user_rel", cascade="all, delete")


Index("ix_station_id_time", StationCondition.station_id, StationCondition.time, unique=False)
Index("weather_real_time_time_idx", StationCondition.time, unique=False)
