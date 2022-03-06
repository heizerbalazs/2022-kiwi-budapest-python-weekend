from datetime import datetime
import requests

import database
from models import Journey
LOCATIONS_URL = 'https://brn-ybus-pubapi.sa.cz/restapi/consts/locations'


def get_location_ids_by_locations():
    locations = requests.get(LOCATIONS_URL).json()

    ids_by_location = dict()
    for country in locations:
        for city in country['cities']:
            ids_by_location[city['name']] = city['id']

    return ids_by_location


def create_path_search_url(source_id: int, destination_id: int, departure: str):
    url = (f"https://brn-ybus-pubapi.sa.cz/restapi/routes/search/simple?"
           f"tariffs=REGULAR&"
           f"toLocationType=CITY&"
           f"toLocationId={source_id}&"
           f"fromLocationType=CITY&"
           f"fromLocationId={destination_id}&"
           f"departureDate={departure}")

    return url


def add_currency_to_header(currency):
    return {'X-Currency': currency}


def send_path_search_request(url, header):
    return requests.get(url).json()


def search_paths(source, destination, departure, currency):
    location_ids_by_location = get_location_ids_by_locations()

    source_id = location_ids_by_location[source]
    destination_id = location_ids_by_location[destination]
    departure = departure

    header = add_currency_to_header(currency)
    url = create_path_search_url(source_id, destination_id, departure)

    response = send_path_search_request(url, header)
    journeys = list()
    for route in response['routes']:
        journey = Journey(
            departure_datetime=route['departureTime'],
            arrival_datetime=route['arrivalTime'],
            price=route['priceFrom'],
            currency=currency,
            vehicle_type=route['vehicleTypes'][0],
            source_id=route['departureStationId'],
            source=source,
            destination_id=route['arrivalStationId'],
            destination=destination,
            free_seats=route['freeSeatsCount'],
            carrier='REGIOJET',
        )
        journeys.append(journey)
    return journeys


def paths_to_journeys(paths):
    journeys = list()
    for path in paths:
        journey = database.Journey(
            source=path['source'],
            destination=path['destination'],
            departure_datetime=datetime.strptime(
                path['departure_datetime'], "%Y-%m-%dT%H:%M:%S.%f%z"),
            arrival_datetime=datetime.strptime(
                path['arrival_datetime'], "%Y-%m-%dT%H:%M:%S.%f%z"),
            carrier=path['carrier'],
            vehicle_type=path['type'],
            price=path['fare']['amount'],
            currency=path['fare']['currency']
        )
        journeys.append(journey)
    return journeys
