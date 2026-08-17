from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from app.db.base import Base
from app.models.delivery import Delivery
from app.models.event import Event, EventType
from app.models.order import Order, OrderStatus
from app.seeders.map_seeder import MapSeeder
from app.services.connector.graph_connector_service import GraphConnector
from app.services.graph_service import GraphService
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


@pytest.fixture
def db_session():
    """Provide an isolated in-memory database session."""

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(bind=engine)
    engine.dispose()

# ========================
# Delivery
# ========================

@pytest.fixture
def db_delivery(db_session, order, rover):
    delivery = Delivery(
        order_id=order.id,
        rover_id=rover.id,
    )

    db_session.add(delivery)
    db_session.commit()

    return delivery

@pytest.fixture
def db_deliveries(db_session, rover):
    orders = [
        Order(
            id=1,
            destination_point_id=1,
            weight=10.0,
            reward=50,
            status=OrderStatus.AVAILABLE,
        ),
        Order(
            id=2,
            destination_point_id=1,
            weight=20.0,
            reward=100,
            status=OrderStatus.AVAILABLE,
        ),
    ]
    deliveries = [
        Delivery(
            order_id=orders[0].id,
            rover_id=rover.id,
        ),
        Delivery(
            order_id=orders[1].id,
            rover_id=rover.id,
        ),
    ]

    db_session.add_all(deliveries)
    db_session.commit()

    return deliveries

# ========================
# Event
# ========================

@pytest.fixture
def event(db_session):
    event = Event(
        event_type=EventType.DUST_STORM,
        title="Dust Storm",
        description="A dust storm reduces rover speed.",
        start_turn=1,
        end_turn=3,
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    return event


@pytest.fixture
def events(db_session):
    now = datetime.now(timezone.utc)

    active_event = Event(
        event_type=EventType.DUST_STORM,
        title="Dust Storm",
        description="A dust storm reduces rover speed.",
        start_turn=2,
        end_turn=5,
    )

    expired_event = Event(
        event_type=EventType.SOLAR_STORM,
        title="Solar Storm",
        description="Solar activity increases battery consumption.",
        start_turn=1,
        end_turn=2
    )

    db_session.add_all([active_event, expired_event])
    db_session.commit()

    db_session.refresh(active_event)
    db_session.refresh(expired_event)

    return [active_event, expired_event]

# ========================
# Graph
# ========================

@pytest.fixture
def graph_service(
    db_session,
    seed_map,
):
    """Create a GraphService with the seeded map."""

    repository = GraphConnector(db_session)

    return GraphService(repository)

# ========================
# MapSeeder
# ========================

MAP_PATH = Path("data/map.json")

@pytest.fixture
def seed_map(db_session):
    """Seed the initial game map."""

    MapSeeder(
        session=db_session,
        map_path=Path("data/map.json"),
    ).seed()