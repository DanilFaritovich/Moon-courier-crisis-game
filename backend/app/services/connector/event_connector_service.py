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

    def get_active_events(self) -> list[Event]:
        """Return events that are currently active."""

        return list(
            self.db.scalars(
                select(Event).where(
                    Event.expires_at > datetime.utcnow(),
                )
            ).all()
        )

    def update_event(self, event: Event) -> Event:
        """Update and persist a game event."""

        self.db.commit()
        self.db.refresh(event)

        return event