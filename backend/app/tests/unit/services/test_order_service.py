from unittest.mock import Mock

from app.models.order import Order, OrderStatus, OrderUrgency
from app.services.order_service import OrderService


class TestOrderService:

    def test_create_order(self, order_repository):
        """Create an order and pass it to the repository."""

        order_repository.create_order.side_effect = lambda order: order

        service = OrderService(order_repository)

        order = service.create_order(
            destination_point_id=10,
            weight=25.0,
            reward=100,
            urgency=OrderUrgency.HIGH,
            status=OrderStatus.AVAILABLE
        )

        assert isinstance(order, Order)
        assert order.destination_point_id == 10
        assert order.weight == 25.0
        assert order.reward == 100
        assert order.urgency == OrderUrgency.HIGH
        assert order.status == OrderStatus.AVAILABLE

        order_repository.create_order.assert_called_once_with(order)

    def test_create_order_with_default_urgency(self, order_repository):
        """Create an order with medium urgency by default."""

        order_repository.create_order.side_effect = lambda order: order

        service = OrderService(order_repository)

        order = service.create_order(
            destination_point_id=10,
            weight=25.0,
            reward=100,
        )

        assert order.urgency == OrderUrgency.MEDIUM
        assert order.status == OrderStatus.AVAILABLE

        order_repository.create_order.assert_called_once_with(order)

    def test_get_order(self, order_repository):
        """Return an order by its identifier."""

        order = Order(
            id=1,
            destination_point_id=10,
            weight=25.0,
            reward=100,
            urgency=OrderUrgency.MEDIUM,
            status=OrderStatus.AVAILABLE,
        )

        order_repository.get_order.return_value = order

        service = OrderService(order_repository)

        result = service.get_order(1)

        assert result is order
        order_repository.get_order.assert_called_once_with(1)

    def test_get_order_not_found(self, order_repository):
        """Return None when the order does not exist."""

        order_repository.get_order.return_value = None

        service = OrderService(order_repository)

        result = service.get_order(999)

        assert result is None
        order_repository.get_order.assert_called_once_with(999)

    def test_get_available_orders(self, order_repository):
        """Return orders available for delivery."""

        orders = [
            Order(
                id=1,
                destination_point_id=10,
                weight=10.0,
                reward=100,
                urgency=OrderUrgency.LOW,
                status=OrderStatus.AVAILABLE,
            ),
            Order(
                id=2,
                destination_point_id=20,
                weight=20.0,
                reward=200,
                urgency=OrderUrgency.HIGH,
                status=OrderStatus.AVAILABLE,
            ),
        ]

        order_repository.get_available_orders.return_value = orders

        service = OrderService(order_repository)

        result = service.get_available_orders()

        assert result == orders
        assert len(result) == 2

        order_repository.get_available_orders.assert_called_once()

    def test_complete_order(self, order_repository):
        """Complete an order through the repository."""

        order = Order(
            id=1,
            destination_point_id=10,
            weight=25.0,
            reward=100,
            status=OrderStatus.IN_PROGRESS,
        )

        service = OrderService(order_repository)

        service.complete_order(order)

        order_repository.complete_order.assert_called_once_with(order)

    def test_fail_order(self, order_repository):
        """Fail an order through the repository."""

        order = Order(
            id=1,
            destination_point_id=10,
            weight=25.0,
            reward=100,
            status=OrderStatus.IN_PROGRESS,
        )

        service = OrderService(order_repository)

        service.fail_order(order)

        order_repository.fail_order.assert_called_once_with(order)