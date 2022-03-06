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

    key = caching.create_key('heizer', source, destination, departure)
    print("Try Cache")
    journeys = caching.get_journeys(key)

    if journeys is None:
        print("Try DB")
        journeys = database.get_all_journeys()
        caching.save_journeys(key, journeys)

    if journeys is None:
        print("Scrape Web, and save to Cahche and DB")
        journeys = data_acqusition.search_paths(
            source, destination, departure, currency)
        caching.save_journeys(key, journeys)

        journeys = [database.Journey(**journey.dict()) for journey in journeys]
        database.save_journeys(journeys)

    # journeys = database.get_all_journeys()
    for journey in journeys:
        print(
            "found jorney: "
            f"{journey.source} - {journey.destination}"
        )
