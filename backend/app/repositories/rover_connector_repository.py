from abc import ABC, abstractmethod

from app.models.rover import Rover


class RoverConnectorRepository(ABC):
    """Abstract repository for rover data access."""

    @abstractmethod
    def create_rover(self, rover: Rover) -> Rover:
        """Persist a new rover."""
        ...

    @abstractmethod
    def get_rover(self, rover_id: int) -> Rover | None:
        """Return a rover by its identifier."""
        ...

    @abstractmethod
    def get_available_rovers(self) -> list[Rover]:
        """Return all idle rovers available for delivery."""
        ...

    @abstractmethod
    def update_rover(self, rover: Rover) -> None:
        """Persist rover changes."""
        ...