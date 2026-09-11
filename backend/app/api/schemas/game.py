from uuid import UUID

from app.models.delivery import DeliveryStatus
from app.models.event import EventType
from app.models.order import OrderStatus, OrderUrgency
from app.models.rover import RoverStatus
from app.services.game_service import GameState
from pydantic import BaseModel, ConfigDict


class RoverResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    cargo_capacity: int
    cargo: int
    battery_capacity: int
    battery: int
    current_point_id: int
    status: RoverStatus


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    destination_point_id: int
    weight: int
    reward: int
    urgency: OrderUrgency
    status: OrderStatus


class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    rover_id: int
    status: DeliveryStatus
    started_turn: int
    completed_turn: int | None


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: EventType
    title: str
    description: str
    start_turn: int
    end_turn: int


class GameStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    game_id: UUID
    active_rovers: list[RoverResponse]
    active_orders: list[OrderResponse]
    active_deliveries: list[DeliveryResponse]
    active_events: list[EventResponse]
    turn: int
    money: int
    score: int

    @classmethod
    def from_game_state(cls, game_state: GameState) -> "GameStateResponse":
        return cls.model_validate(game_state)


class CreateDeliveryRequest(BaseModel):
    rover_id: int
    order_id: int
