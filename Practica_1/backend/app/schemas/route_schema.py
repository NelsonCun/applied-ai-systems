from pydantic import BaseModel, Field


class RouteRequest(BaseModel):
    origin: str
    destination: str


class CityRequest(BaseModel):
    name: str


class ConnectionRequest(BaseModel):
    origin: str
    destination: str
    distance: int = Field(gt=0)