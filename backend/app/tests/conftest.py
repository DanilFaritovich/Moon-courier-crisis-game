import networkx as nx
import pytest
from app.models.delivery import Delivery
from app.models.event import Event, EventType
from app.models.order import Order, OrderStatus, OrderUrgency
from app.models.point import Point, PointType
from app.models.road import Road
from app.models.rover import Rover, RoverStatus

# ========================
# Delivery
# ========================


@pytest.fixture
def delivery() -> Delivery:
    return Delivery(
        id=1,
        order_id=1,
        rover_id=2,
        started_turn=10,
    )


@pytest.fixture
def deliveries() -> list[Delivery]:
    return [
        Delivery(order_id=1, rover_id=2, started_turn=10),
        Delivery(order_id=3, rover_id=4, started_turn=20),
    ]


# ========================
# Events
# ========================


@pytest.fixture
def event() -> Event:
    return Event(
        event_type=EventType.SOLAR_STORM,
        title="Solar Storm",
        description="Solar activity increases battery consumption.",
        start_turn=10,
        end_turn=12,
    )


@pytest.fixture
def events() -> list[Event]:
    return [
        Event(
            event_type=EventType.SOLAR_STORM,
            title="Solar Storm",
            description="Solar activity increases battery consumption.",
            start_turn=10,
            end_turn=12,
        ),
        Event(
            event_type=EventType.METEOR_SHOWER,
            title="Meteor Shower",
            description="Meteor activity increases route risk.",
            start_turn=11,
            end_turn=13,
        ),
    ]


# ========================
# Graph
# ========================


@pytest.fixture
def points() -> list[Point]:
    return [
        Point(
            id=1,
            name="Base",
            type=PointType.BASE,
            x=0,
            y=0,
        ),
        Point(
            id=2,
            name="Point A",
            type=PointType.ROUTE,
            x=10,
            y=10,
        ),
        Point(
            id=3,
            name="Point B",
            type=PointType.DELIVERY,
            x=20,
            y=20,
        ),
    ]


@pytest.fixture
def base_point() -> Point:
    return Point(
        id=1,
        name="Base",
        type=PointType.BASE,
        x=0,
        y=0,
    )


@pytest.fixture
def roads() -> list[Road]:
    return [
        Road(
            from_point_id=1,
            to_point_id=2,
            distance=10,
            risk=0.1,
            speed_modifier=1.0,
        ),
        Road(
            from_point_id=2,
            to_point_id=3,
            distance=20,
            risk=0.2,
            speed_modifier=0.8,
        ),
    ]


@pytest.fixture
def graph() -> nx.Graph:
    graph = nx.Graph()

    graph.add_edge(
        1,
        2,
        distance=10,
        risk=0.1,
        speed_modifier=1.0,
    )
    graph.add_edge(
        2,
        3,
        distance=20,
        risk=0.2,
        speed_modifier=0.8,
    )

    return graph


# ========================
# Orders
# ========================


@pytest.fixture
def order() -> Order:
    return Order(
        id=1,
        destination_point_id=10,
        weight=5,
        reward=80,
        urgency=OrderUrgency.MEDIUM,
        status=OrderStatus.AVAILABLE,
    )


@pytest.fixture
def orders() -> list[Order]:
    return [
        Order(
            id=1,
            destination_point_id=10,
            weight=5,
            reward=80,
            urgency=OrderUrgency.MEDIUM,
            status=OrderStatus.AVAILABLE,
        ),
        Order(
            id=2,
            destination_point_id=20,
            weight=8,
            reward=100,
            urgency=OrderUrgency.HIGH,
            status=OrderStatus.AVAILABLE,
        ),
    ]


@pytest.fixture
def orders_by_status() -> list[Order]:
    return [
        Order(
            id=1,
            destination_point_id=10,
            weight=5,
            reward=80,
            urgency=OrderUrgency.MEDIUM,
            status=OrderStatus.AVAILABLE,
        ),
        Order(
            id=2,
            destination_point_id=20,
            weight=8,
            reward=100,
            urgency=OrderUrgency.HIGH,
            status=OrderStatus.ASSIGNED,
        ),
        Order(
            id=3,
            destination_point_id=30,
            weight=12,
            reward=150,
            urgency=OrderUrgency.LOW,
            status=OrderStatus.COMPLETED,
        ),
    ]


# ========================
# Rovers
# ========================


@pytest.fixture
def rover() -> Rover:
    return Rover(
        id=1,
        name="Rover-1",
        cargo_capacity=100.0,
        cargo=20.0,
        battery_capacity=100,
        battery=80,
        current_point_id=10,
        status=RoverStatus.IDLE,
    )


@pytest.fixture
def rovers() -> list[Rover]:
    return [
        Rover(
            id=1,
            name="Rover-1",
            cargo_capacity=100.0,
            cargo=20.0,
            battery_capacity=100,
            battery=80,
            current_point_id=10,
            status=RoverStatus.IDLE,
        ),
        Rover(
            id=2,
            name="Rover-2",
            cargo_capacity=150.0,
            cargo=50.0,
            battery_capacity=120,
            battery=90,
            current_point_id=20,
            status=RoverStatus.IDLE,
        ),
    ]
