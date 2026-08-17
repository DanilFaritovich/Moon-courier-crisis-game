
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from app.services.graph_service import GraphService, GraphState
from app.models.delivery import Delivery
from app.models.order import Order
from app.models.rover import Rover
from app.models.event import Event
from app.services.rover_service import RoverService
from app.services.order_service import OrderService
from app.services.delivery_service import DeliveryService
from app.services.event_service import EventService

@dataclass
class GameState:
    game_id: UUID
    graph_state: GraphState

    active_rovers: list[Rover] = field(default_factory=list)
    active_orders: list[Order] = field(default_factory=list)
    active_deliveries: list[Delivery] = field(default_factory=list)
    active_events: list[Event] = field(default_factory=list)

    turn: int = 1
    money: int = 0
    score: int = 0

class GameService:
    """Manage game initialization."""

    def __init__(
        self,
        graph_service: GraphService,
        rover_service: RoverService,
        order_service: OrderService,
        delivery_service: DeliveryService,
        event_service: EventService,
    ):
        self.graph_service = graph_service
        self.rover_service = rover_service
        self.order_service = order_service
        self.delivery_service = delivery_service
        self.event_service = event_service
        self.game_state: GameState | None = None

    def initialize_game(self):
        """Initialize the game world."""

        graph_state = self.graph_service.build_graph()
        rovers = self.rover_service.get_available_rovers()
        orders = self.order_service.get_available_orders()
        deliveries = self.delivery_service.get_active_deliveries()
        active_events = self.event_service.get_active_events(turn=GameState.turn)

        game_state = GameState(
            game_id=uuid4(),
            graph_state=graph_state,
            active_rovers=rovers,
            active_orders=orders,
            active_deliveries=deliveries,
            active_events=active_events,
        )

        self.game_state = game_state

        # return GameState(game_id=uuid4(), graph_state=graph_state)