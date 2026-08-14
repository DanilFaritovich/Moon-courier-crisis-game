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
    def get_roads(self) -> list[Road]:
        """Return all grpah roads."""
        ...