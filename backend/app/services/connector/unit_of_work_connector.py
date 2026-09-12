import logging

from app.repositories.unit_of_work import UnitOfWork
from sqlalchemy.orm import Session


class SQLAlchemyUnitOfWork(UnitOfWork):
    """Manage SQLAlchemy transactions."""

    def __init__(self, db: Session, logger: logging.Logger | None = None):
        self.db = db
        self.logger = logger if logger is not None else logging.getLogger(__name__)

    def commit(self) -> None:
        self.db.commit()
        self.logger.debug("Committed database transaction")

    def rollback(self) -> None:
        self.db.rollback()
        self.logger.warning("Rolled back database transaction")
