from app.models.rover import Rover, RoverStatus
from app.repositories.rover_connector_repository import RoverConnectorRepository
from sqlalchemy import select
from sqlalchemy.orm import Session


class RoverConnectorService(RoverConnectorRepository):
    """SQLAlchemy implementation of the rover repository."""

    def __init__(self, db: Session):
        self.db = db

    def create_rover(self, rover: Rover) -> Rover:
        """Persist a new rover."""

        self.db.add(rover)
        self.db.commit()
        self.db.refresh(rover)

        return rover

    def get_rover(self, rover_id: int) -> Rover | None:
        """Return a rover by its identifier."""

        return self.db.get(Rover, rover_id)

    def get_rover_with_max_weight(self) -> Rover | None:
        """Return a rover with the highest weight capacity."""

        return self.db.scalars(
            select(Rover).order_by(Rover.cargo_capacity.desc())
        ).first()

    def get_available_rovers(self) -> list[Rover]:
        """Return all rovers ready for delivery."""

        return list(
            self.db.scalars(
                select(Rover).where(Rover.status == RoverStatus.IDLE)
            ).all()
        )

    def update_rover(self, rover: Rover) -> None:
        """Persist rover changes."""

        self.db.commit()
        self.db.refresh(rover)