from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from app.models.delivery import Delivery
from app.models.event import Event
from app.models.order import Order, OrderStatus, OrderUrgency
from app.models.rover import Rover, RoverStatus
from app.repositories.unit_of_work import UnitOfWork
from app.services.delivery_service import DeliveryService
from app.services.event_service import EventService
from app.services.game_service import GameService, GameState
from app.services.graph_service import GraphService, GraphState
from app.services.order_service import OrderService
from app.services.rover_service import RoverService


@pytest.fixture
def unit_of_work() -> Mock:
    return Mock(spec=UnitOfWork)


@pytest.fixture
def graph_service() -> Mock:
    return Mock(spec=GraphService)


@pytest.fixture
def rover_service() -> Mock:
    return Mock(spec=RoverService)


@pytest.fixture
def order_service() -> Mock:
    return Mock(spec=OrderService)


@pytest.fixture
def delivery_service() -> Mock:
    return Mock(spec=DeliveryService)


@pytest.fixture
def event_service() -> Mock:
    return Mock(spec=EventService)


@pytest.fixture
def service(
    unit_of_work: Mock,
    graph_service: Mock,
    rover_service: Mock,
    order_service: Mock,
    delivery_service: Mock,
    event_service: Mock,
) -> GameService:
    return GameService(
        unit_of_work=unit_of_work,
        graph_service=graph_service,
        rover_service=rover_service,
        order_service=order_service,
        delivery_service=delivery_service,
        event_service=event_service,
    )


@pytest.fixture
def graph_state() -> GraphState:
    return GraphState(graph=Mock())


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
def order() -> Order:
    return Order(
        id=1,
        destination_point_id=20,
        weight=10,
        reward=100,
        urgency=OrderUrgency.MEDIUM,
        status=OrderStatus.AVAILABLE,
    )


@pytest.fixture
def delivery() -> Delivery:
    return Delivery(
        id=1,
        order_id=1,
        rover_id=1,
        started_turn=1,
    )


@pytest.fixture
def game_state(graph_state: GraphState) -> GameState:
    return GameState(
        game_id=UUID("00000000-0000-0000-0000-000000000001"),
        graph_state=graph_state,
        turn=1,
        money=0,
        score=0,
    )


