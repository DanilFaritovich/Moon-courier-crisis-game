from unittest.mock import patch

import pytest
from app.models.delivery import Delivery, DeliveryStatus
from app.models.order import Order, OrderStatus
from app.models.point import Point
from app.models.rover import Rover
from app.services.connector.delivery_connector_service import (
    DeliveryConnectorRepository,
)
from app.services.connector.event_connector_service import (
    EventConnectorRepository,
)
from app.services.connector.graph_connector_service import GraphConnector
from app.services.connector.order_connector_service import OrderConnector
from app.services.connector.rover_connector_service import RoverConnectorService
from app.services.connector.unit_of_work_connector import (
    SQLAlchemyUnitOfWork,
)
from app.services.delivery_service import DeliveryService
from app.services.event_service import EventService
from app.services.game_service import GameService, GameState
from app.services.graph_service import GraphService
from app.services.order_service import OrderService
from app.services.rover_service import RoverService


@pytest.fixture
def unit_of_work(db_session):
    return SQLAlchemyUnitOfWork(db_session)


@pytest.fixture
def graph_repository(db_session):
    return GraphConnector(db_session)


@pytest.fixture
def rover_repository(db_session):
    return RoverConnectorService(db_session)


@pytest.fixture
def order_repository(db_session):
    return OrderConnector(db_session)


@pytest.fixture
def delivery_repository(db_session):
    return DeliveryConnectorRepository(db_session)


@pytest.fixture
def event_repository(db_session):
    return EventConnectorRepository(db_session)


@pytest.fixture
def graph_service(graph_repository):
    return GraphService(graph_repository)


@pytest.fixture
def rover_service(rover_repository):
    return RoverService(rover_repository)


@pytest.fixture
def order_service(order_repository):
    return OrderService(order_repository)


@pytest.fixture
def delivery_service(delivery_repository):
    return DeliveryService(delivery_repository)


@pytest.fixture
def event_service(event_repository):
    return EventService(event_repository)


@pytest.fixture
def service(
    unit_of_work,
    graph_service,
    rover_service,
    order_service,
    delivery_service,
    event_service,
):
    return GameService(
        unit_of_work=unit_of_work,
        graph_service=graph_service,
        rover_service=rover_service,
        order_service=order_service,
        delivery_service=delivery_service,
        event_service=event_service,
    )


@pytest.fixture
def db_game_map(
    db_session,
    points: list[Point],
    roads,
):
    db_session.add_all(points)
    db_session.flush()

    db_session.add_all(roads)
    db_session.flush()

    return points, roads


@pytest.fixture
def db_game_data(
    db_session,
    db_game_map,
    rovers: list[Rover],
    orders: list[Order],
):
    points, _ = db_game_map

    for rover in rovers:
        rover.current_point_id = points[0].id

    for order, point in zip(
        orders,
        points[1:],
        strict=False,
    ):
        order.destination_point_id = point.id

    db_session.add_all(rovers)
    db_session.add_all(orders)
    db_session.flush()

    return rovers, orders


class TestGameService:
    def test_initialize_game(
        self,
        service: GameService,
        db_game_map,
        db_game_data,
    ):
        points, roads = db_game_map
        rovers, orders = db_game_data

        result = service.initialize_game()

        assert isinstance(result, GameState)
        assert result is service.game_state

        assert result.turn == 1
        assert result.money == 0
        assert result.score == 0

        assert result.graph_state.graph.number_of_nodes() == len(points)
        assert result.graph_state.graph.number_of_edges() == len(roads)

        assert result.active_rovers == rovers
        assert result.active_orders == orders
        assert result.active_deliveries == []
        assert result.active_events == []

    def test_create_delivery(
        self,
        service: GameService,
        db_session,
        db_game_map,
        db_game_data,
    ):
        points, _ = db_game_map
        rovers, orders = db_game_data

        service.initialize_game()

        rover = rovers[0]
        order = orders[0]

        rover_id = rover.id
        order_id = order.id
        destination_point_id = order.destination_point_id

        initial_battery = rover.battery
        initial_cargo = rover.cargo
        weight = order.weight
        distance = 10

        result = service.create_delivery(
            rover_id=rover_id,
            order_id=order_id,
        )

        assert result is service.game_state

        delivery = db_session.query(Delivery).filter_by(order_id=order_id).one()

        assert delivery.rover_id == rover_id
        assert delivery.order_id == order_id
        assert delivery.started_turn == 1
        assert delivery.status == DeliveryStatus.IN_PROGRESS

        assert order.status == OrderStatus.ASSIGNED

        assert rover.current_point_id == destination_point_id
        assert rover.cargo == initial_cargo + weight
        assert rover.battery == (initial_battery - distance * (initial_cargo + weight))

    def test_cancel_delivery(
        self,
        service: GameService,
        db_session,
        db_game_map,
        db_game_data,
    ):
        points, _ = db_game_map
        rovers, orders = db_game_data

        service.initialize_game()

        rover = rovers[0]
        order = orders[0]

        rover_id = rover.id
        order_id = order.id

        initial_battery = rover.battery
        initial_cargo = rover.cargo

        service.create_delivery(
            rover_id=rover_id,
            order_id=order_id,
        )

        delivery = db_session.query(Delivery).filter_by(order_id=order_id).one()

        delivery_id = delivery.id

        service.cancel_delivery(delivery_id)

        deleted_delivery = db_session.get(
            Delivery,
            delivery_id,
        )

        assert deleted_delivery is None
        assert order.status == OrderStatus.AVAILABLE
        assert rover.current_point_id == points[0].id
        assert rover.cargo == initial_cargo
        assert rover.battery == initial_battery

    def test_next_turn(
        self,
        service: GameService,
        db_session,
        db_game_map,
        db_game_data,
    ):
        points, _ = db_game_map
        rovers, orders = db_game_data

        service.initialize_game()

        rover = rovers[0]
        order = orders[0]

        order_id = order.id
        reward = order.reward
        initial_cargo = rover.cargo

        service.create_delivery(
            rover_id=rover.id,
            order_id=order.id,
        )

        delivery = db_session.query(Delivery).filter_by(order_id=order_id).one()

        delivery_id = delivery.id
        started_turn = service.game_state.turn

        with patch(
            "app.services.game_service.randint",
            return_value=1,
        ):
            result = service.next_turn()

        assert result.turn == started_turn + 1

        assert order.status == OrderStatus.COMPLETED
        assert delivery.status == DeliveryStatus.COMPLETED
        assert result.money == reward

        assert rover.current_point_id == points[0].id
        assert rover.cargo == initial_cargo

        assert result.active_deliveries == []

        completed_delivery = db_session.get(
            Delivery,
            delivery_id,
        )

        assert completed_delivery is not None
        assert completed_delivery.status == DeliveryStatus.COMPLETED
