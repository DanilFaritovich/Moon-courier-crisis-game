from app.models.delivery import DeliveryStatus
from app.services.delivery_service import DeliveryService


class TestDeliveryService:
    def test_create_delivery(self, delivery_repository):
        """Create a delivery and pass it to the repository."""

        delivery_repository.create_delivery.side_effect = (
            lambda delivery: delivery
        )

        service = DeliveryService(delivery_repository)

        delivery = service.create_delivery(
            order_id=10,
            rover_id=5,
            started_turn=1,
        )

        assert delivery.order_id == 10
        assert delivery.rover_id == 5
        assert delivery.started_turn == 1
        
        delivery_repository.create_delivery.assert_called_once_with(
            delivery
        )

    def test_get_delivery(
        self,
        delivery_repository,
        delivery,
    ):
        """Return a delivery from the repository."""

        delivery_repository.get_delivery.return_value = delivery

        service = DeliveryService(delivery_repository)

        result = service.get_delivery(delivery.id)

        assert result is delivery
        delivery_repository.get_delivery.assert_called_once_with(
            delivery.id
        )

    def test_get_delivery_not_found(self, delivery_repository):
        """Return None when the delivery does not exist."""

        delivery_repository.get_delivery.return_value = None

        service = DeliveryService(delivery_repository)

        result = service.get_delivery(999)

        assert result is None
        delivery_repository.get_delivery.assert_called_once_with(999)

    def test_get_active_deliveries(
        self,
        delivery_repository,
        deliveries,
    ):
        """Return deliveries currently in progress."""

        delivery_repository.get_deliveries_by_status.return_value = deliveries

        service = DeliveryService(delivery_repository)

        result = service.get_active_deliveries()

        assert result == deliveries
        delivery_repository.get_deliveries_by_status.assert_called_once_with(
            DeliveryStatus.IN_PROGRESS
        )

    def test_complete_delivery(
        self,
        delivery_repository,
        delivery,
    ):
        """Mark a delivery as completed."""

        service = DeliveryService(delivery_repository)

        service.complete_delivery(delivery)

        assert delivery.status == DeliveryStatus.COMPLETED
        delivery_repository.update_delivery.assert_called_once_with(
            delivery
        )

    def test_fail_delivery(
        self,
        delivery_repository,
        delivery,
    ):
        """Mark a delivery as failed."""

        service = DeliveryService(delivery_repository)

        service.fail_delivery(delivery)

        assert delivery.status == DeliveryStatus.FAILED
        delivery_repository.update_delivery.assert_called_once_with(
            delivery
        )