class TestGameService:
    def test_get_game_state(
        self,
        service: GameService,
        game_state: GameState,
    ) -> None:
        service.game_state = game_state

        result = service._get_game_state()

        assert result is game_state

    def test_get_game_state_before_initialization(
        self,
        service: GameService,
    ) -> None:
        with pytest.raises(
            RuntimeError,
            match="Game has not been initialized.",
        ):
            service._get_game_state()

    def test_initialize_game(
        self,
        service: GameService,
        graph_service: Mock,
        rover_service: Mock,
        order_service: Mock,
        delivery_service: Mock,
        event_service: Mock,
        graph_state: GraphState,
        rover: Rover,
        order: Order,
        delivery: Delivery,
    ) -> None:
        rovers = [rover]
        orders = [order]
        deliveries = [delivery]
        events = [Mock(spec=Event)]

        graph_service.build_graph.return_value = graph_state
        rover_service.get_available_rovers.return_value = rovers
        order_service.get_available_orders.return_value = orders
        delivery_service.get_active_deliveries.return_value = deliveries
        event_service.get_active_events.return_value = events

        result = service.initialize_game()

        assert result is service.game_state
        assert result.graph_state is graph_state
        assert result.active_rovers == rovers
        assert result.active_orders == orders
        assert result.active_deliveries == deliveries
        assert result.active_events == events
        assert result.turn == 1
        assert result.money == 0
        assert result.score == 0

        graph_service.build_graph.assert_called_once_with()
        rover_service.get_available_rovers.assert_called_once_with()
        order_service.get_available_orders.assert_called_once_with()
        delivery_service.get_active_deliveries.assert_called_once_with()
        event_service.get_active_events.assert_called_once_with(1)

    def test_create_delivery(
        self,
        service: GameService,
        unit_of_work: Mock,
        graph_service: Mock,
        rover_service: Mock,
        order_service: Mock,
        delivery_service: Mock,
        game_state: GameState,
        rover: Rover,
        order: Order,
    ) -> None:
        rover_id = rover.id
        order_id = order.id
        path = [rover.current_point_id, order.destination_point_id]
        distance = 15

        service.game_state = game_state
        game_state.active_rovers = [rover]

        rover_service.get_rover.return_value = rover
        order_service.get_order.return_value = order
        graph_service.find_path.return_value = path
        graph_service.get_path_distance.return_value = distance
        delivery_service.get_active_deliveries.return_value = [Mock()]
        rover_service.get_available_rovers.return_value = [rover]

        result = service.create_delivery(
            rover_id=rover_id,
            order_id=order_id,
        )

        assert result is game_state
        assert result.active_deliveries == delivery_service.get_active_deliveries()
        assert result.active_rovers == [rover]

        rover_service.get_rover.assert_called_once_with(rover_id)
        order_service.get_order.assert_called_once_with(order_id)

        delivery_service.create_delivery.assert_called_once_with(
            order_id=order_id,
            rover_id=rover_id,
            started_turn=game_state.turn,
        )
        order_service.assign_order.assert_called_once_with(order)

        graph_service.find_path.assert_called_once_with(
            start_point_id=rover.current_point_id,
            end_point_id=order.destination_point_id,
        )
        graph_service.get_path_distance.assert_called_once_with(
            path=path,
        )

        rover_service.move_rover.assert_called_once_with(
            rover=rover,
            point_id=order.destination_point_id,
            distance=distance,
            weight=order.weight,
        )

        unit_of_work.commit.assert_called_once_with()
        unit_of_work.rollback.assert_not_called()

    def test_create_delivery_rover_not_found(
        self,
        service: GameService,
        rover_service: Mock,
        order_service: Mock,
        unit_of_work: Mock,
        game_state: GameState,
    ) -> None:
        rover_id = 99
        order_id = 1

        service.game_state = game_state
        rover_service.get_rover.return_value = None

        with pytest.raises(
            RuntimeError,
            match=f"Rover {rover_id} not found.",
        ):
            service.create_delivery(
                rover_id=rover_id,
                order_id=order_id,
            )

        rover_service.get_rover.assert_called_once_with(rover_id)
        order_service.get_order.assert_not_called()
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_not_called()

    def test_create_delivery_rejects_busy_rover(
        self,
        service: GameService,
        rover_service: Mock,
        order_service: Mock,
        unit_of_work: Mock,
        game_state: GameState,
        rover: Rover,
    ) -> None:
        rover.status = RoverStatus.DELIVERING
        service.game_state = game_state
        rover_service.get_rover.return_value = rover

        with pytest.raises(
            RuntimeError,
            match=f"Rover {rover.id} is not available.",
        ):
            service.create_delivery(rover_id=rover.id, order_id=1)

        order_service.get_order.assert_not_called()
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_not_called()

    def test_create_delivery_order_not_found(
        self,
        service: GameService,
        rover_service: Mock,
        order_service: Mock,
        unit_of_work: Mock,
        game_state: GameState,
        rover: Rover,
    ) -> None:
        rover_id = rover.id
        order_id = 99

        service.game_state = game_state
        rover_service.get_rover.return_value = rover
        order_service.get_order.return_value = None

        with pytest.raises(
            RuntimeError,
            match=f"Order {order_id} not found.",
        ):
            service.create_delivery(
                rover_id=rover_id,
                order_id=order_id,
            )

        rover_service.get_rover.assert_called_once_with(rover_id)
        order_service.get_order.assert_called_once_with(order_id)
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_not_called()

    def test_create_delivery_rolls_back_on_error(
        self,
        service: GameService,
        unit_of_work: Mock,
        rover_service: Mock,
        order_service: Mock,
        delivery_service: Mock,
        game_state: GameState,
        rover: Rover,
        order: Order,
    ) -> None:
        rover_id = rover.id
        order_id = order.id

        service.game_state = game_state

        rover_service.get_rover.return_value = rover
        order_service.get_order.return_value = order
        delivery_service.create_delivery.side_effect = RuntimeError(
            "database error",
        )

        with pytest.raises(RuntimeError, match="database error"):
            service.create_delivery(
                rover_id=rover_id,
                order_id=order_id,
            )

        unit_of_work.rollback.assert_called_once_with()
        unit_of_work.commit.assert_not_called()

    def test_cancel_delivery(
        self,
        service: GameService,
        unit_of_work: Mock,
        graph_service: Mock,
        rover_service: Mock,
        order_service: Mock,
        delivery_service: Mock,
        game_state: GameState,
        rover: Rover,
        order: Order,
        delivery: Delivery,
    ) -> None:
        delivery_id = delivery.id
        base_point_id = 5
        distance = 15

        service.game_state = game_state
        game_state.active_rovers = [rover]

        delivery_service.get_delivery.return_value = delivery
        rover_service.get_rover.return_value = rover
        order_service.get_order.return_value = order
        graph_service.get_base.return_value = Mock(id=base_point_id)
        graph_service.get_distance_to_base.return_value = distance
        delivery_service.get_active_deliveries.return_value = []
        rover_service.get_available_rovers.return_value = [rover]

        result = service.cancel_delivery(delivery_id)

        assert result is game_state
        assert result.active_deliveries == []
        assert result.active_rovers == [rover]

        delivery_service.get_delivery.assert_called_once_with(delivery_id)
        rover_service.get_rover.assert_called_once_with(delivery.rover_id)
        order_service.get_order.assert_called_once_with(delivery.order_id)

        delivery_service.delete_delivery.assert_called_once_with(delivery_id)
        order_service.unassign_order.assert_called_once_with(order)

        graph_service.get_base.assert_called_once_with()
        graph_service.get_distance_to_base.assert_called_once_with(
            rover.current_point_id,
        )

        rover_service.move_rover_back.assert_called_once_with(
            rover,
            point_id=base_point_id,
            distance=distance,
            weight=order.weight,
        )

        unit_of_work.commit.assert_called_once_with()
        unit_of_work.rollback.assert_not_called()

    def test_cancel_delivery_not_found(
        self,
        service: GameService,
        delivery_service: Mock,
        unit_of_work: Mock,
        game_state: GameState,
    ) -> None:
        delivery_id = 99

        service.game_state = game_state
        delivery_service.get_delivery.return_value = None

        with pytest.raises(
            RuntimeError,
            match=f"Delivery {delivery_id} not found.",
        ):
            service.cancel_delivery(delivery_id)

        delivery_service.get_delivery.assert_called_once_with(delivery_id)
        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_not_called()

    def test_cancel_delivery_rover_not_found(
        self,
        service: GameService,
        delivery_service: Mock,
        rover_service: Mock,
        unit_of_work: Mock,
        game_state: GameState,
        delivery: Delivery,
    ) -> None:
        delivery_id = delivery.id

        service.game_state = game_state
        delivery_service.get_delivery.return_value = delivery
        rover_service.get_rover.return_value = None

        with pytest.raises(
            RuntimeError,
            match=f"Rover {delivery.rover_id} not found.",
        ):
            service.cancel_delivery(delivery_id)

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_not_called()

    def test_cancel_delivery_order_not_found(
        self,
        service: GameService,
        delivery_service: Mock,
        rover_service: Mock,
        order_service: Mock,
        unit_of_work: Mock,
        game_state: GameState,
        rover: Rover,
        delivery: Delivery,
    ) -> None:
        delivery_id = delivery.id

        service.game_state = game_state
        delivery_service.get_delivery.return_value = delivery
        rover_service.get_rover.return_value = rover
        order_service.get_order.return_value = None

        with pytest.raises(
            RuntimeError,
            match=f"Order {delivery.order_id} not found.",
        ):
            service.cancel_delivery(delivery_id)

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_not_called()

    def test_cancel_delivery_rolls_back_on_error(
        self,
        service: GameService,
        unit_of_work: Mock,
        delivery_service: Mock,
        rover_service: Mock,
        order_service: Mock,
        game_state: GameState,
        rover: Rover,
        order: Order,
        delivery: Delivery,
    ) -> None:
        delivery_id = delivery.id

        service.game_state = game_state

        delivery_service.get_delivery.return_value = delivery
        rover_service.get_rover.return_value = rover
        order_service.get_order.return_value = order
        delivery_service.delete_delivery.side_effect = RuntimeError(
            "database error",
        )

        with pytest.raises(RuntimeError, match="database error"):
            service.cancel_delivery(delivery_id)

        unit_of_work.rollback.assert_called_once_with()
        unit_of_work.commit.assert_not_called()

    def test_get_available_orders_by_rover(
        self,
        service: GameService,
        graph_service: Mock,
        rover_service: Mock,
        game_state: GameState,
        rover: Rover,
        order: Order,
    ) -> None:
        unavailable_order = Order(
            id=2,
            destination_point_id=30,
            weight=90,
            reward=200,
            urgency=OrderUrgency.HIGH,
            status=OrderStatus.AVAILABLE,
        )

        service.game_state = game_state
        game_state.active_orders = [order, unavailable_order]

        rover_service.get_rover.return_value = rover

        graph_service.find_path.side_effect = [
            [10, 20],
            [10, 30],
        ]
        graph_service.get_path_distance.side_effect = [5, 10]

        rover_service.get_battery_after_move.side_effect = [
            30,
            -20,
        ]
        rover_service.get_cargo_after_move.side_effect = [
            30,
            110,
        ]

        result = service.get_available_orders_by_rover(rover.id)

        assert result == [order]

        assert graph_service.find_path.call_count == 2
        assert graph_service.get_path_distance.call_count == 2
        assert rover_service.get_battery_after_move.call_count == 2
        assert rover_service.get_cargo_after_move.call_count == 2

    def test_get_available_orders_by_rover_skips_zero_distance(
        self,
        service: GameService,
        graph_service: Mock,
        rover_service: Mock,
        game_state: GameState,
        rover: Rover,
        order: Order,
    ) -> None:
        service.game_state = game_state
        game_state.active_orders = [order]

        rover_service.get_rover.return_value = rover
        graph_service.find_path.return_value = []
        graph_service.get_path_distance.return_value = 0

        result = service.get_available_orders_by_rover(rover.id)

        assert result == []

        rover_service.get_battery_after_move.assert_not_called()
        rover_service.get_cargo_after_move.assert_not_called()

    def test_get_available_orders_by_rover_rover_not_found(
        self,
        service: GameService,
        rover_service: Mock,
        game_state: GameState,
    ) -> None:
        rover_id = 99

        service.game_state = game_state
        rover_service.get_rover.return_value = None

        with pytest.raises(
            RuntimeError,
            match=f"Rover {rover_id} not found.",
        ):
            service.get_available_orders_by_rover(rover_id)

    def test_complete_deliveries(
        self,
        service: GameService,
        graph_service: Mock,
        rover_service: Mock,
        order_service: Mock,
        delivery_service: Mock,
        game_state: GameState,
        rover: Rover,
        order: Order,
        delivery: Delivery,
    ) -> None:
        base_point_id = 5
        distance = 15
        initial_money = game_state.money

        delivery_service.get_active_deliveries.return_value = [delivery]
        order_service.get_order.return_value = order
        rover_service.get_rover.return_value = rover
        graph_service.get_base.return_value = Mock(id=base_point_id)
        graph_service.get_distance_to_base.return_value = distance

        service._complete_deliveries(game_state)

        delivery_service.complete_delivery.assert_called_once_with(
            delivery,
        )
        order_service.get_order.assert_called_once_with(
            delivery.order_id,
        )
        order_service.complete_order.assert_called_once_with(order)

        assert game_state.money == initial_money + order.reward

        rover_service.get_rover.assert_called_once_with(
            delivery.rover_id,
        )
        graph_service.get_base.assert_called_once_with()
        graph_service.get_distance_to_base.assert_called_once_with(
            rover.current_point_id,
        )

        rover_service.move_rover_back.assert_called_once_with(
            rover,
            base_point_id,
            distance,
            order.weight,
        )

    def test_complete_deliveries_order_not_found(
        self,
        service: GameService,
        delivery_service: Mock,
        order_service: Mock,
        game_state: GameState,
        delivery: Delivery,
    ) -> None:
        delivery_service.get_active_deliveries.return_value = [delivery]
        order_service.get_order.return_value = None

        with pytest.raises(
            RuntimeError,
            match=f"Order {delivery.order_id} not found.",
        ):
            service._complete_deliveries(game_state)

    def test_complete_deliveries_rover_not_found(
        self,
        service: GameService,
        delivery_service: Mock,
        order_service: Mock,
        rover_service: Mock,
        game_state: GameState,
        delivery: Delivery,
        order: Order,
    ) -> None:
        delivery_service.get_active_deliveries.return_value = [delivery]
        order_service.get_order.return_value = order
        rover_service.get_rover.return_value = None

        with pytest.raises(
            RuntimeError,
            match=f"Rover {delivery.rover_id} not found.",
        ):
            service._complete_deliveries(game_state)

    def test_generate_events(
        self,
        service: GameService,
        event_service: Mock,
        game_state: GameState,
    ) -> None:
        service._generate_events(game_state)

        event_service.create_random_event.assert_called_once_with(
            turn=game_state.turn,
        )

    @patch("app.services.game_service.randint")
    def test_generate_orders(
        self,
        mock_randint: Mock,
        service: GameService,
        graph_service: Mock,
        rover_service: Mock,
        order_service: Mock,
        game_state: GameState,
        rover: Rover,
    ) -> None:
        points = [
            Mock(id=20),
            Mock(id=30),
            Mock(id=40),
        ]
        available_orders = [Mock()]
        available_rovers = [rover]
        add_orders = 2

        mock_randint.return_value = add_orders
        graph_service.get_unbase.return_value = points
        graph_service.get_base.return_value = Mock(id=10)
        graph_service.find_path.return_value = [10, 20]
        graph_service.get_path_distance.return_value = 10
        rover_service.get_rover_with_max_weight.return_value = rover
        order_service.get_available_orders.return_value = available_orders
        rover_service.get_available_rovers.return_value = available_rovers

        service._generate_orders(game_state)

        graph_service.get_unbase.assert_called_once_with()
        rover_service.get_rover_with_max_weight.assert_called_once_with()
        order_service.get_available_orders.assert_called_once_with()
        rover_service.get_available_rovers.assert_called_once_with()

        mock_randint.assert_any_call(1, 1)

        assert order_service.create_order.call_count == add_orders
        for call in order_service.create_order.call_args_list:
            assert call.kwargs["destination_point_id"] in {20, 30, 40}
            assert call.kwargs["weight"] == add_orders
            assert call.kwargs["reward"] == add_orders

    def test_generate_orders_does_not_create_when_enough_orders(
        self,
        service: GameService,
        graph_service: Mock,
        rover_service: Mock,
        order_service: Mock,
        game_state: GameState,
        rover: Rover,
    ) -> None:
        available_orders = [Mock(), Mock()]
        available_rovers = [rover]

        graph_service.get_unbase.return_value = []
        rover_service.get_rover_with_max_weight.return_value = rover
        order_service.get_available_orders.return_value = available_orders
        rover_service.get_available_rovers.return_value = available_rovers

        service._generate_orders(game_state)

        order_service.create_random_order.assert_not_called()

    def test_generate_orders_without_rovers(
        self,
        service: GameService,
        graph_service: Mock,
        rover_service: Mock,
        game_state: GameState,
    ) -> None:
        graph_service.get_unbase.return_value = []
        rover_service.get_rover_with_max_weight.return_value = None

        with pytest.raises(
            RuntimeError,
            match="No rovers found.",
        ):
            service._generate_orders(game_state)

    def test_refresh_game_state(
        self,
        service: GameService,
        rover_service: Mock,
        order_service: Mock,
        delivery_service: Mock,
        event_service: Mock,
        game_state: GameState,
        rover: Rover,
        order: Order,
        delivery: Delivery,
    ) -> None:
        rovers = [rover]
        orders = [order]
        deliveries = [delivery]
        events = [Mock(spec=Event)]

        rover_service.get_available_rovers.return_value = rovers
        order_service.get_available_orders.return_value = orders
        delivery_service.get_active_deliveries.return_value = deliveries
        event_service.get_active_events.return_value = events

        service._refresh_game_state(game_state)

        assert game_state.active_rovers == rovers
        assert game_state.active_orders == orders
        assert game_state.active_deliveries == deliveries
        assert game_state.active_events == events

        rover_service.get_available_rovers.assert_called_once_with()
        order_service.get_available_orders.assert_called_once_with()
        delivery_service.get_active_deliveries.assert_called_once_with()
        event_service.get_active_events.assert_called_once_with(
            game_state.turn,
        )

    def test_next_turn(
        self,
        service: GameService,
        unit_of_work: Mock,
        game_state: GameState,
    ) -> None:
        service.game_state = game_state

        with (
            patch.object(service, "_complete_deliveries") as complete_deliveries,
            patch.object(service, "_generate_events") as generate_events,
            patch.object(service, "_generate_orders") as generate_orders,
            patch.object(service, "_refresh_game_state") as refresh_game_state,
        ):
            result = service.next_turn()

        assert result is game_state
        assert game_state.turn == 2

        complete_deliveries.assert_called_once_with(game_state)
        generate_events.assert_called_once_with(game_state)
        generate_orders.assert_called_once_with(game_state)
        refresh_game_state.assert_called_once_with(game_state)

        unit_of_work.commit.assert_called_once_with()
        unit_of_work.rollback.assert_not_called()

    def test_next_turn_rolls_back_on_error(
        self,
        service: GameService,
        unit_of_work: Mock,
        game_state: GameState,
    ) -> None:
        service.game_state = game_state

        error = RuntimeError("turn error")

        with patch.object(
            service,
            "_complete_deliveries",
            side_effect=error,
        ):
            with pytest.raises(RuntimeError, match="turn error"):
                service.next_turn()

        assert game_state.turn == 2
        unit_of_work.rollback.assert_called_once_with()
        unit_of_work.commit.assert_not_called()

    @pytest.mark.parametrize(
        ("battery_after_move", "weight_after_move"),
        [
            (-1, 30),
            (10, 101),
        ],
    )
    def test_get_available_orders_by_rover_skips_unavailable_order(
        self,
        service: GameService,
        graph_service: Mock,
        rover_service: Mock,
        game_state: GameState,
        rover: Rover,
        order: Order,
        battery_after_move: int,
        weight_after_move: float,
    ) -> None:
        service.game_state = game_state
        game_state.active_orders = [order]

        rover_service.get_rover.return_value = rover
        graph_service.find_path.return_value = [10, 20]
        graph_service.get_path_distance.return_value = 10
        rover_service.get_battery_after_move.return_value = battery_after_move
        rover_service.get_cargo_after_move.return_value = weight_after_move

        result = service.get_available_orders_by_rover(rover.id)

        assert result == []
