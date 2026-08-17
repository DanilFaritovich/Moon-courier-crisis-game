from app.models.point import PointType
from pydantic import BaseModel


class MapPointData(BaseModel):
    id: int
    name: str
    type: PointType
    x: float
    y: float


class MapRoadData(BaseModel):
    from_point_id: int
    to_point_id: int
    distance: int
    risk: float
    speed_modifier: float


class MapData(BaseModel):
    points: list[MapPointData]
    roads: list[MapRoadData]