import logging

from app.models.delivery import Delivery, DeliveryStatus
from app.repositories.delivery_connector_repository import DeliveryRepository
from sqlalchemy import select
from sqlalchemy.orm import Session


class DeliveryConnectorRepository(DeliveryRepository):
    """SQLAlchemy implementation of the delivery repository."""

    def __init__(self, db: Session, logger: logging.Logger | None = None):
        self.db = db
        self.logger = logger if logger is not None else logging.getLogger(__name__)

    def create_delivery(self, delivery: Delivery) -> Delivery:
        """Create and persist a delivery."""

        self.db.add(delivery)
        self.db.flush()

        return delivery

    def delete_delivery(self, delivery_id: int) -> None:
        """Delete a delivery."""

        delivery = self.db.get(Delivery, delivery_id)

        if delivery is None:
            return

        self.db.delete(delivery)
        self.db.flush()

    def get_delivery(
        self,
        delivery_id: int,
    ) -> Delivery | None:
        """Return a delivery by its identifier."""

        return self.db.get(Delivery, delivery_id)

    def get_deliveries_by_status(
        self,
        status: DeliveryStatus,
    ) -> list[Delivery]:
        """Return deliveries with the specified status."""

        return list(
            self.db.scalars(
                select(Delivery).where(
                    Delivery.status == status,
                )
            ).all()
        )

    def update_delivery(self, delivery: Delivery) -> Delivery:
        """Update and persist a delivery."""

        self.db.flush()

        return delivery
