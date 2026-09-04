from unittest.mock import MagicMock

from app.services.connector.unit_of_work_connector import SQLAlchemyUnitOfWork
from sqlalchemy.orm import Session


class TestSQLAlchemyUnitOfWork:
    def test_commit(self):
        db = MagicMock(spec=Session)
        unit_of_work = SQLAlchemyUnitOfWork(db)

        unit_of_work.commit()

        db.commit.assert_called_once_with()

    def test_rollback(self):
        db = MagicMock(spec=Session)
        unit_of_work = SQLAlchemyUnitOfWork(db)

        unit_of_work.rollback()

        db.rollback.assert_called_once_with()
