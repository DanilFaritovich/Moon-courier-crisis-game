from datetime import datetime, timedelta, timezone

from app.models.event import Event, EventType
from app.services.connector.event_connector_service import (
    EventConnectorRepository,
)


class TestEventConnectorRepository:
    def test_create_event(self, db_session):
        repository = EventConnectorRepository(db_session)

        event = Event(
            event_type=EventType.DUST_STORM,
            title="Dust Storm",
            description="A dust storm reduces rover speed.",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=3),
        )

        result = repository.create_event(event)

        assert result.id is not None
        assert result.event_type == EventType.DUST_STORM
        assert result.title == "Dust Storm"
        assert result.description == "A dust storm reduces rover speed."
        assert result.expires_at == event.expires_at

    def test_get_event(self, db_session, event):
        repository = EventConnectorRepository(db_session)

        result = repository.get_event(event.id)

        assert result is not None
        assert result.id == event.id
        assert result.event_type == event.event_type
        assert result.title == event.title

    def test_get_event_not_found(self, db_session):
        repository = EventConnectorRepository(db_session)

        result = repository.get_event(999999)

        assert result is None

    def test_get_active_events(
        self,
        db_session,
        events,
    ):
        repository = EventConnectorRepository(db_session)

        result = repository.get_active_events()

        assert len(result) == 1
        assert result[0].id == events[0].id

    def test_update_event(self, db_session, event):
        repository = EventConnectorRepository(db_session)

        event.title = "Updated Dust Storm"
        event.expires_at = datetime.now(timezone.utc) + timedelta(hours=5)

        result = repository.update_event(event)

        assert result.title == "Updated Dust Storm"

        db_session.expire_all()

        updated_event = repository.get_event(event.id)

        assert updated_event is not None
        assert updated_event.title == "Updated Dust Storm"
        assert updated_event.expires_at == event.expires_at