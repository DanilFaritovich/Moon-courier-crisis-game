from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.point import Point
from app.models.road import Road
from app.repositories.graph_connector_repository import GraphRepository

class GraphConnector(GraphRepository):
    """SQLAlchemy implementation of the graph_connector repository."""

    def __init__(self, db: Session):
        self.db = db

    def get_points(self) -> list[Point]:
        """Return all graph points from the database."""

        return list(
            self.db.scalars(
                select(Point)
            ).all()
        )

    def get_roads(self) -> list[Road]:
        """Return all graph roads from the database."""

        return list(
            self.db.scalars(
                select(Road)
            ).all()
        )