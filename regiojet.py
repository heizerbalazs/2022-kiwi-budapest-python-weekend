import argparse
from datetime import datetime
import json
import requests

import caching
import database
import models
import data_acqusition


def parse_args():
    parser = argparse.ArgumentParser(description='Regiojet')
    parser.add_argument('source', type=str)
    parser.add_argument('destination', type=str)
    parser.add_argument('departure', type=str)
    parser.add_argument('currency', type=str,  nargs='?', default='EUR')

    args = parser.parse_args()
    return args.source, args.destination, args.departure, args.currency


if __name__ == '__main__':
    start = datetime.now()
    source, destination, departure, currency = parse_args()

    departure_datetime = datetime.strptime(departure, '%Y-%m-%d')

    key = caching.create_key('heizer', source, destination, departure)
    print("Try Cache")
    key = caching.create_key(
        'heizer', source, destination, departure)
    journeys = caching.get_journeys(key)

    if journeys is not None:
        journeys = list(filter(lambda journey: (journey.source == source) and (
            journey.destination == destination) and (journey.departure >= departure_datetime), journeys))
        journeys = journeys if len(journeys) > 0 else None
    else:
        journeys = database.get_journyes(
            source, destination, departure_datetime)
        caching.save_journeys(key, journeys)

    if journeys is None:
        journeys = data_acqusition.search_paths(
            source, destination, departure, currency)
        caching.save_journeys(key, journeys)

        # journeys = [database.Journey(**journey.dict()) for journey in journeys]
        database.save_journeys(
            [database.Journey(**journey.dict()) for journey in journeys])

    for journey in journeys:
        print(
            "found jorney: "
            f"{journey.source} - {journey.destination}"
        )
