import pytest
from app.models.order import Order, OrderStatus, OrderUrgency
from app.services.connector.order_connector_service import OrderConnector


@pytest.fixture
def repository(
    db_session,
) -> OrderConnector:
    return OrderConnector(db_session)


@pytest.fixture
def db_order(
    db_session,
    order: Order,
) -> Order:
    db_session.add(order)
    db_session.flush()

    return order


@pytest.fixture
def db_orders(
    db_session,
    orders: list[Order],
) -> list[Order]:
    db_session.add_all(orders)
    db_session.flush()

    return orders


@pytest.fixture
def db_orders_by_status(
    db_session,
    orders_by_status: list[Order],
) -> list[Order]:
    db_session.add_all(orders_by_status)
    db_session.flush()

    return orders_by_status


class TestOrderConnector:
    def test_create_order(
        self,
        repository: OrderConnector,
        order: Order,
    ):
        result = repository.create_order(order)

        assert result is order
        assert result.id is not None

        assert result.destination_point_id == order.destination_point_id
        assert result.weight == order.weight
        assert result.reward == order.reward
        assert result.urgency == order.urgency
        assert result.status == order.status

    def test_get_order(
        self,
        repository: OrderConnector,
        db_order: Order,
    ):
        order_id = db_order.id

        result = repository.get_order(order_id)

        assert result is db_order

    def test_get_order_not_found(
        self,
        repository: OrderConnector,
    ):
        order_id = 999

        result = repository.get_order(order_id)

        assert result is None

    def test_get_available_orders(
        self,
        repository: OrderConnector,
        db_orders_by_status: list[Order],
    ):
        result = repository.get_available_orders()

        assert result == [db_orders_by_status[0]]

    def test_get_available_orders_without_available_orders(
        self,
        repository: OrderConnector,
        db_orders: list[Order],
    ):
        for order in db_orders:
            order.status = OrderStatus.ASSIGNED

        result = repository.get_available_orders()

        assert result == []

    def test_update_order(
        self,
        repository: OrderConnector,
        db_order: Order,
    ):
        weight = 10
        reward = 120
        urgency = OrderUrgency.HIGH
        status = OrderStatus.ASSIGNED

        db_order.weight = weight
        db_order.reward = reward
        db_order.urgency = urgency
        db_order.status = status

        result = repository.update_order(db_order)

        assert result is db_order
        assert result.weight == weight
        assert result.reward == reward
        assert result.urgency == urgency
        assert result.status == status

        persisted_order = repository.get_order(db_order.id)

        assert persisted_order is db_order
        assert persisted_order.weight == weight
        assert persisted_order.reward == reward
        assert persisted_order.urgency == urgency
        assert persisted_order.status == status
