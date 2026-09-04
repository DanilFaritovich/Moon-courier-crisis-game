from unittest.mock import Mock, patch

import pytest
from app.models.event import Event, EventType
from app.repositories.event_connector_repository import EventRepository
from app.services.event_service import EventService


@pytest.fixture
def repository() -> Mock:
    return Mock(spec=EventRepository)


@pytest.fixture
def service(repository: Mock) -> EventService:
    return EventService(repository)


class TestEventServiceUnit:
    def test_create_event(
        self,
        service: EventService,
        repository: Mock,
        event: Event,
    ) -> None:
        repository.create_event.return_value = event

        start_turn = 10
        duration = 3
        end_turn = start_turn + duration - 1

        result = service.create_event(
            event_type=event.event_type,
            title=event.title,
            description=event.description,
            turn=start_turn,
            duration=duration,
        )

        assert result is event

        repository.create_event.assert_called_once()
        created_event = repository.create_event.call_args.args[0]

        assert isinstance(created_event, Event)
        assert created_event.event_type == event.event_type
        assert created_event.title == event.title
        assert created_event.description == event.description
        assert created_event.start_turn == start_turn
        assert created_event.end_turn == end_turn

    def test_create_random_event_with_duration(
        self,
        service: EventService,
        repository: Mock,
        event: Event,
    ) -> None:
        repository.create_event.return_value = event

        event_type = EventType.SOLAR_STORM
        start_turn = 10
        duration = 3
        end_turn = start_turn + duration - 1

        title = "Solar Storm"
        description = "Solar activity increases battery consumption."

        with patch(
            "app.services.event_service.choice",
            return_value=event_type,
        ):
            result = service.create_random_event(
                turn=start_turn,
                duration=duration,
            )

        assert result is event

        repository.create_event.assert_called_once()
        created_event = repository.create_event.call_args.args[0]

        assert created_event.event_type == event_type
        assert created_event.title == title
        assert created_event.description == description
        assert created_event.start_turn == start_turn
        assert created_event.end_turn == end_turn

    def test_create_random_event_without_duration(
        self,
        service: EventService,
        repository: Mock,
        event: Event,
    ) -> None:
        repository.create_event.return_value = event

        event_type = EventType.SOLAR_STORM
        start_turn = 10
        duration = 2
        end_turn = start_turn + duration - 1

        title = "Solar Storm"
        description = "Solar activity increases battery consumption."

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
            result = service.create_random_event(turn=start_turn)

        assert result is event

        repository.create_event.assert_called_once()
        created_event = repository.create_event.call_args.args[0]

        assert created_event.event_type == event_type
        assert created_event.title == title
        assert created_event.description == description
        assert created_event.start_turn == start_turn
        assert created_event.end_turn == end_turn

    @pytest.mark.parametrize(
        ("event_type", "title", "description"),
        [
            (
                EventType.SOLAR_STORM,
                "Solar Storm",
                "Solar activity increases battery consumption.",
            ),
            (
                EventType.METEOR_SHOWER,
                "Meteor Shower",
                "Meteor activity increases route risk.",
            ),
            (
                EventType.DUST_STORM,
                "Dust Storm",
                "A dust storm reduces rover speed.",
            ),
            (
                EventType.ROVER_MALFUNCTION,
                "Rover Malfunction",
                "A rover may lose additional battery.",
            ),
        ],
    )
    def test_create_random_event_types(
        self,
        service: EventService,
        repository: Mock,
        event_type: EventType,
        title: str,
        description: str,
    ) -> None:
        start_turn = 10
        duration = 1
        end_turn = start_turn + duration - 1

        repository.create_event.return_value = Event(
            event_type=event_type,
            title=title,
            description=description,
            start_turn=start_turn,
            end_turn=end_turn,
        )

        with patch(
            "app.services.event_service.choice",
            return_value=event_type,
        ):
            service.create_random_event(
                turn=start_turn,
                duration=duration,
            )

        repository.create_event.assert_called_once()
        created_event = repository.create_event.call_args.args[0]

        assert created_event.event_type == event_type
        assert created_event.title == title
        assert created_event.description == description
        assert created_event.start_turn == start_turn
        assert created_event.end_turn == end_turn

    def test_get_event(
        self,
        service: EventService,
        repository: Mock,
        event: Event,
    ) -> None:
        repository.get_event.return_value = event

        event_id = event.id

        result = service.get_event(event_id)

        assert result is event
        repository.get_event.assert_called_once_with(event_id)

    def test_get_active_events(
        self,
        service: EventService,
        repository: Mock,
        events: list[Event],
    ) -> None:
        turn = 10
        repository.get_active_events.return_value = events

        result = service.get_active_events(turn)

        assert result == events
        repository.get_active_events.assert_called_once_with(turn)
