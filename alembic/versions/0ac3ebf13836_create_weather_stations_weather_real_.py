"""create weather_stations & weather_real_time tables

Revision ID: 0ac3ebf13836
Revises: 
Create Date: 2022-11-23 20:31:33.572659

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0ac3ebf13836"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "weather_stations",
        sa.Column("station_id", sa.Integer, nullable=False, primary_key=True),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column("latitude", sa.Float, nullable=False),
    )

    op.create_table(
        "weather_real_time",
        sa.Column("time", sa.TIMESTAMP, primary_key=True, nullable=False),
        sa.Column("station_id", sa.Integer, sa.ForeignKey("weather_stations.station_id"), nullable=False),
        sa.Column("battery_percentage", sa.Float, nullable=True),
        sa.Column("temperature", sa.Float, nullable=True),
        sa.Column("humidity", sa.Float, nullable=True),
        sa.Column("pressure", sa.Float, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("weather_stations")
    op.drop_table("weather_real_time")
