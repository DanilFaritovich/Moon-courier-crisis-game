from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.point import Point


class Road(Base):
    __tablename__ = "roads"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Start and end points of the road.
    from_point_id: Mapped[int] = mapped_column(
        ForeignKey("points.id"),
        nullable=False,
    )

    to_point_id: Mapped[int] = mapped_column(
        ForeignKey("points.id"),
        nullable=False,
    )

    # Physical length of the road in kilometers.
    distance: Mapped[float] = mapped_column(
        nullable=False,
    )

    # Probability of encountering a dangerous event on this road.
    # Expected range: 0.0 - 1.0.
    risk: Mapped[float] = mapped_column(
        nullable=False,
    )

    # Multiplier affecting rover speed on this road.
    # 1.0 means normal speed, values below 1.0 represent slower terrain.
    speed_modifier: Mapped[float] = mapped_column(
        nullable=False,
        default=1.0,
    )

    from_point: Mapped["Point"] = relationship(
        "Point",
        foreign_keys=[from_point_id],
        back_populates="outgoing_roads",
    )

    to_point: Mapped["Point"] = relationship(
        "Point",
        foreign_keys=[to_point_id],
        back_populates="incoming_roads",
    )