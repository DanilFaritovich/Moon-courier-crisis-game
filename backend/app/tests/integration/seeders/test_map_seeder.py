import json
from pathlib import Path

import pytest
from app.models.point import Point
from app.models.road import Road
from app.seeders.map_seeder import MapSeeder
from pydantic import ValidationError
from sqlalchemy import select

MAP_PATH = Path("data/map.json")


class TestMapSeeder:
    def test_seed_map(
        self,
        db_session,
    ):
        """Load points and roads from the map file into the database."""

        seeder = MapSeeder(
            session=db_session,
            map_path=MAP_PATH,
        )

        seeder.seed()

        points = db_session.scalars(
            select(Point).order_by(Point.id),
        ).all()

        roads = db_session.scalars(
            select(Road).order_by(Road.id),
        ).all()

        assert len(points) == 4
        assert len(roads) == 4

        assert points[0].id == 1
        assert points[0].name == "Lunar Base"
        assert points[0].x == 0
        assert points[0].y == 0

        assert points[1].id == 2
        assert points[1].name == "Crater Alpha"
        assert points[1].x == 10
        assert points[1].y == 5

        assert points[2].id == 3
        assert points[2].name == "Crater Beta"
        assert points[2].x == -8
        assert points[2].y == 12

        assert roads[0].from_point_id == 1
        assert roads[0].to_point_id == 2
        assert roads[0].distance == 11.18
        assert roads[0].risk == 0.2
        assert roads[0].speed_modifier == 1.0

        assert roads[1].from_point_id == 1
        assert roads[1].to_point_id == 3
        assert roads[1].distance == 14.42
        assert roads[1].risk == 0.4
        assert roads[1].speed_modifier == 0.8

        assert roads[2].from_point_id == 2
        assert roads[2].to_point_id == 3
        assert roads[2].distance == 13.6
        assert roads[2].risk == 0.7
        assert roads[2].speed_modifier == 0.6

    def test_seed_does_not_create_duplicates(
        self,
        db_session,
    ):
        """Do not create duplicate map data on repeated seeding."""

        seeder = MapSeeder(
            session=db_session,
            map_path=MAP_PATH,
        )

        seeder.seed()
        seeder.seed()

        points = db_session.scalars(
            select(Point),
        ).all()

        roads = db_session.scalars(
            select(Road),
        ).all()

        assert len(points) == 4
        assert len(roads) == 4

    def test_seed_invalid_map(
        self,
        db_session,
        tmp_path,
    ):
        """Raise a validation error when map data is invalid."""

        map_path = tmp_path / "invalid_map.json"

        map_path.write_text(
            json.dumps(
                {
                    "points": [],
                    "roads": "invalid",
                }
            ),
            encoding="utf-8",
        )

        seeder = MapSeeder(
            session=db_session,
            map_path=map_path,
        )

        with pytest.raises(ValidationError):
            seeder.seed()