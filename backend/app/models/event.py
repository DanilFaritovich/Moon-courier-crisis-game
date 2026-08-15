from datetime import datetime, timezone
from enum import Enum

from app.db.base import Base
from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column


class EventType(str, Enum):
    """Type of a game event."""

    SOLAR_STORM = "solar_storm"
    METEOR_SHOWER = "meteor_shower"
    DUST_STORM = "dust_storm"
    ROVER_MALFUNCTION = "rover_malfunction"


class Event(Base):
    """Random event affecting the game world."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)

    event_type: Mapped[EventType] = mapped_column(
        SqlEnum(EventType),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )