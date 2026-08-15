from app.models.delivery import Delivery, DeliveryStatus
from app.services.connector.delivery_connector_service import (
    DeliveryConnectorRepository,
)


class TestDeliveryConnectorRepository:
    def test_create_delivery(
        self,
        db_session,
        order,
        rover,
    ):
        repository = DeliveryConnectorRepository(db_session)

        delivery = Delivery(
            order_id=order.id,
            rover_id=rover.id,
        )

        result = repository.create_delivery(delivery)

        assert result.id is not None
        assert result.order_id == order.id
        assert result.rover_id == rover.id
        assert result.status == DeliveryStatus.IN_PROGRESS

    def test_get_delivery(
        self,
        db_session,
        db_delivery,
    ):
        repository = DeliveryConnectorRepository(db_session)

        result = repository.get_delivery(db_delivery.id)

        assert result is not None
        assert result.id == db_delivery.id
        assert result.order_id == db_delivery.order_id
        assert result.rover_id == db_delivery.rover_id

    def test_get_delivery_not_found(self, db_session):
        repository = DeliveryConnectorRepository(db_session)

        result = repository.get_delivery(999999)

        assert result is None

    def test_get_deliveries_by_status(
        self,
        db_session,
        db_deliveries,
    ):
        repository = DeliveryConnectorRepository(db_session)

        result = repository.get_deliveries_by_status(
            DeliveryStatus.IN_PROGRESS,
        )

        result_ids = {delivery.id for delivery in result}
        expected_ids = {
            delivery.id
            for delivery in db_deliveries
            if delivery.status == DeliveryStatus.IN_PROGRESS
        }

        assert result_ids == expected_ids

    def test_update_delivery(
        self,
        db_session,
        db_delivery,
    ):
        repository = DeliveryConnectorRepository(db_session)

        db_delivery.status = DeliveryStatus.COMPLETED

        result = repository.update_delivery(db_delivery)

        assert result.status == DeliveryStatus.COMPLETED

        db_session.expire_all()

        updated_delivery = db_session.get(
            Delivery,
            db_delivery.id,
        )

        assert updated_delivery is not None
        assert updated_delivery.status == DeliveryStatus.COMPLETED