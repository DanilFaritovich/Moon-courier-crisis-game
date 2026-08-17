import networkx as nx
import pytest
from app.services.graph_service import GraphService


class TestGraphService:
    def test_build_graph(
        self,
        points,
        roads,
        graph_repository,
    ):
        """Build a graph with nodes and edges from points and roads."""

        graph_repository.get_points.return_value = points
        graph_repository.get_roads.return_value = roads

        service = GraphService(
            repository=graph_repository,
        )

        graph_state = service.build_graph()
        graph = graph_state.graph

        assert isinstance(graph, nx.Graph)
        assert graph.number_of_nodes() == 3
        assert graph.number_of_edges() == 2

        assert graph.nodes[1]["name"] == "Lunar Base"
        assert graph.nodes[1]["type"] == "base"
        assert graph.nodes[1]["x"] == 0
        assert graph.nodes[1]["y"] == 0

        assert graph.nodes[3]["name"] == "Delivery Point"
        assert graph.nodes[3]["type"] == "delivery"

        assert graph.edges[1, 2]["distance"] == 10.0
        assert graph.edges[1, 2]["risk"] == 0.1
        assert graph.edges[1, 2]["speed_modifier"] == 1.0

        assert graph.edges[2, 3]["distance"] == 15.0
        assert graph.edges[2, 3]["risk"] == 0.2
        assert graph.edges[2, 3]["speed_modifier"] == 0.8

    def test_build_empty_graph(
        self,
        graph_repository,
    ):
        """Build an empty graph when no points or roads are provided."""

        graph_repository.get_points.return_value = []
        graph_repository.get_roads.return_value = []

        service = GraphService(
            repository=graph_repository,
        )

        graph_state = service.build_graph()
        graph = graph_state.graph

        assert isinstance(graph, nx.Graph)
        assert graph.number_of_nodes() == 0
        assert graph.number_of_edges() == 0

    def test_build_graph_with_isolated_point(
        self,
        isolated_point,
        graph_repository,
    ):
        """Build a graph containing a point with no connected roads."""

        graph_repository.get_points.return_value = [isolated_point]
        graph_repository.get_roads.return_value = []

        service = GraphService(
            repository=graph_repository,
        )

        graph_state = service.build_graph()
        graph = graph_state.graph

        assert graph.number_of_nodes() == 1
        assert graph.number_of_edges() == 0
        assert isolated_point.id in graph.nodes

    def test_build_graph_stores_state(
        self,
        points,
        roads,
        graph_repository,
    ):
        """Store the built graph in the service state."""

        graph_repository.get_points.return_value = points
        graph_repository.get_roads.return_value = roads

        service = GraphService(
            repository=graph_repository,
        )

        graph_state = service.build_graph()

        assert service.graph_state is graph_state
        assert service.graph_state.graph is graph_state.graph

    def test_find_path(
        self,
        points,
        roads,
        graph_repository,
    ):
        """Find the shortest path between two points."""

        graph_repository.get_points.return_value = points
        graph_repository.get_roads.return_value = roads

        service = GraphService(
            repository=graph_repository,
        )
        service.build_graph()

        path = service.find_path(
            start_point_id=1,
            end_point_id=3,
        )

        assert path == [1, 2, 3]

    def test_find_path_uses_distance(
        self,
        points,
        roads,
        graph_repository,
    ):
        """Find the path with the lowest total distance."""

        graph_repository.get_points.return_value = points

        graph_repository.get_roads.return_value = [
            roads[0],
            roads[1],
            type(roads[0])(
                from_point_id=1,
                to_point_id=3,
                distance=40.0,
                risk=0.1,
                speed_modifier=1.0,
            ),
        ]

        service = GraphService(
            repository=graph_repository,
        )
        service.build_graph()

        path = service.find_path(
            start_point_id=1,
            end_point_id=3,
        )

        assert path == [1, 2, 3]

    def test_get_path_distance(
        self,
        points,
        roads,
        graph_repository,
    ):
        """Calculate the total distance of a path."""

        graph_repository.get_points.return_value = points
        graph_repository.get_roads.return_value = roads

        service = GraphService(
            repository=graph_repository,
        )
        service.build_graph()

        path = [1, 2, 3]

        distance = service.get_path_distance(path)

        assert distance == 25.0

    def test_get_path_risk(
        self,
        points,
        roads,
        graph_repository,
    ):
        """Calculate the total risk of a path."""

        graph_repository.get_points.return_value = points
        graph_repository.get_roads.return_value = roads

        service = GraphService(
            repository=graph_repository,
        )
        service.build_graph()

        path = [1, 2, 3]

        risk = service.get_path_risk(path)

        assert risk == pytest.approx(0.3)

    def test_find_path_without_built_graph(
        self,
        graph_repository,
    ):
        """Raise an error when finding a path before building the graph."""

        service = GraphService(
            repository=graph_repository,
        )

        with pytest.raises(
            RuntimeError,
            match="Graph has not been built.",
        ):
            service.find_path(
                start_point_id=1,
                end_point_id=2,
            )

    def test_get_path_distance_without_built_graph(
        self,
        graph_repository,
    ):
        """Raise an error when calculating distance before building the graph."""

        service = GraphService(
            repository=graph_repository,
        )

        with pytest.raises(
            RuntimeError,
            match="Graph has not been built.",
        ):
            service.get_path_distance([1, 2])

    def test_get_path_risk_without_built_graph(
        self,
        graph_repository,
    ):
        """Raise an error when calculating risk before building the graph."""

        service = GraphService(
            repository=graph_repository,
        )

        with pytest.raises(
            RuntimeError,
            match="Graph has not been built.",
        ):
            service.get_path_risk([1, 2])

    def test_find_path_between_disconnected_points(
        self,
        points,
        graph_repository,
    ):
        """Raise an error when no path exists between points."""

        graph_repository.get_points.return_value = points
        graph_repository.get_roads.return_value = []

        service = GraphService(
            repository=graph_repository,
        )
        service.build_graph()

        with pytest.raises(nx.NetworkXNoPath):
            service.find_path(
                start_point_id=1,
                end_point_id=3,
            )