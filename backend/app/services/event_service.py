import logging
from random import choice, randint

from app.models.event import Event, EventType
from app.repositories.event_connector_repository import EventRepository


class EventService:
    """Manage game events."""

    def __init__(
        self,
        repository: EventRepository,
        logger: logging.Logger | None = None,
    ):
        self.repository = repository
        self.logger = logger if logger is not None else logging.getLogger(__name__)

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

        event = self.repository.create_event(event)
        self.logger.info(
            "Created event id=%s type=%s for turns %s-%s",
            event.id,
            event_type.value,
            event.start_turn,
            event.end_turn,
        )
        return event

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

        self.logger.debug(
            "Generated random event type=%s for turn=%s with duration=%s",
            event_type.value,
            turn,
            duration,
        )

        return self.create_event(
            event_type=event_type,
            title=title,
            description=description,
            turn=turn,
            duration=duration,
        )

    def get_event(self, event_id: int) -> Event | None:
        """Return an event by its identifier."""

        self.logger.debug("Fetching event id=%s", event_id)
        return self.repository.get_event(event_id)

    def get_active_events(self, turn: int) -> list[Event]:
        """Return currently active game events."""

        self.logger.debug("Fetching active events for turn=%s", turn)
        return self.repository.get_active_events(turn)
