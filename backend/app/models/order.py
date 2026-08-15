from enum import Enum

from app.db.base import Base
from app.models.point import Point
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OrderStatus(str, Enum):
    """Current state of a delivery order."""

    AVAILABLE = "available"
    ASSIGNED = "assigned"
    COMPLETED = "completed"


class OrderUrgency(str, Enum):
    """Priority level of an order."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Order(Base):
    """Delivery order for transporting food supplies."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Destination point where the supplies must be delivered.
    destination_point_id: Mapped[int] = mapped_column(
        ForeignKey("points.id"),
        nullable=False,
    )

    # Cargo weight in kilograms.
    weight: Mapped[float] = mapped_column(nullable=False)

    # Credits earned after a successful delivery.
    reward: Mapped[int] = mapped_column(nullable=False)

    # Delivery priority.
    urgency: Mapped[OrderUrgency] = mapped_column(
        SqlEnum(OrderUrgency),
        default=OrderUrgency.MEDIUM,
        nullable=False,
    )

    # Current order status.
    status: Mapped[OrderStatus] = mapped_column(
        SqlEnum(OrderStatus),
        default=OrderStatus.AVAILABLE,
        nullable=False,
    )

    destination: Mapped["Point"] = relationship()