
from app.models.event import Event, EventType
from app.services.event_service import EventService


class TestEventService:
    def test_create_event(self, event_repository):
        """Create an event and pass it to the repository."""

        event_repository.create_event.side_effect = lambda event: event

        service = EventService(event_repository)

        turn = 1
        duration = 3

        event = service.create_event(
            event_type=EventType.DUST_STORM,
            title="Dust Storm",
            description="A dust storm reduces rover speed.",
            turn=turn,
            duration=duration,
        )

        assert isinstance(event, Event)
        assert event.event_type == EventType.DUST_STORM
        assert event.title == "Dust Storm"
        assert event.description == "A dust storm reduces rover speed."
        assert event.end_turn == turn + duration - 1

        event_repository.create_event.assert_called_once_with(event)

    def test_create_random_event(self, event_repository):
        """Create a random game event."""

        event_repository.create_event.side_effect = lambda event: event

        service = EventService(event_repository)

        turn = 1
        duration = 3

        event = service.create_random_event(
            turn=turn,
            duration=duration,
        )

        assert isinstance(event, Event)
        assert event.event_type in EventType
        assert event.title
        assert event.description

        event_repository.create_event.assert_called_once_with(event)

    def test_get_event(
        self,
        event_repository,
        event,
    ):
        """Return an event from the repository."""

        event_repository.get_event.return_value = event

        service = EventService(event_repository)

        result = service.get_event(event.id)

        assert result is event

        event_repository.get_event.assert_called_once_with(
            event.id,
        )

    def test_get_event_not_found(self, event_repository):
        """Return None when the event does not exist."""

        event_repository.get_event.return_value = None

        service = EventService(event_repository)

        result = service.get_event(999)

        assert result is None

        event_repository.get_event.assert_called_once_with(999)

    def test_get_active_events(
        self,
        event_repository,
        events,
    ):
        """Return active events from the repository."""

        event_repository.get_active_events.return_value = events

        service = EventService(event_repository)

        turn = 1

        result = service.get_active_events(turn=turn)

        assert result == events

        event_repository.get_active_events.assert_called_once_with(turn)