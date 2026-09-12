import logging
from collections.abc import Callable
from typing import Annotated, TypeVar

from app.api.dependencies import get_game_service
from app.api.schemas.game import (
    CreateDeliveryRequest,
    GameStateResponse,
    OrderResponse,
    AvailableOrderResponse,
)
from app.schemas.map import MapData
from app.services.game_service import GameService
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/game", tags=["game"])

Result = TypeVar("Result")
logger = logging.getLogger(__name__)


def _execute_game_action(action: Callable[[], Result]) -> Result:
    """Translate known domain errors into HTTP responses."""

    try:
        return action()
    except RuntimeError as error:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in str(error)
            else status.HTTP_409_CONFLICT
        )
        logger.warning(
            "Game action rejected status=%s detail=%s",
            status_code,
            error,
        )
        raise HTTPException(status_code=status_code, detail=str(error)) from error


@router.post("/initialize", response_model=GameStateResponse)
def initialize_game(
    game_service: Annotated[GameService, Depends(get_game_service)],
) -> GameStateResponse:
    game_state = _execute_game_action(game_service.initialize_game)
    return GameStateResponse.from_game_state(game_state)


@router.get("/state", response_model=GameStateResponse)
def get_game_state(
    game_service: Annotated[GameService, Depends(get_game_service)],
) -> GameStateResponse:
    game_state = _execute_game_action(game_service._get_game_state)
    return GameStateResponse.from_game_state(game_state)


@router.get("/map", response_model=MapData)
def get_map(
    game_service: Annotated[GameService, Depends(get_game_service)],
) -> MapData:
    return _execute_game_action(game_service.get_map)


@router.post("/deliveries", response_model=GameStateResponse)
def create_delivery(
    payload: CreateDeliveryRequest,
    game_service: Annotated[GameService, Depends(get_game_service)],
) -> GameStateResponse:
    game_state = _execute_game_action(
        lambda: game_service.create_delivery(
            rover_id=payload.rover_id,
            order_id=payload.order_id,
        )
    )
    return GameStateResponse.from_game_state(game_state)


@router.delete("/deliveries/{delivery_id}", response_model=GameStateResponse)
def cancel_delivery(
    delivery_id: int,
    game_service: Annotated[GameService, Depends(get_game_service)],
) -> GameStateResponse:
    game_state = _execute_game_action(
        lambda: game_service.cancel_delivery(delivery_id),
    )
    return GameStateResponse.from_game_state(game_state)


@router.get("/rovers/{rover_id}/available-orders", response_model=list[AvailableOrderResponse])
def get_available_orders_by_rover(
    rover_id: int,
    game_service: Annotated[GameService, Depends(get_game_service)],
) -> list[AvailableOrderResponse]:
    previews = _execute_game_action(
        lambda: game_service.get_available_order_previews(rover_id),
    )
    rover = game_service.rover_service.get_rover(rover_id)
    assert rover is not None
    return [AvailableOrderResponse.model_validate({**OrderResponse.model_validate(order).model_dump(), "distance": distance, "battery_before": rover.battery, "battery_after": battery_after}) for order, distance, battery_after in previews]


@router.post("/next-turn", response_model=GameStateResponse)
def next_turn(
    game_service: Annotated[GameService, Depends(get_game_service)],
) -> GameStateResponse:
    game_state = _execute_game_action(game_service.next_turn)
    return GameStateResponse.from_game_state(game_state)
