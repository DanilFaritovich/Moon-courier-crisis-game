from enum import Enum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.point import Point


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
    cargo_capacity: Mapped[float] = mapped_column(nullable=False)

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