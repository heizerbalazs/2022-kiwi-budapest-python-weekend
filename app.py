from typing import Optional
from fastapi import FastAPI
from fastapi.responses import JSONResponse

import data_acqusition

app = FastAPI()


@app.get('/locations')
def locations():
    result = regiojet.get_location_ids_by_locations()
    return JSONResponse(result)


@app.get('/search')
def search(source: str, destination: str, departure_date: str, currency: Optional[str] = "EUR"):
    result = data_acqusition.search_paths(
        source, destination, departure_date, currency)
    return result
