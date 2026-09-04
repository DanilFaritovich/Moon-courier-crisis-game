from unittest.mock import Mock, patch

import pytest
from app.models.order import Order, OrderStatus, OrderUrgency
from app.repositories.order_connector_repository import OrderRepository
from app.services.order_service import OrderService


@pytest.fixture
def repository() -> Mock:
    return Mock(spec=OrderRepository)


@pytest.fixture
def service(repository: Mock) -> OrderService:
    return OrderService(repository)


class TestOrderServiceUnit:
    def test_create_order(
        self,
        service: OrderService,
        repository: Mock,
        order: Order,
    ) -> None:
        destination_point_id = order.destination_point_id
        weight = order.weight
        reward = order.reward
        urgency = order.urgency
        status = order.status

        repository.create_order.return_value = order

        result = service.create_order(
            destination_point_id=destination_point_id,
            weight=weight,
            reward=reward,
            urgency=urgency,
            status=status,
        )

        assert result is order

        repository.create_order.assert_called_once()
        created_order = repository.create_order.call_args.args[0]

        assert isinstance(created_order, Order)
        assert created_order.destination_point_id == destination_point_id
        assert created_order.weight == weight
        assert created_order.reward == reward
        assert created_order.urgency == urgency
        assert created_order.status == status

    def test_create_order_uses_default_values(
        self,
        service: OrderService,
        repository: Mock,
        order: Order,
    ) -> None:
        destination_point_id = order.destination_point_id
        weight = order.weight
        reward = order.reward

        repository.create_order.return_value = order

        result = service.create_order(
            destination_point_id=destination_point_id,
            weight=weight,
            reward=reward,
        )

        assert result is order

        repository.create_order.assert_called_once()
        created_order = repository.create_order.call_args.args[0]

        assert created_order.destination_point_id == destination_point_id
        assert created_order.weight == weight
        assert created_order.reward == reward
        assert created_order.urgency == OrderUrgency.MEDIUM
        assert created_order.status == OrderStatus.AVAILABLE

    def test_create_random_order(
        self,
        service: OrderService,
        repository: Mock,
        order: Order,
    ) -> None:
        points_ids = [10, 20, 30]
        destination_point_id = 20
        max_weight = 10
        weight = 7
        reward = 80
        urgency = OrderUrgency.HIGH

        repository.create_order.return_value = order

        with (
            patch(
                "app.services.order_service.choice",
                side_effect=[
                    destination_point_id,
                    urgency,
                ],
            ),
            patch(
                "app.services.order_service.randint",
                side_effect=[
                    weight,
                    reward,
                ],
            ),
        ):
            result = service.create_random_order(
                points_ids=points_ids,
                max_weight=max_weight,
            )

        assert result is order

        repository.create_order.assert_called_once()
        created_order = repository.create_order.call_args.args[0]

        assert created_order.destination_point_id == destination_point_id
        assert created_order.weight == weight
        assert created_order.reward == reward
        assert created_order.urgency == urgency
        assert created_order.status == OrderStatus.AVAILABLE

    def test_get_order(
        self,
        service: OrderService,
        repository: Mock,
        order: Order,
    ) -> None:
        order_id = order.id

        repository.get_order.return_value = order

        result = service.get_order(order_id)

        assert result is order
        repository.get_order.assert_called_once_with(order_id)

    def test_get_available_orders(
        self,
        service: OrderService,
        repository: Mock,
        orders: list[Order],
    ) -> None:
        repository.get_available_orders.return_value = orders

        result = service.get_available_orders()

        assert result == orders
        repository.get_available_orders.assert_called_once_with()

    def test_complete_order(
        self,
        service: OrderService,
        repository: Mock,
        order: Order,
    ) -> None:
        expected_status = OrderStatus.COMPLETED

        service.complete_order(order)

        assert order.status == expected_status
        repository.update_order.assert_called_once_with(order)

    def test_assign_order(
        self,
        service: OrderService,
        repository: Mock,
        order: Order,
    ) -> None:
        expected_status = OrderStatus.ASSIGNED

        service.assign_order(order)

        assert order.status == expected_status
        repository.update_order.assert_called_once_with(order)

    def test_unassign_order(
        self,
        service: OrderService,
        repository: Mock,
        order: Order,
    ) -> None:
        expected_status = OrderStatus.AVAILABLE

        service.unassign_order(order)

        assert order.status == expected_status
        repository.update_order.assert_called_once_with(order)
