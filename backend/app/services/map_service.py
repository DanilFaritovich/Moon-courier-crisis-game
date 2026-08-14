from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.point import Point
from app.models.road import Road


class MapService:
    """Load map data from the database."""

    def __init__(self, db: Session):
        """Initialize the map service with a database session."""
        self.db = db

    def get_map(self) -> tuple[list[Point], list[Road]]:
        """Return all map points and roads from the database."""

        points = list(
            self.db.scalars(
                select(Point)
            ).all()
        )

        roads = list(
            self.db.scalars(
                select(Road)
            ).all()
        )

        return points, roads