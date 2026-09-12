"""Seed the first delivery contracts for a new game."""

from app.models.order import Order, OrderStatus, OrderUrgency
from sqlalchemy import select
from sqlalchemy.orm import Session


class OrderSeeder:
    """Create deterministic, immediately feasible starter contracts once."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def seed(self) -> None:
        if self.session.scalar(select(Order.id).limit(1)) is not None:
            return

        self.session.add_all(
            [
                Order(
                    destination_point_id=2,
                    weight=3,
                    reward=60,
                    urgency=OrderUrgency.LOW,
                    status=OrderStatus.AVAILABLE,
                ),
                Order(
                    destination_point_id=3,
                    weight=2,
                    reward=90,
                    urgency=OrderUrgency.MEDIUM,
                    status=OrderStatus.AVAILABLE,
                ),
            ]
        )
        self.session.commit()
