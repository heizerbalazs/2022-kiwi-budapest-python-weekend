import random
from datetime import datetime
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


import data_acqusition
import caching
import database
import models

app = FastAPI()
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/whisper')
def whisper(text: str):
    return [f"{text} {i}" for i in range(random.randint(0, 10))]


@app.get('/locations')
def locations():
    result = data_acqusition.get_location_ids_by_locations()
    return JSONResponse(result)


@app.get('/search')
def search(origin: str, destination: str, departure: str, currency: Optional[str] = "EUR"):
    departure_datetime = datetime.fromisoformat(departure)
    departure = departure_datetime.strftime('%Y-%m-%d')
    key = caching.create_key(
        'heizer', origin, destination, departure)
    journeys = caching.get_journeys(key)

    if journeys is not None:
        journeys = list(filter(lambda journey: (journey.source == origin) and (
            journey.destination == destination) and (journey.departure >= departure_datetime), journeys))
        journeys = journeys if len(journeys) > 0 else None
    else:
        journeys = database.get_journyes(
            origin, destination, departure_datetime)
        caching.save_journeys(key, journeys)

    if journeys is None:
        journeys = data_acqusition.search_paths(
            origin, destination, departure, currency)
        caching.save_journeys(key, journeys)

        database.save_journeys(
            [database.Journey(**journey.dict()) for journey in journeys])

    return [models.to_frontend(journey) for journey in journeys]
