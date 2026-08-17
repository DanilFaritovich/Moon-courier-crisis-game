import networkx as nx


class TestGraphService:
    def test_build_graph(
        self,
        graph_service,
    ):
        """Build a graph from the seeded map."""

        graph_state = graph_service.build_graph()
        graph = graph_state.graph

        assert isinstance(graph, nx.Graph)
        assert graph.number_of_nodes() == 4
        assert graph.number_of_edges() == 4

        assert graph.nodes[1]["name"] == "Lunar Base"
        assert graph.nodes[1]["type"] == "base"

        assert graph.nodes[2]["name"] == "Crater Alpha"
        assert graph.nodes[2]["type"] == "delivery"

        assert graph.nodes[3]["name"] == "Crater Beta"
        assert graph.nodes[3]["type"] == "delivery"

    def test_find_path(
        self,
        graph_service,
    ):
        """Find the shortest path on the seeded map."""

        graph_service.build_graph()

        path = graph_service.find_path(
            start_point_id=4,
            end_point_id=1,
        )

        assert path == [4, 3, 1]

    def test_get_path_distance(
        self,
        graph_service,
    ):
        """Calculate the distance of a path."""

        graph_service.build_graph()

        distance = graph_service.get_path_distance(
            [1, 2, 3],
        )

        assert distance == 24

    def test_get_path_risk(
        self,
        graph_service,
    ):
        """Calculate the risk of a path."""

        graph_service.build_graph()

        risk = graph_service.get_path_risk(
            [1, 2, 3],
        )

        assert round(risk, 2) == 0.9