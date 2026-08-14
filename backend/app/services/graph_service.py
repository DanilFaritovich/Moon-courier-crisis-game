import networkx as nx

from app.models.point import Point
from app.models.road import Road


class GraphService:
    """Build and manipulate the game map graph."""

    @staticmethod
    def build_graph(
        points: list[Point],
        roads: list[Road],
    ) -> nx.Graph:
        """Build a NetworkX graph from map points and roads."""

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