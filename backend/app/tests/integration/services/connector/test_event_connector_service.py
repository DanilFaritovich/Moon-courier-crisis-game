import pytest
from app.models.event import Event
from app.services.connector.event_connector_service import (
    EventConnectorRepository,
)


@pytest.fixture
def repository(
    db_session,
) -> EventConnectorRepository:
    return EventConnectorRepository(db_session)


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


class TestEventConnectorRepository:
    def test_create_event(
        self,
        repository: EventConnectorRepository,
        event: Event,
    ):
        result = repository.create_event(event)

        assert result is event
        assert result.id is not None

        assert result.event_type == event.event_type
        assert result.title == event.title
        assert result.description == event.description
        assert result.start_turn == event.start_turn
        assert result.end_turn == event.end_turn

    def test_get_event(
        self,
        repository: EventConnectorRepository,
        db_event: Event,
    ):
        event_id = db_event.id

        result = repository.get_event(event_id)

        assert result is db_event

    def test_get_event_not_found(
        self,
        repository: EventConnectorRepository,
    ):
        event_id = 999

        result = repository.get_event(event_id)

        assert result is None

    def test_get_active_events_at_start_turn(
        self,
        repository: EventConnectorRepository,
        db_events: list[Event],
    ):
        turn = 10

        for event in db_events:
            print(
                event.id,
                event.start_turn,
                event.end_turn,
            )

        result = repository.get_active_events(turn)

        print(result)

        assert result == [db_events[0]]

    def test_get_active_events_in_range(
        self,
        repository: EventConnectorRepository,
        db_events: list[Event],
    ):
        turn = 11

        result = repository.get_active_events(turn)

        assert result == db_events

    def test_get_active_events_at_end_turn(
        self,
        repository: EventConnectorRepository,
        db_events: list[Event],
    ):
        turn = 12

        result = repository.get_active_events(turn)

        assert result == db_events

    def test_get_active_events_before_start(
        self,
        repository: EventConnectorRepository,
        db_events: list[Event],
    ):
        turn = 9

        result = repository.get_active_events(turn)

        assert result == []

    def test_get_active_events_after_end(
        self,
        repository: EventConnectorRepository,
        db_events: list[Event],
    ):
        turn = 14

        result = repository.get_active_events(turn)

        assert result == []

    def test_update_event(
        self,
        repository: EventConnectorRepository,
        db_event: Event,
    ):
        title = "Updated Solar Storm"
        description = "Updated description."
        end_turn = 15

        db_event.title = title
        db_event.description = description
        db_event.end_turn = end_turn

        result = repository.update_event(db_event)

        assert result is db_event
        assert result.title == title
        assert result.description == description
        assert result.end_turn == end_turn

        persisted_event = repository.get_event(db_event.id)

        assert persisted_event is db_event
        assert persisted_event.title == title
        assert persisted_event.description == description
        assert persisted_event.end_turn == end_turn
