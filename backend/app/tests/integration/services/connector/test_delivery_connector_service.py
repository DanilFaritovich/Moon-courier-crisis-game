import pytest
from app.models.delivery import Delivery, DeliveryStatus
from app.models.order import Order
from app.models.rover import Rover
from app.services.connector.delivery_connector_service import (
    DeliveryConnectorRepository,
)


@pytest.fixture
def repository(
    db_session,
) -> DeliveryConnectorRepository:
    return DeliveryConnectorRepository(db_session)


@pytest.fixture
def db_delivery(
    db_session,
    order: Order,
    rover: Rover,
) -> Delivery:
    started_turn = 1

    delivery = Delivery(
        order_id=order.id,
        rover_id=rover.id,
        started_turn=started_turn,
    )

    db_session.add(delivery)
    db_session.flush()

    return delivery


@pytest.fixture
def db_deliveries_by_status(
    db_session,
    orders: list[Order],
    rover: Rover,
) -> dict[DeliveryStatus, Delivery]:
    in_progress_delivery = Delivery(
        order_id=orders[0].id,
        rover_id=rover.id,
        started_turn=1,
        status=DeliveryStatus.IN_PROGRESS,
    )
    completed_delivery = Delivery(
        order_id=orders[1].id,
        rover_id=rover.id,
        started_turn=2,
        status=DeliveryStatus.COMPLETED,
    )

    db_session.add_all(
        [
            in_progress_delivery,
            completed_delivery,
        ]
    )
    db_session.flush()

    return {
        DeliveryStatus.IN_PROGRESS: in_progress_delivery,
        DeliveryStatus.COMPLETED: completed_delivery,
    }


class TestDeliveryConnectorRepository:
    def test_create_delivery(
        self,
        repository: DeliveryConnectorRepository,
        delivery: Delivery,
    ):
        result = repository.create_delivery(delivery)

        assert result is delivery
        assert result.id is not None
        assert result.order_id == delivery.order_id
        assert result.rover_id == delivery.rover_id
        assert result.status == DeliveryStatus.IN_PROGRESS
        assert result.started_turn == delivery.started_turn
        assert result.completed_turn is None

    def test_get_delivery(
        self,
        repository: DeliveryConnectorRepository,
        db_delivery: Delivery,
    ):
        result = repository.get_delivery(db_delivery.id)

        assert result is db_delivery

    def test_get_delivery_not_found(
        self,
        repository: DeliveryConnectorRepository,
    ):
        delivery_id = 999

        result = repository.get_delivery(delivery_id)

        assert result is None

    def test_get_deliveries_by_status(
        self,
        repository: DeliveryConnectorRepository,
        db_deliveries_by_status: dict[DeliveryStatus, Delivery],
    ):
        status = DeliveryStatus.IN_PROGRESS

        result = repository.get_deliveries_by_status(status)

        assert result == [db_deliveries_by_status[status]]

    def test_update_delivery(
        self,
        repository: DeliveryConnectorRepository,
        db_delivery: Delivery,
    ):
        completed_turn = 5

        db_delivery.status = DeliveryStatus.COMPLETED
        db_delivery.completed_turn = completed_turn

        result = repository.update_delivery(db_delivery)

        assert result is db_delivery
        assert result.status == DeliveryStatus.COMPLETED
        assert result.completed_turn == completed_turn

        persisted_delivery = repository.get_delivery(db_delivery.id)

        assert persisted_delivery is db_delivery
        assert persisted_delivery.status == DeliveryStatus.COMPLETED
        assert persisted_delivery.completed_turn == completed_turn

    def test_delete_delivery(
        self,
        repository: DeliveryConnectorRepository,
        db_delivery: Delivery,
    ):
        delivery_id = db_delivery.id

        repository.delete_delivery(delivery_id)

        result = repository.get_delivery(delivery_id)

        assert result is None
