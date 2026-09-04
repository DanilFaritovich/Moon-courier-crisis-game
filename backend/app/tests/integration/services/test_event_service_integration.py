from unittest.mock import patch

import pytest
from app.models.event import Event, EventType
from app.repositories.event_connector_repository import EventRepository
from app.services.connector.event_connector_service import EventConnectorRepository
from app.services.event_service import EventService


@pytest.fixture
def repository(db_session) -> EventRepository:
    return EventConnectorRepository(db_session)


@pytest.fixture
def service(repository: EventRepository) -> EventService:
    return EventService(repository)


@pytest.fixture
def db_event(
    db_session,
    event: Event,
) -> Event:
    db_session.add(event)
    db_session.flush()
    return event


@pytest.fixture
def db_events(
    db_session,
    events: list[Event],
) -> list[Event]:
    db_session.add_all(events)
    db_session.flush()
    return events


class TestEventService:
    def test_create_event(
        self,
        service: EventService,
        db_session,
    ):
        event_type = EventType.SOLAR_STORM
        title = "Solar Storm"
        description = "Solar activity increases battery consumption."
        turn = 5
        duration = 3

        result = service.create_event(
            event_type=event_type,
            title=title,
            description=description,
            turn=turn,
            duration=duration,
        )

        assert result.event_type == event_type
        assert result.title == title
        assert result.description == description
        assert result.start_turn == turn
        assert result.end_turn == turn + duration - 1

        db_session.expire_all()

        persisted_event = db_session.get(Event, result.id)

        assert persisted_event is not None
        assert persisted_event.event_type == event_type
        assert persisted_event.title == title
        assert persisted_event.description == description
        assert persisted_event.start_turn == turn
        assert persisted_event.end_turn == turn + duration - 1

    def test_create_random_event(
        self,
        service: EventService,
        db_session,
    ):
        event_type = EventType.METEOR_SHOWER
        turn = 10
        duration = 2

        with patch(
            "app.services.event_service.choice",
            return_value=event_type,
        ):
            result = service.create_random_event(
                turn=turn,
                duration=duration,
            )

        assert result.event_type == event_type
        assert result.title == "Meteor Shower"
        assert result.description == ("Meteor activity increases route risk.")
        assert result.start_turn == turn
        assert result.end_turn == turn + duration - 1

        db_session.expire_all()

        persisted_event = db_session.get(Event, result.id)

        assert persisted_event is not None
        assert persisted_event.event_type == event_type
        assert persisted_event.start_turn == turn
        assert persisted_event.end_turn == turn + duration - 1

    def test_create_random_event_with_default_duration(
        self,
        service: EventService,
    ):
        event_type = EventType.DUST_STORM
        turn = 10
        duration = 3

        with (
            patch(
                "app.services.event_service.choice",
                return_value=event_type,
            ),
            patch(
                "app.services.event_service.randint",
                return_value=duration,
            ),
        ):
            result = service.create_random_event(turn=turn)

        assert result.event_type == event_type
        assert result.title == "Dust Storm"
        assert result.description == ("A dust storm reduces rover speed.")
        assert result.start_turn == turn
        assert result.end_turn == turn + duration - 1

    def test_get_event(
        self,
        service: EventService,
        db_event: Event,
    ):
        event_id = db_event.id

        result = service.get_event(event_id)

        assert result is db_event

    def test_get_event_not_found(
        self,
        service: EventService,
    ):
        event_id = 999

        result = service.get_event(event_id)

        assert result is None

    def test_get_active_events(
        self,
        service: EventService,
        db_events: list[Event],
    ):
        turn = 2

        result = service.get_active_events(turn)

        expected_events = [
            event for event in db_events if event.start_turn <= turn <= event.end_turn
        ]

        assert result == expected_events

    def test_get_active_events_without_active_events(
        self,
        service: EventService,
        db_events: list[Event],
    ):
        turn = 999

        result = service.get_active_events(turn)

        assert result == []
