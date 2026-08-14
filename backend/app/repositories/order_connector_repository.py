from abc import ABC, abstractmethod

from app.models.order import Order


class OrderRepository(ABC):
    """"Abstract repository for order data."""

    @abstractmethod
    def create_order(self, order: Order) -> Order:
        """Return all grpah points."""
        ...

    @abstractmethod
    def get_order(self, order_id: int) -> Order | None:
        """Return an order by its identifier."""
        ...

    @abstractmethod
    def get_available_orders(self) -> list[Order]:
        """Return all orders available for delivery."""
        ...

    @abstractmethod
    def complete_order(self, order: Order) -> None:
        """Mark an order as completed."""
        ...

    @abstractmethod
    def fail_order(self, order: Order) -> None:
        """Mark an order as failed."""
        ...