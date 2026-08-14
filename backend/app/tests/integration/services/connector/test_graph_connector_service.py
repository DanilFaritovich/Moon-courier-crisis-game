from app.models.point import Point, PointType
from app.models.road import Road
from app.services.connector.graph_connector_service import GraphConnector


class TestGraphService:
    def test_get_map(self, db_session):
        """Return points and roads stored in the database."""

        point_1 = Point(
            id=1,
            name="Lunar Base",
            type=PointType.BASE,
            x=0,
            y=0,
        )

        point_2 = Point(
            id=2,
            name="Delivery Point",
            type=PointType.DELIVERY,
            x=100,
            y=100,
        )

        road = Road(
            id=1,
            from_point_id=1,
            to_point_id=2,
            distance=10.0,
            risk=0.2,
            speed_modifier=1.0,
        )

        db_session.add_all([
            point_1,
            point_2,
            road,
        ])
        db_session.commit()

        service = GraphConnector(db_session)

        points, roads = service.get_points(), service.get_roads()

        assert len(points) == 2
        assert len(roads) == 1

        assert points[0].name == "Lunar Base"
        assert points[1].name == "Delivery Point"

        assert roads[0].from_point_id == 1
        assert roads[0].to_point_id == 2
        assert roads[0].distance == 10.0