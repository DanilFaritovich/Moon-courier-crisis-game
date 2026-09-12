"""Seed the initial rover fleet for a new game."""

from app.models.rover import Rover, RoverStatus
from sqlalchemy import select
from sqlalchemy.orm import Session


class RoverSeeder:
    """Create a small, deterministic starter fleet exactly once."""

    def __init__(self, session: Session, base_point_id: int) -> None:
        self.session = session
        self.base_point_id = base_point_id

    def seed(self) -> None:
        if self.session.scalar(select(Rover.id).limit(1)) is not None:
            return

        self.session.add_all(
            [
                Rover(
                    name="Artemis-1",
                    cargo_capacity=20,
                    cargo=0,
                    battery_capacity=100,
                    battery=100,
                    current_point_id=self.base_point_id,
                    status=RoverStatus.IDLE,
                ),
                Rover(
                    name="Artemis-2",
                    cargo_capacity=30,
                    cargo=0,
                    battery_capacity=100,
                    battery=100,
                    current_point_id=self.base_point_id,
                    status=RoverStatus.IDLE,
                ),
            ]
        )
        self.session.commit()
