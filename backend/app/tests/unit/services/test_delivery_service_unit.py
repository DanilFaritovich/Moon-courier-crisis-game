from unittest.mock import Mock

import pytest
from app.models.delivery import Delivery, DeliveryStatus
from app.repositories.delivery_connector_repository import DeliveryRepository
from app.services.delivery_service import DeliveryService


@pytest.fixture
def repository() -> Mock:
    return Mock(spec=DeliveryRepository)


@pytest.fixture
def service(repository: Mock) -> DeliveryService:
    return DeliveryService(repository)


class TestDeliveryServiceUnit:
    def test_create_delivery(
        self,
        service: DeliveryService,
        repository: Mock,
        delivery: Delivery,
    ) -> None:
        repository.create_delivery.return_value = delivery

        result = service.create_delivery(
            order_id=delivery.order_id,
            rover_id=delivery.rover_id,
            started_turn=delivery.started_turn,
        )

        assert result is delivery

        repository.create_delivery.assert_called_once()
        created_delivery = repository.create_delivery.call_args.args[0]

        assert isinstance(created_delivery, Delivery)
        assert created_delivery.order_id == delivery.order_id
        assert created_delivery.rover_id == delivery.rover_id
        assert created_delivery.started_turn == delivery.started_turn

    def test_delete_delivery(
        self,
        service: DeliveryService,
        repository: Mock,
        delivery: Delivery,
    ) -> None:
        service.delete_delivery(delivery.id)

        repository.delete_delivery.assert_called_once_with(delivery.id)

    def test_get_delivery(
        self,
        service: DeliveryService,
        repository: Mock,
        delivery: Delivery,
    ) -> None:
        repository.get_delivery.return_value = delivery

        result = service.get_delivery(delivery.id)

        assert result is delivery
        repository.get_delivery.assert_called_once_with(delivery.id)

    def test_get_active_deliveries(
        self,
        service: DeliveryService,
        repository: Mock,
        deliveries: list[Delivery],
    ) -> None:
        repository.get_deliveries_by_status.return_value = deliveries

        result = service.get_active_deliveries()

        assert result == deliveries
        repository.get_deliveries_by_status.assert_called_once_with(
            DeliveryStatus.IN_PROGRESS,
        )

    def test_complete_delivery(
        self,
        service: DeliveryService,
        repository: Mock,
        delivery: Delivery,
    ) -> None:
        service.complete_delivery(delivery)

        assert delivery.status == DeliveryStatus.COMPLETED
        repository.update_delivery.assert_called_once_with(delivery)

    def test_fail_delivery(
        self,
        service: DeliveryService,
        repository: Mock,
        delivery: Delivery,
    ) -> None:
        service.fail_delivery(delivery)

        assert delivery.status == DeliveryStatus.FAILED
        repository.update_delivery.assert_called_once_with(delivery)
