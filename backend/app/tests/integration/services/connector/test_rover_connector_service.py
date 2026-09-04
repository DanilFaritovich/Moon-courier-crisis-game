import pytest
from app.models.point import Point
from app.models.rover import Rover, RoverStatus
from app.services.connector.rover_connector_service import (
    RoverConnectorService,
)


@pytest.fixture
def repository(
    db_session,
) -> RoverConnectorService:
    return RoverConnectorService(db_session)


@pytest.fixture
def db_point(
    db_session,
    base_point: Point,
) -> Point:
    db_session.add(base_point)
    db_session.flush()

    return base_point


@pytest.fixture
def db_points(
    db_session,
    points: list[Point],
) -> list[Point]:
    db_session.add_all(points)
    db_session.flush()

    return points


@pytest.fixture
def db_rover(
    db_session,
    rover: Rover,
    db_point: Point,
) -> Rover:
    db_session.add(rover)
    db_session.flush()

    return rover


@pytest.fixture
def db_rovers(
    db_session,
    rovers: list[Rover],
    db_points: list[Point],
) -> list[Rover]:
    db_session.add_all(rovers)
    db_session.flush()

    return rovers


class TestRoverConnectorService:
    def test_create_rover(
        self,
        repository: RoverConnectorService,
        rover: Rover,
        db_point: Point,
    ):
        result = repository.create_rover(rover)

        assert result is rover
        assert result.id == rover.id
        assert result.name == rover.name
        assert result.cargo_capacity == rover.cargo_capacity
        assert result.cargo == rover.cargo
        assert result.battery_capacity == rover.battery_capacity
        assert result.battery == rover.battery
        assert result.current_point_id == rover.current_point_id
        assert result.status == RoverStatus.IDLE

    def test_get_rover(
        self,
        repository: RoverConnectorService,
        db_rover: Rover,
    ):
        rover_id = db_rover.id

        result = repository.get_rover(rover_id)

        assert result is db_rover

    def test_get_rover_not_found(
        self,
        repository: RoverConnectorService,
    ):
        rover_id = 999

        result = repository.get_rover(rover_id)

        assert result is None

    def test_get_rover_with_max_weight(
        self,
        repository: RoverConnectorService,
        db_rovers: list[Rover],
    ):
        result = repository.get_rover_with_max_weight()

        assert result is db_rovers[1]
        assert result.cargo_capacity == 150

    def test_get_rover_with_max_weight_without_rovers(
        self,
        repository: RoverConnectorService,
    ):
        result = repository.get_rover_with_max_weight()

        assert result is None

    def test_get_available_rovers(
        self,
        repository: RoverConnectorService,
        db_rovers: list[Rover],
    ):
        delivering_status = RoverStatus.DELIVERING
        db_rovers[1].status = delivering_status

        result = repository.get_available_rovers()

        assert result == [db_rovers[0]]

    def test_get_available_rovers_without_available_rovers(
        self,
        repository: RoverConnectorService,
        db_rovers: list[Rover],
    ):
        status = RoverStatus.DELIVERING

        for rover in db_rovers:
            rover.status = status

        result = repository.get_available_rovers()

        assert result == []

    def test_update_rover(
        self,
        repository: RoverConnectorService,
        db_rover: Rover,
    ):
        name = "Rover-Updated"
        cargo = 40
        battery = 60
        status = RoverStatus.DELIVERING

        db_rover.name = name
        db_rover.cargo = cargo
        db_rover.battery = battery
        db_rover.status = status

        result = repository.update_rover(db_rover)

        assert result is db_rover
        assert result.name == name
        assert result.cargo == cargo
        assert result.battery == battery
        assert result.status == status

        persisted_rover = repository.get_rover(db_rover.id)

        assert persisted_rover is db_rover
        assert persisted_rover.name == name
        assert persisted_rover.cargo == cargo
        assert persisted_rover.battery == battery
        assert persisted_rover.status == status
