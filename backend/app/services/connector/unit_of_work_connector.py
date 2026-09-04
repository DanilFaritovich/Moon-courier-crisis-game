from app.repositories.unit_of_work import UnitOfWork
from sqlalchemy.orm import Session


class SQLAlchemyUnitOfWork(UnitOfWork):
    """Manage SQLAlchemy transactions."""

    def __init__(self, db: Session):
        self.db = db

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
