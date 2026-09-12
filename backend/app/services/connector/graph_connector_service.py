import logging

from app.models.point import Point, PointType
from app.models.road import Road
from app.repositories.graph_connector_repository import GraphRepository
from sqlalchemy import select
from sqlalchemy.orm import Session


class GraphConnector(GraphRepository):
    """SQLAlchemy implementation of the graph_connector repository."""

    def __init__(self, db: Session, logger: logging.Logger | None = None):
        self.db = db
        self.logger = logger if logger is not None else logging.getLogger(__name__)

    def get_points(self) -> list[Point]:
        """Return all graph points from the database."""

        self.logger.debug("Loading graph points")
        return list(self.db.scalars(select(Point)).all())

    def get_point_by_id(self, point_id: int) -> Point:
        """Return a graph point from the database by id."""

        self.logger.debug("Loading graph point id=%s", point_id)
        return self.db.scalars(select(Point).where(Point.id == point_id)).one()

    def get_base(self) -> Point:
        self.logger.debug("Loading base point")
        return self.db.scalars(select(Point).where(Point.type == PointType.BASE)).one()

    def get_unbase(self) -> list[Point]:
        """Return all graph points from the database."""

        self.logger.debug("Loading non-base graph points")
        return list(
            self.db.scalars(select(Point).where(Point.type != PointType.BASE)).all()
        )

    def get_roads(self) -> list[Road]:
        """Return all graph roads from the database."""

        self.logger.debug("Loading graph roads")
        return list(self.db.scalars(select(Road)).all())
