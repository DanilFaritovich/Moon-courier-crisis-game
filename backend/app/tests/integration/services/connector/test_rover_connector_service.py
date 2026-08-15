from app.models.point import Point, PointType
from app.models.rover import Rover, RoverStatus
from app.services.connector.rover_connector_service import RoverConnectorService


class TestRoverConnectorService:
    def test_create_rover(self, db_session, point, rover):
        """Persist a rover in the database."""

        db_session.add(point)
        db_session.commit()

        repository = RoverConnectorService(db_session)

        created = repository.create_rover(rover)

        assert created.id is not None
        assert created.name == "Rover A"
        assert created.cargo_capacity == 40
        assert created.status == RoverStatus.IDLE

    def test_get_rover(self, db_session, point, rover):
        """Return a rover by its identifier."""

        db_session.add_all([point, rover])
        db_session.commit()

        repository = RoverConnectorService(db_session)

        result = repository.get_rover(1)

        assert result is not None
        assert result.id == 1
        assert result.name == "Rover A"

    def test_get_available_rovers(self, db_session, point):
        """Return only idle rovers."""

        idle = Rover(
            id=1,
            name="Idle",
            cargo_capacity=30,
            battery=100,
            current_point_id=1,
            status=RoverStatus.IDLE,
        )

        delivering = Rover(
            id=2,
            name="Busy",
            cargo_capacity=30,
            battery=90,
            current_point_id=1,
            status=RoverStatus.DELIVERING,
        )

        db_session.add_all([point, idle, delivering])
        db_session.commit()

        repository = RoverConnectorService(db_session)

        rovers = repository.get_available_rovers()

        assert len(rovers) == 1
        assert rovers[0].name == "Idle"
        assert rovers[0].status == RoverStatus.IDLE

    def test_update_rover(self, db_session, point, rover):
        """Persist rover updates."""

        db_session.add_all([point, rover])
        db_session.commit()

        repository = RoverConnectorService(db_session)

        rover.battery = 55
        rover.status = RoverStatus.CHARGING

        repository.update_rover(rover)

        db_session.refresh(rover)

        assert rover.battery == 55
        assert rover.status == RoverStatus.CHARGING