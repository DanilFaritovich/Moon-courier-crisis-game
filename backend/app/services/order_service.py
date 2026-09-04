from random import choice, randint

from app.models.order import Order, OrderStatus, OrderUrgency
from app.repositories.order_connector_repository import OrderRepository


class OrderService:
    """Manage delivery orders."""

    def __init__(self, repository: OrderRepository):
        """Initialize the service with a database session."""
        self.repository = repository

    def create_order(
        self,
        destination_point_id: int,
        weight: int,
        reward: int,
        urgency: OrderUrgency = OrderUrgency.MEDIUM,
        status: OrderStatus = OrderStatus.AVAILABLE,
    ) -> Order:
        """Create and persist a new delivery order."""

        order = Order(
            destination_point_id=destination_point_id,
            weight=weight,
            reward=reward,
            urgency=urgency,
            status=status,
        )

        return self.repository.create_order(order)

    def create_random_order(self, points_ids: list[int], max_weight: int) -> Order:
        destination_point_id = choice(points_ids)
        order = Order(
            destination_point_id=destination_point_id,
            weight=randint(1, max_weight),
            reward=randint(40, 100),
            urgency=choice(list(OrderUrgency)),
            status=OrderStatus.AVAILABLE,
        )
        return self.repository.create_order(order)

    def get_order(self, order_id: int) -> Order | None:
        """Return an order by its identifier."""

        return self.repository.get_order(order_id)

    def get_available_orders(self) -> list[Order]:
        """Return all orders available for delivery."""

        return self.repository.get_available_orders()

    def complete_order(self, order: Order) -> None:
        order.status = OrderStatus.COMPLETED
        self.repository.update_order(order)

    def assign_order(self, order: Order) -> None:
        order.status = OrderStatus.ASSIGNED
        self.repository.update_order(order)

    def unassign_order(self, order: Order) -> None:
        order.status = OrderStatus.AVAILABLE
        self.repository.update_order(order)
