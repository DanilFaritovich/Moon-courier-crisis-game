from enum import Enum

from app.db.base import Base
from app.models.point import Point
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RoverStatus(str, Enum):
    """Current rover state."""

    IDLE = "idle"
    DELIVERING = "delivering"
    CHARGING = "charging"
    DISABLED = "disabled"


class Rover(Base):
    """Lunar rover used for supply deliveries."""

    __tablename__ = "rovers"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(nullable=False)

    # Maximum cargo capacity in kilograms.
    cargo_capacity: Mapped[int] = mapped_column(nullable=False, default=30)

    # Current cargo weight in kilograms.
    cargo: Mapped[int] = mapped_column(nullable=False, default=0)

    # Maximum battery capacity in percent.
    battery_capacity: Mapped[int] = mapped_column(nullable=False, default=100)

    # Current battery level in percent.
    battery: Mapped[int] = mapped_column(nullable=False, default=100)

    # Current location on the lunar map.
    current_point_id: Mapped[int] = mapped_column(
        ForeignKey("points.id"),
        nullable=False,
    )

    status: Mapped[RoverStatus] = mapped_column(
        SqlEnum(RoverStatus),
        default=RoverStatus.IDLE,
        nullable=False,
    )

    current_point: Mapped[Point] = relationship()
