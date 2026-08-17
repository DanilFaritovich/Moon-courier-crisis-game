from datetime import datetime

from app.models.event import Event
from app.repositories.event_connector_repository import EventRepository
from sqlalchemy import select
from sqlalchemy.orm import Session


class EventConnectorRepository(EventRepository):
    """SQLAlchemy implementation of the event repository."""

    def __init__(self, db: Session):
        self.db = db

    def create_event(self, event: Event) -> Event:
        """Create and persist a game event."""

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        return event

    def get_event(self, event_id: int) -> Event | None:
        """Return an event by its identifier."""

        return self.db.get(Event, event_id)

    def get_active_events(self, turn: int) -> list[Event]:
        """Return events active on the given turn."""

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

        self.db.commit()
        self.db.refresh(event)

        return event