import json
from pathlib import Path

from app.models.point import Point
from app.models.road import Road
from app.schemas.map import MapData, MapPointData, MapRoadData
from sqlalchemy import select
from sqlalchemy.orm import Session


class MapSeeder:
    """Load the initial game map into the database."""

    def __init__(
        self,
        session: Session,
        map_path: Path,
    ):
        self.session = session
        self.map_path = map_path

    def seed(self) -> None:
        """Load the map into the database if it is not already present."""

        if self._map_exists():
            return

        data = self._load_map()

        self._seed_points(data.points)
        self._seed_roads(data.roads)

        self.session.commit()

    def _map_exists(self) -> bool:
        """Return whether map points already exist."""

        statement = select(Point.id).limit(1)

        return self.session.scalar(statement) is not None

    def _load_map(self) -> MapData:
        """Load and validate map data from JSON."""

        with self.map_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return MapData.model_validate(data)

    def _seed_points(
        self,
        points_data: list[MapPointData],
    ) -> None:
        """Create map points."""

        points = [
            Point(
                id=point.id,
                name=point.name,
                type=point.type,
                x=point.x,
                y=point.y,
            )
            for point in points_data
        ]

        self.session.add_all(points)

    def _seed_roads(
        self,
        roads_data: list[MapRoadData],
    ) -> None:
        """Create roads between map points."""

        roads = [
            Road(
                from_point_id=road.from_point_id,
                to_point_id=road.to_point_id,
                distance=road.distance,
                risk=road.risk,
                speed_modifier=road.speed_modifier,
            )
            for road in roads_data
        ]

        self.session.add_all(roads)