from unittest.mock import Mock
from uuid import UUID

import httpx2
import pytest
from app.api.dependencies import get_game_service
from app.main import app
from app.models.order import Order
from app.models.rover import Rover
from app.services.game_service import GameService, GameState
from app.services.graph_service import GraphState

pytestmark = pytest.mark.anyio


@pytest.fixture
def game_service() -> Mock:
    return Mock(spec=GameService)


@pytest.fixture
def game_state(rover: Rover, order: Order) -> GameState:
    return GameState(
        game_id=UUID("00000000-0000-0000-0000-000000000001"),
        graph_state=GraphState(graph=Mock()),
        active_rovers=[rover],
        active_orders=[order],
    )


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def api_client(game_service: Mock, monkeypatch: pytest.MonkeyPatch):
    async def run_in_current_task(function, *args, **kwargs):
        return function(*args, **kwargs)

    monkeypatch.setattr(
        "fastapi.routing.run_in_threadpool",
        run_in_current_task,
    )

    async def get_test_game_service() -> Mock:
        return game_service

    app.dependency_overrides[get_game_service] = get_test_game_service

    async def send(method: str, url: str, **kwargs):
        transport = httpx2.ASGITransport(app=app)
        async with httpx2.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.request(method, url, **kwargs)

    yield send

    app.dependency_overrides.clear()


class TestGameApi:
    async def test_health_check(self, api_client) -> None:
        response = await api_client("GET", "/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    async def test_health_check_logs_request_completion(
        self,
        api_client,
        caplog,
    ) -> None:
        with caplog.at_level("INFO"):
            response = await api_client("GET", "/health")

        assert response.status_code == 200
        assert "Request completed method=GET path=/health status=200" in caplog.text

    async def test_initialize_game_returns_serialized_state(
        self,
        api_client,
        game_service: Mock,
        game_state: GameState,
    ) -> None:
        game_service.initialize_game.return_value = game_state

        response = await api_client("POST", "/game/initialize")

        assert response.status_code == 200
        assert response.json() == {
            "game_id": "00000000-0000-0000-0000-000000000001",
            "active_rovers": [
                {
                    "id": 1,
                    "name": "Rover-1",
                    "cargo_capacity": 100,
                    "cargo": 20,
                    "battery_capacity": 100,
                    "battery": 80,
                    "current_point_id": 10,
                    "status": "idle",
                }
            ],
            "active_orders": [
                {
                    "id": 1,
                    "destination_point_id": 10,
                    "weight": 5,
                    "reward": 80,
                    "urgency": "medium",
                    "status": "available",
                }
            ],
            "active_deliveries": [],
            "active_events": [],
            "turn": 1,
            "money": 0,
            "score": 0,
        }
        game_service.initialize_game.assert_called_once_with()

    async def test_get_game_state_before_initialization_returns_conflict(
        self,
        api_client,
        game_service: Mock,
        caplog,
    ) -> None:
        game_service._get_game_state.side_effect = RuntimeError(
            "Game has not been initialized."
        )

        response = await api_client("GET", "/game/state")

        assert response.status_code == 409
        assert response.json() == {"detail": "Game has not been initialized."}
        assert "Game action rejected status=409" in caplog.text

    async def test_create_delivery_calls_game_service(
        self,
        api_client,
        game_service: Mock,
        game_state: GameState,
    ) -> None:
        game_service.create_delivery.return_value = game_state

        response = await api_client(
            "POST",
            "/game/deliveries",
            json={"rover_id": 1, "order_id": 2},
        )

        assert response.status_code == 200
        game_service.create_delivery.assert_called_once_with(rover_id=1, order_id=2)

    async def test_create_delivery_with_missing_rover_returns_not_found(
        self,
        api_client,
        game_service: Mock,
    ) -> None:
        game_service.create_delivery.side_effect = RuntimeError("Rover 99 not found.")

        response = await api_client(
            "POST",
            "/game/deliveries",
            json={"rover_id": 99, "order_id": 1},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "Rover 99 not found."}

    async def test_cancel_delivery_calls_game_service(
        self,
        api_client,
        game_service: Mock,
        game_state: GameState,
    ) -> None:
        game_service.cancel_delivery.return_value = game_state

        response = await api_client("DELETE", "/game/deliveries/3")

        assert response.status_code == 200
        game_service.cancel_delivery.assert_called_once_with(3)

    async def test_get_available_orders_by_rover_returns_serialized_orders(
        self,
        api_client,
        game_service: Mock,
        order: Order,
    ) -> None:
        game_service.get_available_order_previews.return_value = [(order, 12, 65)]
        game_service.rover_service = Mock()
        game_service.rover_service.get_rover.return_value = Rover(
            id=1,
            name="Rover-1",
            cargo_capacity=100,
            cargo=20,
            battery_capacity=100,
            battery=80,
            current_point_id=10,
        )

        response = await api_client("GET", "/game/rovers/1/available-orders")

        assert response.status_code == 200
        assert response.json()[0]["id"] == order.id
        assert response.json()[0]["status"] == "available"
        assert response.json()[0]["distance"] == 12
        assert response.json()[0]["battery_before"] == 80
        assert response.json()[0]["battery_after"] == 65
        game_service.get_available_order_previews.assert_called_once_with(1)

    async def test_next_turn_calls_game_service(
        self,
        api_client,
        game_service: Mock,
        game_state: GameState,
    ) -> None:
        game_service.next_turn.return_value = game_state

        response = await api_client("POST", "/game/next-turn")

        assert response.status_code == 200
        game_service.next_turn.assert_called_once_with()
