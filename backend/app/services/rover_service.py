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
        battery_capacity: int,
        current_point_id: int,
    ) -> Rover:
        """Create a new rover."""

        rover = Rover(
            name=name,
            cargo_capacity=cargo_capacity,
            cargo=0.0,
            battery_capacity=battery_capacity,
            battery=battery_capacity,
            current_point_id=current_point_id,
            status=RoverStatus.IDLE,
        )

        return self.repository.create_rover(rover)

    def get_rover(self, rover_id: int) -> Rover | None:
        """Return a rover by its identifier."""

        return self.repository.get_rover(rover_id)

    def get_rover_with_max_weight(self) -> Rover | None:
        """Return a rover with the highest weight."""

        return self.repository.get_rover_with_max_weight()

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

    def get_battery_after_move(self, rover: Rover, distance: int, weight: int) -> int:
        """Calculate battery level after a move."""

        return rover.battery - distance * (rover.cargo + weight)

    def get_cargo_after_move(self, rover: Rover, weight: int) -> int:
        """Calculate cargo level after a move."""

        return rover.cargo + weight

    def move_rover(
        self, 
        rover: Rover, 
        point_id: int, 
        distance: int, 
        weight: int
    ) -> None:
        """Change rover current point."""

        rover.current_point_id = point_id
        rover.cargo = self.get_cargo_after_move(rover, weight)
        rover.battery = self.get_battery_after_move(rover, distance, weight)

        self.repository.update_rover(rover)

    def get_battery_after_move_back(
        self, 
        rover: Rover, 
        distance: int, 
        weight: int
    ) -> int:
        """Calculate battery level after a move back."""

        return rover.battery + distance * (rover.cargo + weight)
        
    def get_cargo_after_move_back(self, rover: Rover, weight: int) -> int:
        """Calculate cargo level after a move back."""

        return rover.cargo - weight

    def move_rover_back(
            self, 
            rover: Rover, 
            point_id: int, 
            distance: int, 
            weight: int
        ) -> None:
        """Change rover current point."""

        rover.current_point_id = point_id
        rover.cargo = self.get_cargo_after_move_back(rover, weight)
        rover.battery = self.get_battery_after_move_back(rover, distance, 0)

        self.repository.update_rover(rover)