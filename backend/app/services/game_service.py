
from app.services.graph_service import GraphService


class GameService:
    """Manage game initialization."""

    def __init__(
        self,
        graph_service: GraphService,
    ):
        self.graph_service = graph_service

    def initialize_game(self):
        """Initialize the game world."""

        graph_state = self.graph_service.build_graph()

        return graph_state