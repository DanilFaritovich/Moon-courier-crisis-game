import pytest
from app.models.point import Point
from app.models.road import Road
from app.services.connector.graph_connector_service import GraphConnector
from app.services.graph_service import GraphService, GraphState


@pytest.fixture
def repository(db_session) -> GraphConnector:
    return GraphConnector(db_session)


@pytest.fixture
def service(repository: GraphConnector) -> GraphService:
    return GraphService(repository)


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


@pytest.fixture
def built_graph(
    service: GraphService,
    db_points: list[Point],
    db_roads: list[Road],
) -> GraphState:
    return service.build_graph()


class TestGraphService:
    def test_build_graph(
        self,
        service: GraphService,
        db_points: list[Point],
        db_roads: list[Road],
    ):
        result = service.build_graph()

        assert isinstance(result, GraphState)
        assert result is service.graph_state

        graph = result.graph

        assert graph.number_of_nodes() == len(db_points)
        assert graph.number_of_edges() == len(db_roads)

        for point in db_points:
            assert point.id in graph
            assert graph.nodes[point.id]["name"] == point.name
            assert graph.nodes[point.id]["type"] == point.type.value
            assert graph.nodes[point.id]["x"] == point.x
            assert graph.nodes[point.id]["y"] == point.y

        for road in db_roads:
            edge = graph[road.from_point_id][road.to_point_id]

            assert edge["distance"] == road.distance
            assert edge["risk"] == road.risk
            assert edge["speed_modifier"] == road.speed_modifier

    def test_find_path(
        self,
        service: GraphService,
        built_graph: GraphState,
    ):
        start_point_id = 1
        end_point_id = 3

        result = service.find_path(
            start_point_id=start_point_id,
            end_point_id=end_point_id,
        )

        assert result == [1, 2, 3]

    def test_find_path_without_path(
        self,
        service: GraphService,
        built_graph: GraphState,
    ):
        start_point_id = 1
        end_point_id = 999

        result = service.find_path(
            start_point_id=start_point_id,
            end_point_id=end_point_id,
        )

        assert result == []

    def test_find_path_before_graph_is_built(
        self,
        service: GraphService,
    ):
        start_point_id = 1
        end_point_id = 3

        with pytest.raises(
            RuntimeError,
            match="Graph has not been built.",
        ):
            service.find_path(
                start_point_id=start_point_id,
                end_point_id=end_point_id,
            )

    def test_get_path_distance(
        self,
        service: GraphService,
        built_graph: GraphState,
    ):
        path = [1, 2, 3]

        result = service.get_path_distance(path)

        assert result == 30

    def test_get_path_distance_without_path(
        self,
        service: GraphService,
        built_graph: GraphState,
    ):
        path = [1, 999]

        result = service.get_path_distance(path)

        assert result == 0

    def test_get_path_risk(
        self,
        service: GraphService,
        built_graph: GraphState,
    ):
        path = [1, 2, 3]

        result = service.get_path_risk(path)

        assert result == pytest.approx(0.3)

    def test_get_base(
        self,
        service: GraphService,
        base_point: Point,
        db_session,
    ):
        db_session.add(base_point)
        db_session.flush()

        result = service.get_base()

        assert result is base_point

    def test_get_distance_to_base(
        self,
        service: GraphService,
        built_graph: GraphState,
    ):
        point_id = 3

        result = service.get_distance_to_base(point_id)

        assert result == 30

    def test_get_unbase(
        self,
        service: GraphService,
        db_points: list[Point],
    ):
        result = service.get_unbase()

        assert result == db_points[1:]

    def test_get_graph_before_build(
        self,
        service: GraphService,
    ):
        with pytest.raises(
            RuntimeError,
            match="Graph has not been built.",
        ):
            service._get_graph()
