from app.models.delivery import Delivery, DeliveryStatus
from app.repositories.delivery_connector_repository import DeliveryRepository


class DeliveryService:
    """Manage order deliveries."""

    def __init__(self, repository: DeliveryRepository):
        """Initialize the delivery service."""

        self.repository = repository

    def create_delivery(
        self,
        order_id: int,
        rover_id: int,
    ) -> Delivery:
        """Create a new delivery."""

        delivery = Delivery(
            order_id=order_id,
            rover_id=rover_id,
        )

        return self.repository.create_delivery(delivery)

    def get_delivery(
        self,
        delivery_id: int,
    ) -> Delivery | None:
        """Return a delivery by its identifier."""

        return self.repository.get_delivery(delivery_id)

    def get_active_deliveries(self) -> list[Delivery]:
        """Return all deliveries currently in progress."""

        return self.repository.get_deliveries_by_status(
            DeliveryStatus.IN_PROGRESS,
        )

    def complete_delivery(self, delivery: Delivery) -> None:
        """Mark a delivery as completed."""

        delivery.status = DeliveryStatus.COMPLETED
        self.repository.update_delivery(delivery)

    def fail_delivery(self, delivery: Delivery) -> None:
        """Mark a delivery as failed."""

        delivery.status = DeliveryStatus.FAILED
        self.repository.update_delivery(delivery)