from sqlalchemy import UniqueConstraint, Column, Integer, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Meteostation(Base):
    __tablename__ = "meteostations"

    id = Column(Integer, nullable=False, primary_key=True)
    battery_percentage = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint("longitude", "latitude", name="location"),)
