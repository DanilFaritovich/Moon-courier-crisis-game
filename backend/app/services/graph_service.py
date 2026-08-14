import networkx as nx

from app.repositories.graph_connector_repository import GraphRepository


class GraphService:
    """Build and manipulate the game map graph."""

    def __init__(self, repository: GraphRepository):
        self.repository = repository

    def build_graph(self) -> nx.Graph:
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

        return graph