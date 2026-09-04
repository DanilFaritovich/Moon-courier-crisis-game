from random import choice, randint

from app.models.event import Event, EventType
from app.repositories.event_connector_repository import EventRepository


class EventService:
    """Manage game events."""

    def __init__(self, repository: EventRepository):
        self.repository = repository

    def create_event(
        self,
        event_type: EventType,
        title: str,
        description: str,
        turn: int,
        duration: int,
    ) -> Event:
        """Create a new game event."""

        event = Event(
            event_type=event_type,
            title=title,
            description=description,
            start_turn=turn,
            end_turn=turn + duration - 1,
        )

        return self.repository.create_event(event)

    def create_random_event(
        self,
        turn: int,
        duration: int | None = None,
    ) -> Event:
        """Create a random game event."""

        event_type = choice(list(EventType))

        event_data = {
            EventType.SOLAR_STORM: (
                "Solar Storm",
                "Solar activity increases battery consumption.",
            ),
            EventType.METEOR_SHOWER: (
                "Meteor Shower",
                "Meteor activity increases route risk.",
            ),
            EventType.DUST_STORM: (
                "Dust Storm",
                "A dust storm reduces rover speed.",
            ),
            EventType.ROVER_MALFUNCTION: (
                "Rover Malfunction",
                "A rover may lose additional battery.",
            ),
        }

        title, description = event_data[event_type]

        if duration is None:
            duration = randint(1, 3)

        return self.create_event(
            event_type=event_type,
            title=title,
            description=description,
            turn=turn,
            duration=duration,
        )

    def get_event(self, event_id: int) -> Event | None:
        """Return an event by its identifier."""

        return self.repository.get_event(event_id)

    def get_active_events(self, turn: int) -> list[Event]:
        """Return currently active game events."""

        return self.repository.get_active_events(turn)
