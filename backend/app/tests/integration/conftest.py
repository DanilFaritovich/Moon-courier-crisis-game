import pytest
from app.db.base import Base
from app.models.delivery import Delivery
from app.models.order import Order, OrderStatus
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