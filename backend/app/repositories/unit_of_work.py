from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    """Manage a transaction."""

    @abstractmethod
    def commit(self) -> None:
        """Commit the current transaction."""
        ...

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the current transaction."""
        ...
