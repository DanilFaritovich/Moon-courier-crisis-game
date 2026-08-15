from app.models.rover import Rover, RoverStatus
from app.repositories.rover_connector_repository import RoverConnectorRepository


class RoverService:
    """Manage rover business logic."""

    def __init__(self, repository: RoverConnectorRepository):
        self.repository = repository

    def create_rover(
        self,
        name: str,
        cargo_capacity: float,
        current_point_id: int,
    ) -> Rover:
        """Create a new rover."""

        rover = Rover(
            name=name,
            cargo_capacity=cargo_capacity,
            battery=100,
            current_point_id=current_point_id,
            status=RoverStatus.IDLE,
        )

        return self.repository.create_rover(rover)

    def get_rover(self, rover_id: int) -> Rover | None:
        """Return a rover by its identifier."""

        return self.repository.get_rover(rover_id)

    def get_available_rovers(self) -> list[Rover]:
        """Return rovers that are ready for delivery."""

        return self.repository.get_available_rovers()

    def update_battery(self, rover: Rover, battery: int) -> None:
        """Update rover battery level."""

        rover.battery = max(0, min(100, battery))
        self.repository.update_rover(rover)

    def set_status(self, rover: Rover, status: RoverStatus) -> None:
        """Change rover status."""

        rover.status = status
        self.repository.update_rover(rover)