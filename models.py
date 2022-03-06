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


def to_frontend(journey: Journey):
    d = {
        "departure": journey.departure_datetime,
        "arrival": journey.arrival_datetime,
        "origin": journey.source,
        "destination": journey.destination,
        "fare": {
            "amount": journey.price,
            "currency": journey.currency  # you can use https://api.skypicker.com/rates
        },
        "type": journey.vehicle_type,  # optional (bus/train)
        "source_id": journey.source_id,  # optional (carrier’s id)
        "destination_id": journey.destination_id,  # optional (carrier’s id)
        "free_seats": journey.free_seats,  # optional
        "carrier": journey.carrier,
    }

    return d


class Location(BaseModel):
    id: int
    name: str
