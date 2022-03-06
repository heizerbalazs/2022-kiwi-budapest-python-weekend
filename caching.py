
import json
from typing import Optional, List
from redis import Redis
from slugify import slugify

import models

redis = Redis(host="redis.pythonweekend.skypicker.com", port=6379, db=0)


def create_key(surname, source, destination, dep_date):
    return f"{slugify(surname)}:journey:{slugify(source)}_{slugify(destination)}_{dep_date}"


def save_journeys(key: str, journeys: List[models.Journey], ttl: Optional[int] = 10) -> None:
    # journeys = [journey.dict() for journey in journeys]
    journeys = models.Journey.__config__.json_dumps(
        journeys, default=models.Journey.__json_encoder__)
    redis.set(key, journeys, ttl)


def get_journeys(key: str) -> Optional[dict]:
    maybe_value = redis.get(key)
    if maybe_value is None:
        return None
    try:
        return [models.Journey(**d) for d in json.loads(maybe_value)]
    except json.JSONDecodeError:
        print("The value comming from redis can't be converted to json...")
        return None
