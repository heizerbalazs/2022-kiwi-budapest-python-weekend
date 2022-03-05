import argparse
from datetime import datetime
import json
import requests

from caching import create_key, retrieve_dict, store_dict
import database
LOCATIONS_URL = 'https://brn-ybus-pubapi.sa.cz/restapi/consts/locations'


def parse_args():
    parser = argparse.ArgumentParser(description='Regiojet')
    parser.add_argument('source', type=str)
    parser.add_argument('destination', type=str)
    parser.add_argument('departure', type=str)
    parser.add_argument('currency', type=str,  nargs='?', default='EUR')

    args = parser.parse_args()
    return args.source, args.destination, args.departure, args.currency


def get_locations():
    return requests.get(LOCATIONS_URL).json()


def create_ids_by_location(locations):
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


def parse_response(response):
    paths = list()
    for route in response['routes']:
        path = dict()
        path['departure_datetime'] = route['departureTime']
        path['arrival_datetime'] = route['arrivalTime']
        path['fare'] = dict()
        path['fare']['amount'] = route['priceFrom']
        path['type'] = route['vehicleTypes'][0]
        path['source_id'] = route['departureStationId']
        path['destination_id'] = route['arrivalStationId']
        path['free_seats'] = route['freeSeatsCount']
        path['carrier'] = 'REGIOJET'
        paths.append(path)

    return paths


def enrich_paths(paths, *args, **kwargs):
    currency = kwargs.pop('currency')
    for path in paths:
        path['fare']['currency'] = currency
        path.update(kwargs)


def search_paths(source, destination, departure, currency):
    locations = get_locations()
    ids_by_location = create_ids_by_location(locations)

    source_id = ids_by_location[source]
    destination_id = ids_by_location[destination]
    departure = departure

    header = add_currency_to_header(currency)
    url = create_path_search_url(source_id, destination_id, departure)

    response = send_path_search_request(url, header)
    paths = parse_response(response)
    enrich_paths(paths, source=source,
                 destination=destination, currency=currency)
    return paths


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


if __name__ == '__main__':
    start = datetime.now()
    source, destination, departure, currency = parse_args()

    key = create_key('heizer', source, destination, departure)
    print("Try Cache")
    paths = retrieve_dict(key)

    if paths is None:
        print("Try DB")
        journeys = database.get_all_journeys()

    if paths is None:
        print("Scrape Web, and save to Cahche and DB")
        paths = search_paths(source, destination, departure, currency)
        store_dict(key, paths)
        journeys = paths_to_journeys(paths)
        database.save_journeys(journeys)

    journeys = database.get_all_journeys()
    for journey in journeys:
        print(
            "found jorney: "
            f"{journey.source} - {journey.destination}"
        )

    # Look for path
    # if its in redis use it
    # elif its in db use that
    # else scrape the web and store the results both iin redis and the db
    # end = datetime.now()
    # # print(json.dumps(paths, indent=4))
    # print(end-start)
    # print(type(paths[0]['departure_datetime']))
