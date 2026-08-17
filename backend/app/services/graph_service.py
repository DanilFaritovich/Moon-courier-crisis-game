from dataclasses import dataclass

import networkx as nx
from app.repositories.graph_connector_repository import GraphRepository


@dataclass
class GraphState:
    """Runtime state of the game map graph."""

    graph: nx.Graph


class GraphService:
    """Build and manipulate the game map graph."""

    def __init__(self, repository: GraphRepository):
        self.repository = repository
        self.graph_state: GraphState | None = None

    def build_graph(self) -> GraphState:
        """Build a NetworkX graph from map points and roads."""

        points = self.repository.get_points()
        roads = self.repository.get_roads()

        graph = nx.Graph()

        for point in points:
            graph.add_node(
                point.id,
                name=point.name,
                type=point.type.value,
                x=point.x,
                y=point.y,
            )

        for road in roads:
            graph.add_edge(
                road.from_point_id,
                road.to_point_id,
                distance=road.distance,
                risk=road.risk,
                speed_modifier=road.speed_modifier,
            )

        self.graph_state = GraphState(graph=graph)

        return self.graph_state

    def find_path(
        self,
        start_point_id: int,
        end_point_id: int,
    ) -> list[int]:
        """Find the shortest path between two points."""

        graph = self._get_graph()

        return nx.shortest_path(
            graph,
            source=start_point_id,
            target=end_point_id,
            weight="distance",
        )

    def get_path_distance(
        self,
        path: list[int],
    ) -> float:
        """Calculate the total distance of a path."""

        graph = self._get_graph()

        return nx.path_weight(
            graph,
            path,
            weight="distance",
        )

    def get_path_risk(
        self,
        path: list[int],
    ) -> float:
        """Calculate the total risk of a path."""

        graph = self._get_graph()

        return sum(
            graph[u][v]["risk"]
            for u, v in zip(path, path[1:], strict=False)
        )

    def _get_graph(self) -> nx.Graph:
        """Return the current graph or raise if it has not been built."""

        if self.graph_state is None:
            raise RuntimeError("Graph has not been built.")

        return self.graph_state.graph