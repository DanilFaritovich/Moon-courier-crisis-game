from unittest.mock import patch

import pytest
from app.models.order import Order, OrderStatus, OrderUrgency
from app.models.point import Point
from app.repositories.order_connector_repository import OrderRepository
from app.services.connector.order_connector_service import OrderConnector
from app.services.order_service import OrderService


@pytest.fixture
def repository(db_session) -> OrderRepository:
    return OrderConnector(db_session)


@pytest.fixture
def service(repository: OrderRepository) -> OrderService:
    return OrderService(repository)


@pytest.fixture
def db_points(
    db_session,
    points: list[Point],
) -> list[Point]:
    db_session.add_all(points)
    db_session.flush()
    return points


@pytest.fixture
def db_order(
    db_session,
    order: Order,
    db_points: list[Point],
) -> Order:
    order.destination_point_id = db_points[2].id
    db_session.add(order)
    db_session.flush()
    return order


@pytest.fixture
def db_orders(
    db_session,
    orders: list[Order],
    db_points: list[Point],
) -> list[Order]:
    orders[0].destination_point_id = db_points[1].id
    orders[1].destination_point_id = db_points[2].id

    db_session.add_all(orders)
    db_session.flush()

    return orders


class TestOrderService:
    def test_create_order(
        self,
        service: OrderService,
        db_session,
        db_points: list[Point],
    ):
        destination_point_id = db_points[2].id
        weight = 10
        reward = 80
        urgency = OrderUrgency.HIGH
        status = OrderStatus.AVAILABLE

        result = service.create_order(
            destination_point_id=destination_point_id,
            weight=weight,
            reward=reward,
            urgency=urgency,
            status=status,
        )

        assert result.destination_point_id == destination_point_id
        assert result.weight == weight
        assert result.reward == reward
        assert result.urgency == urgency
        assert result.status == status

        db_session.expire_all()

        persisted_order = db_session.get(Order, result.id)

        assert persisted_order is not None
        assert persisted_order.destination_point_id == destination_point_id
        assert persisted_order.weight == weight
        assert persisted_order.reward == reward
        assert persisted_order.urgency == urgency
        assert persisted_order.status == status

    def test_create_random_order(
        self,
        service: OrderService,
        db_session,
        db_points: list[Point],
    ):
        points_ids = [db_points[1].id, db_points[2].id]
        max_weight = 20

        destination_point_id = db_points[2].id
        weight = 15
        reward = 80
        urgency = OrderUrgency.HIGH

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

        assert result.destination_point_id == destination_point_id
        assert result.weight == weight
        assert result.reward == reward
        assert result.urgency == urgency
        assert result.status == OrderStatus.AVAILABLE

        db_session.expire_all()

        persisted_order = db_session.get(Order, result.id)

        assert persisted_order is not None
        assert persisted_order.destination_point_id == destination_point_id
        assert persisted_order.weight == weight
        assert persisted_order.reward == reward
        assert persisted_order.urgency == urgency
        assert persisted_order.status == OrderStatus.AVAILABLE

    def test_get_order(
        self,
        service: OrderService,
        db_order: Order,
    ):
        order_id = db_order.id

        result = service.get_order(order_id)

        assert result is db_order

    def test_get_order_not_found(
        self,
        service: OrderService,
    ):
        order_id = 999

        result = service.get_order(order_id)

        assert result is None

    def test_get_available_orders(
        self,
        service: OrderService,
        db_orders: list[Order],
    ):
        result = service.get_available_orders()

        assert result == db_orders

    def test_get_available_orders_without_available_orders(
        self,
        service: OrderService,
        db_orders: list[Order],
    ):
        for order in db_orders:
            order.status = OrderStatus.ASSIGNED

        result = service.get_available_orders()

        assert result == []

    def test_complete_order(
        self,
        service: OrderService,
        db_session,
        db_order: Order,
    ):
        service.complete_order(db_order)

        assert db_order.status == OrderStatus.COMPLETED

        db_session.expire_all()

        persisted_order = db_session.get(Order, db_order.id)

        assert persisted_order is not None
        assert persisted_order.status == OrderStatus.COMPLETED

    def test_assign_order(
        self,
        service: OrderService,
        db_session,
        db_order: Order,
    ):
        service.assign_order(db_order)

        assert db_order.status == OrderStatus.ASSIGNED

        db_session.expire_all()

        persisted_order = db_session.get(Order, db_order.id)

        assert persisted_order is not None
        assert persisted_order.status == OrderStatus.ASSIGNED

    def test_unassign_order(
        self,
        service: OrderService,
        db_session,
        db_order: Order,
    ):
        db_order.status = OrderStatus.ASSIGNED

        service.unassign_order(db_order)

        assert db_order.status == OrderStatus.AVAILABLE

        db_session.expire_all()

        persisted_order = db_session.get(Order, db_order.id)

        assert persisted_order is not None
        assert persisted_order.status == OrderStatus.AVAILABLE
