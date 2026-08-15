from app.models.rover import Rover, RoverStatus
from app.services.rover_service import RoverService


class TestRoverService:
    def test_create_rover(self, rover_repository):
        """Create a rover and pass it to the repository."""

        rover_repository.create_rover.side_effect = lambda rover: rover

        service = RoverService(rover_repository)

        rover = service.create_rover(
            name="Rover A",
            cargo_capacity=40.0,
            current_point_id=1,
        )

        assert isinstance(rover, Rover)
        assert rover.name == "Rover A"
        assert rover.cargo_capacity == 40.0
        assert rover.current_point_id == 1
        assert rover.battery == 100
        assert rover.status == RoverStatus.IDLE

        rover_repository.create_rover.assert_called_once_with(rover)

    def test_get_rover(self, rover_repository, rover):
        """Return a rover by its identifier."""

        rover_repository.get_rover.return_value = rover

        service = RoverService(rover_repository)

        result = service.get_rover(1)

        assert result is rover
        rover_repository.get_rover.assert_called_once_with(1)

    def test_get_available_rovers(self, rover_repository, rovers):
        """Return all idle rovers."""

        rover_repository.get_available_rovers.return_value = rovers

        service = RoverService(rover_repository)

        result = service.get_available_rovers()

        assert result == rovers
        assert len(result) == 2

        rover_repository.get_available_rovers.assert_called_once()

    def test_update_battery(self, rover_repository, rover):
        """Clamp battery value and update rover."""

        service = RoverService(rover_repository)

        service.update_battery(rover, 65)

        assert rover.battery == 65
        rover_repository.update_rover.assert_called_once_with(rover)

    def test_update_battery_clamps_to_zero(self, rover_repository, rover):
        """Battery level cannot be below zero."""

        service = RoverService(rover_repository)

        service.update_battery(rover, -10)

        assert rover.battery == 0
        rover_repository.update_rover.assert_called_once_with(rover)

    def test_set_status(self, rover_repository, rover):
        """Change rover status."""

        service = RoverService(rover_repository)

        service.set_status(rover, RoverStatus.DELIVERING)

        assert rover.status == RoverStatus.DELIVERING
        rover_repository.update_rover.assert_called_once_with(rover)