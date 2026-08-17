from enum import Enum

from app.db.base import Base
from app.models.order import Order
from app.models.rover import Rover
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class DeliveryStatus(str, Enum):
    """Current state of a delivery."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Delivery(Base):
    """Execution of an order by a rover."""

    __tablename__ = "deliveries"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
        unique=True,
    )

    rover_id: Mapped[int] = mapped_column(
        ForeignKey("rovers.id"),
        nullable=False,
    )

    status: Mapped[DeliveryStatus] = mapped_column(
        SqlEnum(DeliveryStatus),
        default=DeliveryStatus.IN_PROGRESS,
        nullable=False,
    )

    started_turn: Mapped[int] = mapped_column(
        nullable=False,
    )

    completed_turn: Mapped[int] = mapped_column(
        nullable=True,
    )

    order: Mapped[Order] = relationship()

    rover: Mapped[Rover] = relationship()