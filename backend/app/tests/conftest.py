import pytest

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
# Rover
# ========================

@pytest.fixture
def rover():
    """Return a rover."""
    rover = Rover(
        id=1,
        name="Rover A",
        cargo_capacity=40.0,
        battery=100,
        current_point_id=1,
        status=RoverStatus.IDLE,
    )
    return rover