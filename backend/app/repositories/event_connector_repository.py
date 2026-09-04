from abc import ABC, abstractmethod

from app.models.event import Event


class EventRepository(ABC):
    """Repository interface for game events."""

    @abstractmethod
    def create_event(self, event: Event) -> Event:
        """Create and persist a game event."""
        ...

    @abstractmethod
    def get_event(self, event_id: int) -> Event | None:
        """Return an event by its identifier."""
        ...

    @abstractmethod
    def get_active_events(self, turn: int) -> list[Event]:
        """Return all active game events."""
        ...

    @abstractmethod
    def update_event(self, event: Event) -> Event:
        """Update and persist a game event."""
        ...
