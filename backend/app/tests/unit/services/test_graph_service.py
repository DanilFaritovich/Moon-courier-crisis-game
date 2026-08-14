import networkx as nx

from app.models.point import Point
from app.services.graph_service import GraphService


class TestGraphService:
    def test_build_graph(self, points, roads):
        """Build a graph with nodes and edges from points and roads."""

        graph = GraphService.build_graph(points, roads)

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

    def test_build_empty_graph(self):
        """Build an empty graph when no points or roads are provided."""

        graph = GraphService.build_graph(
            points=[],
            roads=[],
        )

        assert isinstance(graph, nx.Graph)
        assert graph.number_of_nodes() == 0
        assert graph.number_of_edges() == 0

    def test_build_graph_with_isolated_point(self, isolated_point):
        """Build a graph containing a point with no connected roads."""

        graph = GraphService.build_graph(
            points=[isolated_point],
            roads=[],
        )

        assert graph.number_of_nodes() == 1
        assert graph.number_of_edges() == 0
        assert isolated_point.id in graph.nodes