from enum import Enum
from typing import TYPE_CHECKING

from app.db.base import Base
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.road import Road


class PointType(str, Enum):
    """Types of points available on the lunar map."""

    BASE = "base"
    DELIVERY = "delivery"
    ROUTE = "route"


class Point(Base):
    __tablename__ = "points"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        nullable=False,
    )

    type: Mapped[PointType] = mapped_column(
        SQLEnum(PointType),
        nullable=False,
    )

    # Coordinates are used by the frontend to render the map.
    x: Mapped[float] = mapped_column(nullable=False)
    y: Mapped[float] = mapped_column(nullable=False)

    # Roads starting from this point.
    outgoing_roads: Mapped[list["Road"]] = relationship(
        "Road",
        foreign_keys="Road.from_point_id",
        back_populates="from_point",
    )

    # Roads ending at this point.
    incoming_roads: Mapped[list["Road"]] = relationship(
        "Road",
        foreign_keys="Road.to_point_id",
        back_populates="to_point",
    )
