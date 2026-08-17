from abc import ABC, abstractmethod

from app.models.point import Point
from app.models.road import Road


class GraphRepository(ABC):
    """Abstract repository for grpah data."""

    @abstractmethod
    def get_points(self) -> list[Point]:
        """Return all grpah points."""
        ...

    @abstractmethod
    def get_point_by_id(self, point_id: int) -> Point:
        """Return a graph point from the database by id."""
        ...

    @abstractmethod
    def get_base(self) -> Point:
        """Return a graph point from the database by id."""
        ...

    @abstractmethod
    def get_unbase(self) -> list[Point]:
        """Return all grpah points."""
        ...

    @abstractmethod
    def get_roads(self) -> list[Road]:
        """Return all grpah roads."""
        ...