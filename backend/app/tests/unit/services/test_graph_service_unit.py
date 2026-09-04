from unittest.mock import Mock

import networkx as nx
import pytest
from app.models.point import Point, PointType
from app.models.road import Road
from app.repositories.graph_connector_repository import GraphRepository
from app.services.graph_service import GraphService, GraphState


@pytest.fixture
def repository() -> Mock:
    return Mock(spec=GraphRepository)


@pytest.fixture
def service(repository: Mock) -> GraphService:
    return GraphService(repository)


@pytest.fixture
def initialized_service(
    service: GraphService,
    graph: nx.Graph,
) -> GraphService:
    service.graph_state = GraphState(graph=graph)
    return service


class TestGraphServiceUnit:
    def test_build_graph(
        self,
        service: GraphService,
        repository: Mock,
        points: list[Point],
        roads: list[Road],
    ) -> None:
        repository.get_points.return_value = points
        repository.get_roads.return_value = roads

        result = service.build_graph()

        assert isinstance(result, GraphState)
        assert result is service.graph_state
        assert isinstance(result.graph, nx.Graph)

        assert result.graph.number_of_nodes() == len(points)
        assert result.graph.number_of_edges() == len(roads)

        for point in points:
            assert result.graph.nodes[point.id] == {
                "name": point.name,
                "type": point.type.value,
                "x": point.x,
                "y": point.y,
            }

        for road in roads:
            edge = result.graph[road.from_point_id][road.to_point_id]

            assert edge["distance"] == road.distance
            assert edge["risk"] == road.risk
            assert edge["speed_modifier"] == road.speed_modifier

        repository.get_points.assert_called_once_with()
        repository.get_roads.assert_called_once_with()

    def test_find_path(
        self,
        initialized_service: GraphService,
    ) -> None:
        start_point_id = 1
        end_point_id = 3

        result = initialized_service.find_path(
            start_point_id,
            end_point_id,
        )

        assert result == [
            start_point_id,
            2,
            end_point_id,
        ]

    def test_find_path_returns_shortest_path(
        self,
        service: GraphService,
    ) -> None:
        start_point_id = 1
        end_point_id = 4

        short_distance = 10
        long_distance = 50

        graph = nx.Graph()

        graph.add_edge(
            start_point_id,
            2,
            distance=short_distance,
        )
        graph.add_edge(
            2,
            end_point_id,
            distance=short_distance,
        )

        graph.add_edge(
            start_point_id,
            3,
            distance=long_distance,
        )
        graph.add_edge(
            3,
            end_point_id,
            distance=long_distance,
        )

        service.graph_state = GraphState(graph=graph)

        result = service.find_path(
            start_point_id,
            end_point_id,
        )

        assert result == [
            start_point_id,
            2,
            end_point_id,
        ]

    def test_find_path_returns_empty_list_when_no_path(
        self,
        service: GraphService,
    ) -> None:
        start_point_id = 1
        end_point_id = 3

        graph = nx.Graph()
        graph.add_node(start_point_id)
        graph.add_node(end_point_id)

        service.graph_state = GraphState(graph=graph)

        result = service.find_path(
            start_point_id,
            end_point_id,
        )

        assert result == []

    def test_get_path_distance(
        self,
        initialized_service: GraphService,
    ) -> None:
        path = [1, 2, 3]

        first_distance = 10
        second_distance = 20
        expected_distance = first_distance + second_distance

        result = initialized_service.get_path_distance(path)

        assert result == expected_distance

    def test_get_path_distance_returns_zero_when_no_path(
        self,
        service: GraphService,
    ) -> None:
        path = [1, 2, 3]

        graph = nx.Graph()
        graph.add_node(1)
        graph.add_node(2)
        graph.add_node(3)

        service.graph_state = GraphState(graph=graph)

        result = service.get_path_distance(path)

        assert result == 0

    def test_get_path_risk(
        self,
        initialized_service: GraphService,
    ) -> None:
        path = [1, 2, 3]

        first_risk = 0.1
        second_risk = 0.2
        expected_risk = first_risk + second_risk

        result = initialized_service.get_path_risk(path)

        assert result == expected_risk

    def test_get_base(
        self,
        service: GraphService,
        repository: Mock,
        base_point: Point,
    ) -> None:

        repository.get_base.return_value = base_point

        result = service.get_base()

        assert result is base_point
        repository.get_base.assert_called_once_with()

    def test_get_distance_to_base(
        self,
        service: GraphService,
        repository: Mock,
    ) -> None:
        point_id = 5
        base_id = 1
        path = [point_id, 3, base_id]

        expected_distance = 100

        base = Point(
            id=base_id,
            name="Base",
            type=PointType.BASE,
            x=0,
            y=0,
        )

        repository.get_base.return_value = base

        service.find_path = Mock(return_value=path)
        service.get_path_distance = Mock(
            return_value=expected_distance,
        )

        result = service.get_distance_to_base(point_id)

        assert result == expected_distance

        service.find_path.assert_called_once_with(
            point_id,
            base_id,
        )
        service.get_path_distance.assert_called_once_with(path)

    def test_get_unbase(
        self,
        service: GraphService,
        repository: Mock,
        points: list[Point],
    ) -> None:
        repository.get_unbase.return_value = points

        result = service.get_unbase()

        assert result == points
        repository.get_unbase.assert_called_once_with()

    def test_find_path_raises_when_graph_not_built(
        self,
        service: GraphService,
    ) -> None:
        start_point_id = 1
        end_point_id = 2

        with pytest.raises(
            RuntimeError,
            match="Graph has not been built.",
        ):
            service.find_path(
                start_point_id,
                end_point_id,
            )

    def test_get_path_distance_raises_when_graph_not_built(
        self,
        service: GraphService,
    ) -> None:
        path = [1, 2]

        with pytest.raises(
            RuntimeError,
            match="Graph has not been built.",
        ):
            service.get_path_distance(path)

    def test_get_path_risk_raises_when_graph_not_built(
        self,
        service: GraphService,
    ) -> None:
        path = [1, 2]

        with pytest.raises(
            RuntimeError,
            match="Graph has not been built.",
        ):
            service.get_path_risk(path)
