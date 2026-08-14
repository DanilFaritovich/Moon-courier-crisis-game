from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.point import Point
from app.models.road import Road
from backend.app.repositories.graph_repository import GraphRepository

class GraphConnector(GraphRepository):
    """SQLAlchemy implementation of the map repository."""

    def __init__(self, db: Session):
        self.db = db

    def get_points(self) -> list[Point]:
        """Return all map points from the database."""

        return list(
            self.db.scalars(
                select(Point)
            ).all()
        )

    def get_roads(self) -> list[Road]:
        """Return all map roads from the database."""

        return list(
            self.db.scalars(
                select(Road)
            ).all()
        )