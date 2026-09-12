import httpx2
import pytest
from app.api.dependencies import build_game_service, get_game_service
from app.main import app
from app.models.delivery import Delivery
from app.models.order import Order
from app.models.point import Point
from app.models.rover import Rover
from app.services.game_service import GameService
from fastapi import routing

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def game_service(db_session) -> GameService:
    return build_game_service(db_session)


@pytest.fixture
def api_client(game_service: GameService, monkeypatch: pytest.MonkeyPatch):
    async def run_in_current_task(function, *args, **kwargs):
        return function(*args, **kwargs)

    monkeypatch.setattr(routing, "run_in_threadpool", run_in_current_task)

    async def get_test_game_service() -> GameService:
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


@pytest.fixture
def game_data(
    db_session,
    points: list[Point],
    roads,
    rovers: list[Rover],
    orders: list[Order],
):
    for rover in rovers:
        rover.current_point_id = points[0].id

    for order, point in zip(orders, points[1:], strict=False):
        order.destination_point_id = point.id

    db_session.add_all(points)
    db_session.add_all(roads)
    db_session.add_all(rovers)
    db_session.add_all(orders)
    db_session.flush()

    return rovers, orders


class TestGameApi:
    async def test_initialize_game_uses_real_game_service(
        self,
        api_client,
        game_data,
    ) -> None:
        response = await api_client("POST", "/game/initialize")

        assert response.status_code == 200
        body = response.json()
        assert body["turn"] == 1
        assert body["money"] == 0
        assert len(body["active_rovers"]) == 2
        assert len(body["active_orders"]) == 2
        assert body["active_deliveries"] == []

    async def test_create_delivery_persists_through_api(
        self,
        api_client,
        game_data,
        db_session,
    ) -> None:
        rovers, orders = game_data

        initialize_response = await api_client("POST", "/game/initialize")
        assert initialize_response.status_code == 200

        response = await api_client(
            "POST",
            "/game/deliveries",
            json={"rover_id": rovers[0].id, "order_id": orders[0].id},
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["active_deliveries"]) == 1
        assert body["active_deliveries"][0]["rover_id"] == rovers[0].id
        assert body["active_deliveries"][0]["order_id"] == orders[0].id

        delivery = db_session.query(Delivery).one()
        assert delivery.rover_id == rovers[0].id
        assert delivery.order_id == orders[0].id
