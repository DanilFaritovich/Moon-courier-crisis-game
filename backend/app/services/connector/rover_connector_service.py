import logging

from app.models.rover import Rover, RoverStatus
from app.repositories.rover_connector_repository import RoverConnectorRepository
from sqlalchemy import select
from sqlalchemy.orm import Session


class RoverConnectorService(RoverConnectorRepository):
    """SQLAlchemy implementation of the rover repository."""

    def __init__(self, db: Session, logger: logging.Logger | None = None):
        self.db = db
        self.logger = logger if logger is not None else logging.getLogger(__name__)

    def create_rover(self, rover: Rover) -> Rover:
        """Persist a new rover."""

        self.db.add(rover)
        self.db.flush()
        self.logger.debug("Persisted rover id=%s", rover.id)

        return rover

    def get_rover(self, rover_id: int) -> Rover | None:
        """Return a rover by its identifier."""

        self.logger.debug("Loading rover id=%s", rover_id)
        return self.db.get(Rover, rover_id)

    def get_rover_with_max_weight(self) -> Rover | None:
        """Return a rover with the highest weight capacity."""

        self.logger.debug("Loading rover with maximum cargo capacity")
        return self.db.scalars(
            select(Rover).order_by(Rover.cargo_capacity.desc())
        ).first()

    def get_available_rovers(self) -> list[Rover]:
        """Return all rovers ready for delivery."""

        self.logger.debug("Loading available rovers")
        return list(
            self.db.scalars(select(Rover).where(Rover.status == RoverStatus.IDLE)).all()
        )

    def update_rover(self, rover: Rover) -> Rover:
        """Persist rover changes."""

        self.db.flush()
        self.logger.debug("Updated persisted rover id=%s", rover.id)

        return rover
