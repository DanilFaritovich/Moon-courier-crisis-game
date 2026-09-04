from app.models.order import Order, OrderStatus
from app.repositories.order_connector_repository import OrderRepository
from sqlalchemy import select
from sqlalchemy.orm import Session


class OrderConnector(OrderRepository):
    """SQLAlchemy implementation of the order_connector repository."""

    def __init__(self, db: Session):
        self.db = db

    def create_order(self, order: Order) -> Order:
        """Create and persist a new delivery order."""

        self.db.add(order)
        self.db.flush()

        return order

    def get_order(self, order_id: int) -> Order | None:
        return self.db.get(Order, order_id)

    def get_available_orders(self) -> list[Order]:
        return list(
            self.db.scalars(
                select(Order).where(Order.status == OrderStatus.AVAILABLE)
            ).all()
        )

    def update_order(self, order: Order) -> Order:
        """Update an existing delivery order."""

        self.db.flush()

        return order
