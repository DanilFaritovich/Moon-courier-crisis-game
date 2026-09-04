from unittest.mock import Mock

import pytest
from app.models.rover import Rover, RoverStatus
from app.repositories.rover_connector_repository import RoverConnectorRepository
from app.services.rover_service import RoverService


@pytest.fixture
def repository() -> Mock:
    return Mock(spec=RoverConnectorRepository)


@pytest.fixture
def service(repository: Mock) -> RoverService:
    return RoverService(repository)


class TestRoverServiceUnit:
    def test_create_rover(
        self,
        service: RoverService,
        repository: Mock,
        rover: Rover,
    ) -> None:
        name = rover.name
        cargo_capacity = rover.cargo_capacity
        battery_capacity = rover.battery_capacity
        current_point_id = rover.current_point_id

        repository.create_rover.return_value = rover

        result = service.create_rover(
            name=name,
            cargo_capacity=cargo_capacity,
            battery_capacity=battery_capacity,
            current_point_id=current_point_id,
        )

        assert result is rover

        repository.create_rover.assert_called_once()
        created_rover = repository.create_rover.call_args.args[0]

        assert isinstance(created_rover, Rover)
        assert created_rover.name == name
        assert created_rover.cargo_capacity == cargo_capacity
        assert created_rover.cargo == 0.0
        assert created_rover.battery_capacity == battery_capacity
        assert created_rover.battery == battery_capacity
        assert created_rover.current_point_id == current_point_id
        assert created_rover.status == RoverStatus.IDLE

    def test_get_rover(
        self,
        service: RoverService,
        repository: Mock,
        rover: Rover,
    ) -> None:
        rover_id = rover.id

        repository.get_rover.return_value = rover

        result = service.get_rover(rover_id)

        assert result is rover
        repository.get_rover.assert_called_once_with(rover_id)

    def test_get_rover_with_max_weight(
        self,
        service: RoverService,
        repository: Mock,
        rover: Rover,
    ) -> None:
        repository.get_rover_with_max_weight.return_value = rover

        result = service.get_rover_with_max_weight()

        assert result is rover
        repository.get_rover_with_max_weight.assert_called_once_with()

    def test_get_available_rovers(
        self,
        service: RoverService,
        repository: Mock,
        rovers: list[Rover],
    ) -> None:
        repository.get_available_rovers.return_value = rovers

        result = service.get_available_rovers()

        assert result == rovers
        repository.get_available_rovers.assert_called_once_with()

    def test_update_battery(
        self,
        service: RoverService,
        repository: Mock,
        rover: Rover,
    ) -> None:
        battery = 60

        service.update_battery(rover, battery)

        assert rover.battery == battery
        repository.update_rover.assert_called_once_with(rover)

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
        repository: Mock,
        rover: Rover,
        battery: int,
        expected_battery: int,
    ) -> None:
        service.update_battery(rover, battery)

        assert rover.battery == expected_battery
        repository.update_rover.assert_called_once_with(rover)

    def test_set_status(
        self,
        service: RoverService,
        repository: Mock,
        rover: Rover,
    ) -> None:
        status = RoverStatus.IDLE

        service.set_status(rover, status)

        assert rover.status == status
        repository.update_rover.assert_called_once_with(rover)

    def test_get_battery_after_move(
        self,
        service: RoverService,
        rover: Rover,
    ) -> None:
        distance = 5
        weight = 10

        cargo_after_move = rover.cargo + weight
        battery_consumption = distance * cargo_after_move
        expected_battery = rover.battery - battery_consumption

        result = service.get_battery_after_move(
            rover,
            distance,
            weight,
        )

        assert result == expected_battery

    def test_get_cargo_after_move(
        self,
        service: RoverService,
        rover: Rover,
    ) -> None:
        weight = 10
        expected_cargo = rover.cargo + weight

        result = service.get_cargo_after_move(
            rover,
            weight,
        )

        assert result == expected_cargo

    def test_move_rover(
        self,
        service: RoverService,
        repository: Mock,
        rover: Rover,
    ) -> None:
        point_id = 20
        distance = 5
        weight = 10

        initial_cargo = rover.cargo
        initial_battery = rover.battery

        expected_cargo = initial_cargo + weight
        expected_battery = initial_battery - distance * (initial_cargo + weight)

        service.move_rover(
            rover,
            point_id,
            distance,
            weight,
        )

        assert rover.current_point_id == point_id
        assert rover.cargo == expected_cargo
        assert rover.battery == expected_battery

        repository.update_rover.assert_called_once_with(rover)

    def test_get_battery_after_move_back(
        self,
        service: RoverService,
        rover: Rover,
    ) -> None:
        distance = 5

        expected_battery = rover.battery + distance * rover.cargo

        result = service.get_battery_after_move_back(
            rover,
            distance,
        )

        assert result == expected_battery

    def test_get_cargo_after_move_back(
        self,
        service: RoverService,
        rover: Rover,
    ) -> None:
        weight = 10
        expected_cargo = rover.cargo - weight

        result = service.get_cargo_after_move_back(
            rover,
            weight,
        )

        assert result == expected_cargo

    def test_move_rover_back(
        self,
        service: RoverService,
        repository: Mock,
        rover: Rover,
    ) -> None:
        point_id = 10
        distance = 5
        weight = 10

        initial_cargo = rover.cargo
        initial_battery = rover.battery

        expected_cargo = initial_cargo - weight
        expected_battery = initial_battery + distance * initial_cargo

        service.move_rover_back(
            rover,
            point_id,
            distance,
            weight,
        )

        assert rover.current_point_id == point_id
        assert rover.cargo == expected_cargo
        assert rover.battery == expected_battery

        repository.update_rover.assert_called_once_with(rover)

    def test_move_rover_forward_and_back(
        self,
        service: RoverService,
        repository: Mock,
        rover: Rover,
    ) -> None:
        initial_point_id = rover.current_point_id
        initial_cargo = rover.cargo
        initial_battery = rover.battery

        forward_point_id = 20
        forward_distance = 5
        weight = 10

        service.move_rover(
            rover,
            forward_point_id,
            forward_distance,
            weight,
        )

        assert rover.current_point_id == forward_point_id
        assert rover.cargo == initial_cargo + weight
        assert rover.battery == (
            initial_battery - forward_distance * (initial_cargo + weight)
        )

        service.move_rover_back(
            rover,
            initial_point_id,
            forward_distance,
            weight,
        )

        assert rover.current_point_id == initial_point_id
        assert rover.cargo == initial_cargo
        assert rover.battery == initial_battery

        assert repository.update_rover.call_count == 2
