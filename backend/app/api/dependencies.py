from typing import cast

from app.services.connector.delivery_connector_service import (
    DeliveryConnectorRepository,
)
from app.services.connector.event_connector_service import EventConnectorRepository
from app.services.connector.graph_connector_service import GraphConnector
from app.services.connector.order_connector_service import OrderConnector
from app.services.connector.rover_connector_service import RoverConnectorService
from app.services.connector.unit_of_work_connector import SQLAlchemyUnitOfWork
from app.services.delivery_service import DeliveryService
from app.services.event_service import EventService
from app.services.game_service import GameService
from app.services.graph_service import GraphService
from app.services.order_service import OrderService
from app.services.rover_service import RoverService
from fastapi import Request
from sqlalchemy.orm import Session


def build_game_service(db: Session) -> GameService:
    """Create the game service and all of its infrastructure dependencies."""

    return GameService(
        unit_of_work=SQLAlchemyUnitOfWork(db),
        graph_service=GraphService(GraphConnector(db)),
        rover_service=RoverService(RoverConnectorService(db)),
        order_service=OrderService(OrderConnector(db)),
        delivery_service=DeliveryService(DeliveryConnectorRepository(db)),
        event_service=EventService(EventConnectorRepository(db)),
    )


async def get_game_service(request: Request) -> GameService:
    """Return the single game instance created during application startup."""

    return cast(GameService, request.app.state.game_service)
