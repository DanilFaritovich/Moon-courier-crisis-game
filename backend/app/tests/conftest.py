import pytest
from app.models.delivery import Delivery, DeliveryStatus
from app.models.order import Order, OrderStatus, OrderUrgency
from app.models.point import Point, PointType
from app.models.rover import Rover, RoverStatus


@pytest.fixture
def point() -> Point:
    """Return a test lunar base."""

    return Point(
        id=1,
        name="Lunar Base",
        type=PointType.BASE,
        x=0,
        y=0,
    )

# ========================
# Order
# ========================

@pytest.fixture
def order():
    """Return a test order."""

    return Order(
        id=1,
        destination_point_id=10,
        weight=25.0,
        reward=100,
        urgency=OrderUrgency.HIGH,
        status=OrderStatus.AVAILABLE
    )

# ========================
# Rover
# ========================

@pytest.fixture
def rover():
    """Return a rover."""

    return Rover(
        id=1,
        name="Rover A",
        cargo_capacity=40.0,
        battery=100,
        current_point_id=1,
        status=RoverStatus.IDLE,
    )

@pytest.fixture
def rovers():
    """Return a rover."""
    rovers = [
        Rover(
            id=1,
            name="Rover A",
            cargo_capacity=40.0,
            battery=100,
            current_point_id=1,
            status=RoverStatus.IDLE,
        ),
        Rover(
            id=2,
            name="Rover B",
            cargo_capacity=40.0,
            battery=100,
            current_point_id=2,
            status=RoverStatus.IDLE,
        )
    ]
    return rovers

# ========================
# Delivery
# ========================

@pytest.fixture
def delivery():
    """Return a test delivery."""

    return Delivery(
        id=1,
        order_id=10,
        rover_id=5,
        status=DeliveryStatus.IN_PROGRESS,
    )

@pytest.fixture
def deliveries():
    """Return test deliveries."""

    return [
        Delivery(
            id=1,
            order_id=10,
            rover_id=5,
            status=DeliveryStatus.IN_PROGRESS,
        ),
        Delivery(
            id=2,
            order_id=11,
            rover_id=6,
            status=DeliveryStatus.IN_PROGRESS,
        ),
    ]