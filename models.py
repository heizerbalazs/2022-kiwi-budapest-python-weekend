from datetime import datetime
from pydantic import BaseModel


class Journey(BaseModel):
    departure_datetime: datetime
    arrival_datetime: datetime
    price: float
    currency: str
    vehicle_type: str
    source_id: int
    source: str
    destination_id: int
    destination: str
    free_seats: int
    carrier: str

    class Config:
        orm_mode = True


class Location(BaseModel):
    id: int
    name: str
