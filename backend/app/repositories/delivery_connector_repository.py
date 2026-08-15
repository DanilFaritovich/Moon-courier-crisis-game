from abc import ABC, abstractmethod

from app.models.delivery import Delivery, DeliveryStatus


class DeliveryRepository(ABC):
    """Repository interface for delivery data."""

    @abstractmethod
    def create_delivery(self, delivery: Delivery) -> Delivery:
        """Create and persist a delivery."""
        ...

    @abstractmethod
    def get_delivery(self, delivery_id: int) -> Delivery | None:
        """Return a delivery by its identifier."""
        ...

    @abstractmethod
    def get_deliveries_by_status(
        self,
        status: DeliveryStatus,
    ) -> list[Delivery]:
        """Return deliveries with the specified status."""
        ...

    @abstractmethod
    def update_delivery(self, delivery: Delivery) -> Delivery:
        """Update and persist a delivery."""
        ...