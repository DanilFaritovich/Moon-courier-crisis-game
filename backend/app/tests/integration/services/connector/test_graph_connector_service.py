import pytest
from app.models.point import Point, PointType
from app.models.road import Road
from app.services.connector.graph_connector_service import GraphConnector
from sqlalchemy.exc import NoResultFound


@pytest.fixture
def repository(
    db_session,
) -> GraphConnector:
    return GraphConnector(db_session)


@pytest.fixture
def db_points(
    db_session,
    points: list[Point],
) -> list[Point]:
    db_session.add_all(points)
    db_session.flush()

    return points


@pytest.fixture
def db_roads(
    db_session,
    roads: list[Road],
    db_points: list[Point],
) -> list[Road]:
    db_session.add_all(roads)
    db_session.flush()

    return roads


class TestGraphConnector:
    def test_get_points(
        self,
        repository: GraphConnector,
        db_points: list[Point],
    ):
        result = repository.get_points()

        assert result == db_points

    def test_get_point_by_id(
        self,
        repository: GraphConnector,
        db_points: list[Point],
    ):
        point_id = 2

        result = repository.get_point_by_id(point_id)

        assert result is db_points[1]

    def test_get_point_by_id_not_found(
        self,
        repository: GraphConnector,
        db_points: list[Point],
    ):
        point_id = 999

        with pytest.raises(NoResultFound):
            repository.get_point_by_id(point_id)

    def test_get_base(
        self,
        repository: GraphConnector,
        db_points: list[Point],
    ):
        result = repository.get_base()

        assert result is db_points[0]
        assert result.type == PointType.BASE

    def test_get_unbase(
        self,
        repository: GraphConnector,
        db_points: list[Point],
    ):
        result = repository.get_unbase()

        assert result == db_points[1:]
        assert all(point.type != PointType.BASE for point in result)

    def test_get_roads(
        self,
        repository: GraphConnector,
        db_roads: list[Road],
    ):
        result = repository.get_roads()

        assert result == db_roads
