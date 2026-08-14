from app.models.order import Order, OrderStatus, OrderUrgency
from app.models.point import Point, PointType
from app.services.connector.order_connector_service import OrderConnector


class TestOrderConnectorRepository:
    def test_create_order(self, db_session):
        """Create and persist an order in the database."""

        point = Point(
            id=1,
            name="Delivery Point",
            type=PointType.DELIVERY,
            x=100,
            y=100,
        )

        db_session.add(point)
        db_session.commit()

        repository = OrderConnector(db_session)

        order = Order(
            destination_point_id=point.id,
            weight=25.0,
            reward=100,
            urgency=OrderUrgency.HIGH,
        )

        created_order = repository.create_order(order)

        assert created_order.id is not None
        assert created_order.destination_point_id == point.id
        assert created_order.weight == 25.0
        assert created_order.reward == 100
        assert created_order.urgency == OrderUrgency.HIGH
        assert created_order.status == OrderStatus.AVAILABLE

    def test_get_order(self, db_session):
        """Return an order by its identifier."""

        point = Point(
            id=1,
            name="Delivery Point",
            type=PointType.DELIVERY,
            x=100,
            y=100,
        )

        order = Order(
            id=1,
            destination_point_id=1,
            weight=10.0,
            reward=50,
        )

        db_session.add_all([point, order])
        db_session.commit()

        repository = OrderConnector(db_session)

        result = repository.get_order(1)

        assert result is not None
        assert result.id == 1
        assert result.destination_point_id == 1
        assert result.weight == 10.0
        assert result.reward == 50

    def test_get_order_returns_none_for_missing_order(self, db_session):
        """Return None when the order does not exist."""

        repository = OrderConnector(db_session)

        result = repository.get_order(999)

        assert result is None

    def test_get_available_orders(self, db_session):
        """Return only orders with AVAILABLE status."""

        point = Point(
            id=1,
            name="Delivery Point",
            type=PointType.DELIVERY,
            x=100,
            y=100,
        )

        available_order = Order(
            id=1,
            destination_point_id=1,
            weight=10.0,
            reward=50,
            status=OrderStatus.AVAILABLE,
        )

        completed_order = Order(
            id=2,
            destination_point_id=1,
            weight=20.0,
            reward=100,
            status=OrderStatus.COMPLETED,
        )

        db_session.add_all([
            point,
            available_order,
            completed_order,
        ])
        db_session.commit()

        repository = OrderConnector(db_session)

        orders = repository.get_available_orders()

        assert len(orders) == 1
        assert orders[0].id == 1
        assert orders[0].status == OrderStatus.AVAILABLE

    def test_complete_order(self, db_session):
        """Change an order status to COMPLETED."""

        point = Point(
            id=1,
            name="Delivery Point",
            type=PointType.DELIVERY,
            x=100,
            y=100,
        )

        order = Order(
            id=1,
            destination_point_id=1,
            weight=10.0,
            reward=50,
        )

        db_session.add_all([point, order])
        db_session.commit()

        repository = OrderConnector(db_session)

        repository.complete_order(order)

        db_session.refresh(order)

        assert order.status == OrderStatus.COMPLETED

    def test_fail_order(self, db_session):
        """Change an order status to FAILED."""

        point = Point(
            id=1,
            name="Delivery Point",
            type=PointType.DELIVERY,
            x=100,
            y=100,
        )

        order = Order(
            id=1,
            destination_point_id=1,
            weight=10.0,
            reward=50,
        )

        db_session.add_all([point, order])
        db_session.commit()

        repository = OrderConnector(db_session)

        repository.fail_order(order)

        db_session.refresh(order)

        assert order.status == OrderStatus.FAILED