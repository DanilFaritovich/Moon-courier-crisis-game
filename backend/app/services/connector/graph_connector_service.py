from app.models.point import Point, PointType
from app.models.road import Road
from app.repositories.graph_connector_repository import GraphRepository
from sqlalchemy import select
from sqlalchemy.orm import Session


class GraphConnector(GraphRepository):
    """SQLAlchemy implementation of the graph_connector repository."""

    def __init__(self, db: Session):
        self.db = db

    def get_points(self) -> list[Point]:
        """Return all graph points from the database."""

        return list(self.db.scalars(select(Point)).all())

    def get_point_by_id(self, point_id: int) -> Point:
        """Return a graph point from the database by id."""

        return self.db.scalars(select(Point).where(Point.id == point_id)).one()

    def get_base(self) -> Point:
        return self.db.scalars(select(Point).where(Point.type == PointType.BASE)).one()

    def get_unbase(self) -> list[Point]:
        """Return all graph points from the database."""

        return list(
            self.db.scalars(select(Point).where(Point.type != PointType.BASE)).all()
        )

    def get_roads(self) -> list[Road]:
        """Return all graph roads from the database."""

        return list(self.db.scalars(select(Road)).all())
