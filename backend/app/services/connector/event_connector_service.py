import logging

from app.models.event import Event
from app.repositories.event_connector_repository import EventRepository
from sqlalchemy import select
from sqlalchemy.orm import Session


class EventConnectorRepository(EventRepository):
    """SQLAlchemy implementation of the event repository."""

    def __init__(self, db: Session, logger: logging.Logger | None = None):
        self.db = db
        self.logger = logger if logger is not None else logging.getLogger(__name__)

    def create_event(self, event: Event) -> Event:
        """Create and persist a game event."""

        self.db.add(event)
        self.db.flush()
        self.logger.debug("Persisted event id=%s", event.id)

        return event

    def get_event(self, event_id: int) -> Event | None:
        """Return an event by its identifier."""

        self.logger.debug("Loading event id=%s", event_id)
        return self.db.get(Event, event_id)

    def get_active_events(self, turn: int) -> list[Event]:
        """Return events active on the given turn."""

        self.logger.debug("Loading active events for turn=%s", turn)
        return list(
            self.db.scalars(
                select(Event).where(
                    Event.start_turn <= turn,
                    Event.end_turn >= turn,
                )
            ).all()
        )

    def update_event(self, event: Event) -> Event:
        """Update and persist a game event."""

        self.db.flush()
        self.logger.debug("Updated persisted event id=%s", event.id)

        return event
