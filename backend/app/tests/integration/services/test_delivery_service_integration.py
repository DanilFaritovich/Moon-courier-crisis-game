import pytest
from app.models.delivery import Delivery, DeliveryStatus
from app.models.order import Order
from app.models.rover import Rover
from app.repositories.delivery_connector_repository import DeliveryRepository
from app.services.connector.delivery_connector_service import (
    DeliveryConnectorRepository,
)
from app.services.delivery_service import DeliveryService


@pytest.fixture
def repository(db_session) -> DeliveryRepository:
    return DeliveryConnectorRepository(db_session)


@pytest.fixture
def service(repository: DeliveryRepository) -> DeliveryService:
    return DeliveryService(repository)


@pytest.fixture
def db_delivery(
    db_session,
    delivery: Delivery,
    order: Order,
    rover: Rover,
) -> Delivery:
    db_session.add(delivery)
    db_session.flush()
    return delivery


@pytest.fixture
def db_deliveries(
    db_session,
    deliveries: list[Delivery],
    orders: list[Order],
    rover: Rover,
) -> list[Delivery]:
    db_session.add_all(deliveries)
    db_session.flush()
    return deliveries


class TestDeliveryService:
    def test_create_delivery(
        self,
        service: DeliveryService,
        db_session,
        order: Order,
        rover: Rover,
    ):
        order_id = order.id
        rover_id = rover.id
        started_turn = 5

        result = service.create_delivery(
            order_id=order_id,
            rover_id=rover_id,
            started_turn=started_turn,
        )

        assert result.order_id == order_id
        assert result.rover_id == rover_id
        assert result.started_turn == started_turn
        assert result.status == DeliveryStatus.IN_PROGRESS

        db_session.expire_all()

        persisted_delivery = db_session.get(Delivery, result.id)

        assert persisted_delivery is not None
        assert persisted_delivery.order_id == order_id
        assert persisted_delivery.rover_id == rover_id
        assert persisted_delivery.started_turn == started_turn
        assert persisted_delivery.status == DeliveryStatus.IN_PROGRESS

    def test_delete_delivery(
        self,
        service: DeliveryService,
        db_session,
        db_delivery: Delivery,
    ):
        delivery_id = db_delivery.id

        service.delete_delivery(delivery_id)

        db_session.expire_all()

        result = db_session.get(Delivery, delivery_id)

        assert result is None

    def test_delete_delivery_not_found(
        self,
        service: DeliveryService,
    ):
        delivery_id = 999

        service.delete_delivery(delivery_id)

    def test_get_delivery(
        self,
        service: DeliveryService,
        db_delivery: Delivery,
    ):
        delivery_id = db_delivery.id

        result = service.get_delivery(delivery_id)

        assert result is db_delivery

    def test_get_delivery_not_found(
        self,
        service: DeliveryService,
    ):
        delivery_id = 999

        result = service.get_delivery(delivery_id)

        assert result is None

    def test_get_active_deliveries(
        self,
        service: DeliveryService,
        db_deliveries: list[Delivery],
    ):
        result = service.get_active_deliveries()

        expected_deliveries = [
            delivery
            for delivery in db_deliveries
            if delivery.status == DeliveryStatus.IN_PROGRESS
        ]

        assert result == expected_deliveries

    def test_get_active_deliveries_without_active_deliveries(
        self,
        service: DeliveryService,
        db_deliveries: list[Delivery],
    ):
        for delivery in db_deliveries:
            delivery.status = DeliveryStatus.COMPLETED

        result = service.get_active_deliveries()

        assert result == []

    def test_complete_delivery(
        self,
        service: DeliveryService,
        db_session,
        db_delivery: Delivery,
    ):
        service.complete_delivery(db_delivery)

        assert db_delivery.status == DeliveryStatus.COMPLETED

        db_session.expire_all()

        persisted_delivery = db_session.get(Delivery, db_delivery.id)

        assert persisted_delivery is not None
        assert persisted_delivery.status == DeliveryStatus.COMPLETED

    def test_fail_delivery(
        self,
        service: DeliveryService,
        db_session,
        db_delivery: Delivery,
    ):
        service.fail_delivery(db_delivery)

        assert db_delivery.status == DeliveryStatus.FAILED

        db_session.expire_all()

        persisted_delivery = db_session.get(Delivery, db_delivery.id)

        assert persisted_delivery is not None
        assert persisted_delivery.status == DeliveryStatus.FAILED
