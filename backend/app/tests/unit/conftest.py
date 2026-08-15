from unittest.mock import Mock

import pytest
from app.models.point import Point, PointType
from app.models.road import Road
from app.repositories.delivery_connector_repository import DeliveryRepository
from app.repositories.graph_connector_repository import GraphRepository
from app.repositories.order_connector_repository import OrderRepository
from app.repositories.rover_connector_repository import RoverConnectorRepository


@pytest.fixture
def points() -> list[Point]:
    """Return test points for the lunar map."""
    return [
        Point(
            id=1,
            name="Lunar Base",
            type=PointType.BASE,
            x=0,
            y=0,
        ),
        Point(
            id=2,
            name="Route Point A",
            type=PointType.ROUTE,
            x=100,
            y=50,
        ),
        Point(
            id=3,
            name="Delivery Point",
            type=PointType.DELIVERY,
            x=200,
            y=100,
        ),
    ]


@pytest.fixture
def roads() -> list[Road]:
    """Return test roads for the lunar map."""
    return [
        Road(
            id=1,
            from_point_id=1,
            to_point_id=2,
            distance=10.0,
            risk=0.1,
            speed_modifier=1.0,
        ),
        Road(
            id=2,
            from_point_id=2,
            to_point_id=3,
            distance=15.0,
            risk=0.2,
            speed_modifier=0.8,
        ),
    ]

@pytest.fixture
def isolated_point() -> Point:
    """Return a point without any connected roads."""
    return Point(
        id=1,
        name="Isolated Point",
        type=PointType.ROUTE,
        x=500,
        y=500,
    )

@pytest.fixture
def graph_repository():
    """Return a mocked graph repository with test data."""
    return Mock(spec=GraphRepository)

@pytest.fixture
def order_repository():
    """Return a mocked graph repository with test data."""
    return Mock(spec=OrderRepository)

# ========================
# Rover
# ========================

@pytest.fixture
def rover_repository():
    """Return a mocked rover repository."""
    return Mock(spec=RoverConnectorRepository)

# ========================
# Delivery
# ========================

@pytest.fixture
def delivery_repository():
    """Return a mocked delivery repository."""

    return Mock(spec=DeliveryRepository)