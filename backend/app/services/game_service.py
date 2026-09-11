import logging
from dataclasses import dataclass, field
from random import randint
from uuid import UUID, uuid4

from app.models.delivery import Delivery
from app.models.event import Event
from app.models.order import Order
from app.models.rover import Rover
from app.repositories.unit_of_work import UnitOfWork
from app.services.delivery_service import DeliveryService
from app.services.event_service import EventService
from app.services.graph_service import GraphService, GraphState
from app.services.order_service import OrderService
from app.services.rover_service import RoverService


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
        unit_of_work: UnitOfWork,
        graph_service: GraphService,
        rover_service: RoverService,
        order_service: OrderService,
        delivery_service: DeliveryService,
        event_service: EventService,
        logger: logging.Logger | None = None,
    ):
        self.unit_of_work = unit_of_work
        self.graph_service = graph_service
        self.rover_service = rover_service
        self.order_service = order_service
        self.delivery_service = delivery_service
        self.event_service = event_service
        self.logger = logger if logger is not None else logging.getLogger(__name__)
        self.game_state: GameState | None = None

    def _get_game_state(self) -> GameState:
        """Return the current game state."""

        if self.game_state is None:
            raise RuntimeError("Game has not been initialized.")

        return self.game_state

    def initialize_game(self):
        """Initialize the game world."""

        graph_state = self.graph_service.build_graph()
        rovers = self.rover_service.get_available_rovers()
        orders = self.order_service.get_available_orders()
        deliveries = self.delivery_service.get_active_deliveries()

        game_state = GameState(
            game_id=uuid4(),
            graph_state=graph_state,
            active_rovers=rovers,
            active_orders=orders,
            active_deliveries=deliveries,
        )

        game_state.active_events = self.event_service.get_active_events(game_state.turn)

        self.game_state = game_state

        return game_state

    def create_delivery(self, rover_id: int, order_id: int) -> GameState:
        """Create a new delivery."""

        game_state = self._get_game_state()
        rover = self.rover_service.get_rover(rover_id)

        if rover is None:
            raise RuntimeError(f"Rover {rover_id} not found.")

        order = self.order_service.get_order(order_id)

        if order is None:
            raise RuntimeError(f"Order {order_id} not found.")

        try:
            self.delivery_service.create_delivery(
                order_id=order_id,
                rover_id=rover_id,
                started_turn=game_state.turn,
            )

            self.order_service.assign_order(order)

            path = self.graph_service.find_path(
                start_point_id=rover.current_point_id,
                end_point_id=order.destination_point_id,
            )
            distance = self.graph_service.get_path_distance(
                path=path,
            )

            self.rover_service.move_rover(
                rover=rover,
                point_id=order.destination_point_id,
                distance=distance,
                weight=order.weight,
            )

            game_state.active_deliveries = self.delivery_service.get_active_deliveries()
            game_state.active_rovers = self.rover_service.get_available_rovers()

            self.unit_of_work.commit()
        except Exception as e:
            self.unit_of_work.rollback()
            raise e

        return game_state

    def cancel_delivery(self, delivery_id: int) -> GameState:
        """Cancel a delivery."""

        game_state = self._get_game_state()
        delivery = self.delivery_service.get_delivery(delivery_id)

        if delivery is None:
            raise RuntimeError(f"Delivery {delivery_id} not found.")

        rover = self.rover_service.get_rover(delivery.rover_id)

        if rover is None:
            raise RuntimeError(f"Rover {delivery.rover_id} not found.")

        order = self.order_service.get_order(delivery.order_id)

        if order is None:
            raise RuntimeError(f"Order {delivery.order_id} not found.")

        try:
            self.delivery_service.delete_delivery(delivery_id)

            self.order_service.unassign_order(order)

            point_id = self.graph_service.get_base().id

            distance = self.graph_service.get_distance_to_base(
                rover.current_point_id,
            )

            self.rover_service.move_rover_back(
                rover,
                point_id=point_id,
                distance=distance,
                weight=order.weight,
            )

            game_state.active_deliveries = self.delivery_service.get_active_deliveries()
            game_state.active_rovers = self.rover_service.get_available_rovers()

            self.unit_of_work.commit()
        except Exception as e:
            self.unit_of_work.rollback()
            raise e

        return game_state

    def get_available_orders_by_rover(self, rover_id: int) -> list[Order]:
        """Return available orders for a rover."""

        game_state = self._get_game_state()
        rover = self.rover_service.get_rover(rover_id)

        if rover is None:
            raise RuntimeError(f"Rover {rover_id} not found.")

        available_orders = []

        for order in game_state.active_orders:
            path = self.graph_service.find_path(
                start_point_id=rover.current_point_id,
                end_point_id=order.destination_point_id,
            )
            distance = self.graph_service.get_path_distance(
                path=path,
            )
            if distance == 0:
                continue

            battery_after_move = self.rover_service.get_battery_after_move(
                rover=rover,
                distance=distance,
                weight=order.weight,
            )
            weight_after_move = self.rover_service.get_cargo_after_move(
                rover=rover,
                weight=order.weight,
            )
            if battery_after_move < 0 or weight_after_move > rover.cargo_capacity:
                continue

            available_orders.append(order)

        return available_orders

    def _complete_deliveries(self, game_state: GameState) -> None:
        active_deliveries = self.delivery_service.get_active_deliveries()
        for delivery in active_deliveries:
            self.delivery_service.complete_delivery(delivery)

            order = self.order_service.get_order(delivery.order_id)
            if order is None:
                raise RuntimeError(f"Order {delivery.order_id} not found.")

            self.order_service.complete_order(order)
            game_state.money += order.reward

            rover = self.rover_service.get_rover(delivery.rover_id)
            if rover is None:
                raise RuntimeError(f"Rover {delivery.rover_id} not found.")

            base_point_id = self.graph_service.get_base().id

            distance = self.graph_service.get_distance_to_base(rover.current_point_id)

            self.rover_service.move_rover_back(
                rover, base_point_id, distance, order.weight
            )

    def _generate_events(self, game_state: GameState) -> None:
        self.event_service.create_random_event(turn=game_state.turn)

    def _generate_orders(self, game_state: GameState) -> None:
        points_id = self.graph_service.get_unbase()
        rover = self.rover_service.get_rover_with_max_weight()
        if rover is None:
            raise RuntimeError("No rovers found.")
        max_weight_rover = rover.cargo_capacity

        available_orders = self.order_service.get_available_orders()
        available_rovers = self.rover_service.get_available_rovers()

        max_orders = len(available_rovers) * 2
        if len(available_orders) < max_orders:
            needed_orders = max_orders - len(available_orders)
            add_orders = randint(1, needed_orders)
            for _ in range(add_orders):
                self.order_service.create_random_order(
                    list(map(lambda x: x.id, points_id)), max_weight_rover
                )

    def _refresh_game_state(self, game_state: GameState) -> None:
        game_state.active_rovers = self.rover_service.get_available_rovers()
        game_state.active_orders = self.order_service.get_available_orders()
        game_state.active_deliveries = self.delivery_service.get_active_deliveries()
        game_state.active_events = self.event_service.get_active_events(
            game_state.turn,
        )

    def next_turn(self) -> GameState:
        """Advance the game turn."""

        game_state = self._get_game_state()

        try:
            game_state.turn += 1

            # Complete deliveries
            self._complete_deliveries(game_state)
            # Generate new events
            self._generate_events(game_state)
            # Generate new orders
            self._generate_orders(game_state)
            # Update game state
            self._refresh_game_state(game_state)

            self.unit_of_work.commit()
        except Exception as e:
            self.unit_of_work.rollback()
            raise e

        return game_state
