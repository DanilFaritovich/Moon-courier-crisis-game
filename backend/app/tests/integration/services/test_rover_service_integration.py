import pytest
from app.models.point import Point
from app.models.rover import Rover, RoverStatus
from app.repositories.rover_connector_repository import RoverConnectorRepository
from app.services.connector.rover_connector_service import RoverConnectorService
from app.services.rover_service import RoverService


@pytest.fixture
def repository(db_session) -> RoverConnectorRepository:
    return RoverConnectorService(db_session)


@pytest.fixture
def service(
    repository: RoverConnectorRepository,
) -> RoverService:
    return RoverService(repository)


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
    db_points: list[Point],
) -> Rover:
    rover.current_point_id = db_points[0].id

    db_session.add(rover)
    db_session.flush()

    return rover


@pytest.fixture
def db_rovers(
    db_session,
    rovers: list[Rover],
    db_points: list[Point],
) -> list[Rover]:
    rovers[0].current_point_id = db_points[0].id
    rovers[1].current_point_id = db_points[1].id

    db_session.add_all(rovers)
    db_session.flush()

    return rovers


class TestRoverService:
    def test_create_rover(
        self,
        service: RoverService,
        db_session,
        db_points: list[Point],
    ):
        name = "Rover-3"
        cargo_capacity = 120
        battery_capacity = 150
        current_point_id = db_points[0].id

        result = service.create_rover(
            name=name,
            cargo_capacity=cargo_capacity,
            battery_capacity=battery_capacity,
            current_point_id=current_point_id,
        )

        assert result.name == name
        assert result.cargo_capacity == cargo_capacity
        assert result.cargo == 0
        assert result.battery_capacity == battery_capacity
        assert result.battery == battery_capacity
        assert result.current_point_id == current_point_id
        assert result.status == RoverStatus.IDLE

        db_session.expire_all()

        persisted_rover = db_session.get(Rover, result.id)

        assert persisted_rover is not None
        assert persisted_rover.name == name
        assert persisted_rover.cargo_capacity == cargo_capacity
        assert persisted_rover.cargo == 0
        assert persisted_rover.battery_capacity == battery_capacity
        assert persisted_rover.battery == battery_capacity
        assert persisted_rover.current_point_id == current_point_id
        assert persisted_rover.status == RoverStatus.IDLE

    def test_get_rover(
        self,
        service: RoverService,
        db_rover: Rover,
    ):
        rover_id = db_rover.id

        result = service.get_rover(rover_id)

        assert result is db_rover

    def test_get_rover_not_found(
        self,
        service: RoverService,
    ):
        rover_id = 999

        result = service.get_rover(rover_id)

        assert result is None

    def test_get_rover_with_max_weight(
        self,
        service: RoverService,
        db_rovers: list[Rover],
    ):
        result = service.get_rover_with_max_weight()

        assert result is db_rovers[1]
        assert result.cargo_capacity == 150

    def test_get_rover_with_max_weight_without_rovers(
        self,
        service: RoverService,
    ):
        result = service.get_rover_with_max_weight()

        assert result is None

    def test_get_available_rovers(
        self,
        service: RoverService,
        db_rovers: list[Rover],
    ):
        delivering_status = RoverStatus.DELIVERING
        db_rovers[1].status = delivering_status

        result = service.get_available_rovers()

        assert result == [db_rovers[0]]

    def test_get_available_rovers_without_available_rovers(
        self,
        service: RoverService,
        db_rovers: list[Rover],
    ):
        delivering_status = RoverStatus.DELIVERING

        for rover in db_rovers:
            rover.status = delivering_status

        result = service.get_available_rovers()

        assert result == []

    def test_update_battery(
        self,
        service: RoverService,
        db_session,
        db_rover: Rover,
    ):
        battery = 60

        service.update_battery(db_rover, battery)

        assert db_rover.battery == battery

        db_session.expire_all()

        persisted_rover = db_session.get(Rover, db_rover.id)

        assert persisted_rover is not None
        assert persisted_rover.battery == battery

    @pytest.mark.parametrize(
        ("battery", "expected_battery"),
        [
            (-10, 0),
            (50, 50),
            (150, 100),
        ],
    )
    def test_update_battery_clamps_value(
        self,
        service: RoverService,
        db_rover: Rover,
        battery: int,
        expected_battery: int,
    ):
        service.update_battery(db_rover, battery)

        assert db_rover.battery == expected_battery

    def test_set_status(
        self,
        service: RoverService,
        db_session,
        db_rover: Rover,
    ):
        status = RoverStatus.DELIVERING

        service.set_status(db_rover, status)

        assert db_rover.status == status

        db_session.expire_all()

        persisted_rover = db_session.get(Rover, db_rover.id)

        assert persisted_rover is not None
        assert persisted_rover.status == status
