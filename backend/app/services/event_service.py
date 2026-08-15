from datetime import datetime, timedelta, timezone
from random import choice

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
        expires_at: datetime,
    ) -> Event:
        """Create a new game event."""

        event = Event(
            event_type=event_type,
            title=title,
            description=description,
            expires_at=expires_at,
        )

        return self.repository.create_event(event)

    def create_random_event(
        self,
        duration: int,
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

        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=duration,
        )


        return self.create_event(
            event_type=event_type,
            title=title,
            description=description,
            expires_at=expires_at,
        )

    def get_event(self, event_id: int) -> Event | None:
        """Return an event by its identifier."""

        return self.repository.get_event(event_id)

    def get_active_events(self) -> list[Event]:
        """Return currently active game events."""

        return self.repository.get_active_events()